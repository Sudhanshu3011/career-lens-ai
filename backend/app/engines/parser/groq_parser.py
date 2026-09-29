"""
CareerLens AI - Universal Structured LLM Resume Parser
Uses LangChain ChatGroq with structured Pydantic output and LangSmith tracing.
Parses any resume across any industry (Medical, Legal, Finance, Tech, Sales) into 6 canonical sections.
"""

from __future__ import annotations

import json
from typing import Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.core.config import settings
from app.core.logger import get_logger
from app.core.rate_limiter import groq_rate_limiter
from app.engines.parser.pdf_extractor import extract_text_and_links_from_pdf
from app.models.domain.resume_sections import (
    EducationItem,
    ProjectItem,
    ResumeParsedSections,
    WorkExperienceItem,
)

logger = get_logger(__name__)

RESUME_EXTRACTION_SYSTEM_PROMPT = """
You are a World-Class Executive Resume Parser and Talent Data Architect.
Your task is to parse raw text extracted from an applicant's resume into comprehensive, standardized, canonical sections.

CRITICAL INSTRUCTIONS:
1. UNIVERSAL DOMAIN AGNOSTICISM:
   - Handle applicants from ANY industry: Healthcare/Nursing, Finance, Law, Technology, Sales, Engineering, Education, Operations, etc.
   - Do NOT force software engineering concepts onto non-technical candidates.
2. ACCURATE SECTION PARSING:
   - `candidate_name`: The full legal or professional name of the applicant.
   - `contact_identity`: email, phone, location, and professional portfolio / bar / registry links.
   - `professional_summary`: Career objective, headline, or executive summary.
   - `work_experience`: Chronological employment history. For each role, extract employer, title, dates, whether current, responsibilities & achievements (quantified outcomes), and tools/methods used.
   - `projects`: Key projects, technical initiatives, research, systems architecture, publications, or client deliverables. Extract project title, overview/description, technologies/tools used, key responsibilities & quantified outcomes, and links if mentioned.
   - `core_competencies`: Complete list of domain skills, clinical skills, legal disciplines, financial frameworks, or software competencies.
   - `education`: Degrees, institutions, majors/fields of study, graduation year.
   - `certifications_and_licenses`: State board licenses (RN, MD, Bar, CPA, PE), specialized certifications (BLS, ACLS, AWS, PMP), or notable credentials.
3. PRESERVE FACTUAL INTEGRITY:
   - Do NOT invent or extrapolate facts not present in the resume text.
   - If a field is not present in the document, leave it empty or None.
"""


def validate_parsed_sections(sections: ResumeParsedSections, raw_text: str) -> tuple[bool, str]:
    """
    Validates that the parsed resume is complete, accurate, and was not disrupted.
    Returns (is_complete, failure_reason).
    """
    if not sections:
        return False, "No parsed data produced"

    name = (sections.candidate_name or "").strip()
    if not name or len(name) < 2:
        return False, "Candidate name is missing or blank"

    # Reject phone numbers or artifact strings masquerading as candidate names
    import re
    if re.match(r"^[\+\d\s\-\(\)\.\#]+$", name) or name.startswith("+"):
        return False, f"Invalid candidate name '{name}' (contact phone number detected as name)"

    if "@" in name:
        return False, f"Invalid candidate name '{name}' (email detected as name)"

    if name.lower() in ["candidate profile", "resume", "curriculum vitae", "unknown", "untitled"]:
        return False, f"Placeholder candidate name '{name}' detected"

    # If raw text contains substantive content (> 200 characters), verify at least one core domain entity was captured
    if len(raw_text.strip()) > 200:
        has_experience = len(sections.work_experience) > 0
        has_projects = len(sections.projects) > 0
        has_competencies = len(sections.core_competencies) > 0

        # Disrupted condition: document has substantial text but LLM failed to capture any experience, projects, or competencies
        if not has_experience and not has_projects and not has_competencies:
            return False, "Zero work experiences, projects, or core competencies were extracted from the document"

    return True, "Complete"


class UniversalResumeParser:
    """Universal structured resume parser leveraging ChatGroq and LangSmith."""

    def __init__(self, model_name: str | None = None) -> None:
        configured = model_name or settings.GROQ_MODEL
        # Use optimal 120B parameter model with generous token quotas
        if "qwen" in configured.lower() or "llama" in configured.lower():
            configured = "openai/gpt-oss-120b"
        self.model_name = configured
        self._llm = None


    def _get_llm(self) -> ChatGroq:
        if self._llm is None:
            if not settings.GROQ_API_KEY:
                raise ValueError(
                    "GROQ_API_KEY is not configured in environment or settings. "
                    "Cannot initialize ChatGroq for structured resume parsing."
                )
            self._llm = ChatGroq(
                model=self.model_name,
                temperature=0.0,
                api_key=settings.GROQ_API_KEY,
                max_retries=2,
                request_timeout=40.0,
            )
        return self._llm

    async def parse_resume_bytes(
        self,
        pdf_bytes: bytes,
        filename: str = "resume.pdf",
    ) -> ResumeParsedSections:
        """Extracts text from PDF and runs structured parsing with LangSmith observability."""
        text, links = extract_text_and_links_from_pdf(pdf_bytes)
        if not text.strip():
            logger.warning(f"Extracted empty text from {filename}")
            raise ValueError(f"Resume '{filename}' contains no readable text. Data was not saved. Please verify the document.")

        return await self.parse_resume_text(text, filename=filename, initial_links=links)

    async def parse_resume_text(
        self,
        resume_text: str,
        filename: str = "resume.txt",
        initial_links: Optional[list[str]] = None,
    ) -> ResumeParsedSections:
        """Parses raw resume plaintext into ResumeParsedSections schema."""
        initial_links = initial_links or []

        try:
            llm = self._get_llm()
            structured_llm = llm.with_structured_output(ResumeParsedSections)

            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", RESUME_EXTRACTION_SYSTEM_PROMPT),
                    (
                        "human",
                        "Parse the following resume document text into structured sections:\n\n"
                        "FILENAME: {filename}\n"
                        "EXTRACTED HYPERLINKS: {hyperlinks}\n\n"
                        "DOCUMENT CONTENT:\n{resume_text}",
                    ),
                ]
            )

            chain = prompt | structured_llm

            # LangSmith tracing metadata
            config = {
                "tags": ["careerlens", "resume_parser", "groq", "universal"],
                "metadata": {
                    "filename": filename,
                    "model": self.model_name,
                    "text_length": len(resume_text),
                },
            }

            result: ResumeParsedSections = await groq_rate_limiter.execute(
                chain.ainvoke,
                {
                    "filename": filename,
                    "hyperlinks": ", ".join(initial_links) if initial_links else "None",
                    "resume_text": resume_text[:25000],  # Bound input token context
                },
                config=config,
            )

            # Ensure raw_text and links are retained
            result.raw_text = resume_text
            for link in initial_links:
                if link not in result.portfolio_links:
                    result.portfolio_links.append(link)

            # Validate completeness
            is_complete, reason = validate_parsed_sections(result, resume_text)
            if not is_complete:
                logger.warning(f"Extracted data for {filename} is incomplete: {reason}")
                raise ValueError(
                    f"Parsed resume data was incomplete ({reason}). "
                    "Data was discarded to prevent corrupted evaluation. Please parse again."
                )

            logger.info(
                f"Successfully parsed resume for '{result.candidate_name}' ({len(result.work_experience)} roles, {len(result.core_competencies)} competencies)"
            )
            return result

        except Exception as exc:
            logger.error(
                f"LLM parsing failed or was disrupted for {filename}: {exc}.",
                exc_info=True,
            )
            # Do NOT silently save incomplete fallback data to the database
            raise ValueError(
                f"Parsing was disrupted or produced incomplete data ({type(exc).__name__}: {str(exc)[:120]}). "
                "Data was not saved in the database. Please try parsing again."
            )

    def _fallback_parse(
        self,
        resume_text: str,
        filename: str,
        links: list[str],
    ) -> ResumeParsedSections:
        """Safe non-blocking heuristic parser when Groq is unavailable or network is blocked."""
        lines = [line.strip() for line in resume_text.splitlines() if line.strip()]
        candidate_name = lines[0] if lines else filename.replace(".pdf", "").replace("_", " ")
        # Clean candidate name if it contains cid artifacts
        candidate_name = candidate_name.split("(cid:")[0].strip()

        # Look for email and phone heuristics
        email = None
        phone = None
        for line in lines[:10]:
            if "@" in line and not email:
                for w in line.split():
                    if "@" in w:
                        email = w.strip("<>(),;:#'\"")
            if any(char.isdigit() for char in line) and any(
                sym in line for sym in ["+", "(", ")", "-"]
            ):
                if not phone and len(line) < 35:
                    phone = line.split("#")[0].strip()

        # Sections tracking
        current_section = None
        skills_lines: list[str] = []
        experience_blocks: list[dict] = []
        project_blocks: list[dict] = []
        education_lines: list[str] = []

        for line in lines:
            upper = line.upper()
            if any(h in upper for h in ["TECHNICAL SKILLS", "SKILLS & EXPERTISE", "CORE SKILLS", "COMPETENCIES"]):
                current_section = "SKILLS"
                continue
            elif any(h in upper for h in ["EXPERIENCE", "WORK EXPERIENCE", "EMPLOYMENT HISTORY"]):
                current_section = "EXPERIENCE"
                continue
            elif any(h in upper for h in ["PROJECTS", "PERSONAL PROJECTS", "KEY DELIVERABLES"]):
                current_section = "PROJECTS"
                continue
            elif any(h in upper for h in ["EDUCATION", "ACADEMIC BACKGROUND", "CREDENTIALS"]):
                current_section = "EDUCATION"
                continue
            elif any(h in upper for h in ["CERTIFICATIONS", "LICENSES", "AWARDS", "PUBLICATIONS"]):
                current_section = "CERTIFICATIONS"
                continue

            if current_section == "SKILLS":
                skills_lines.append(line)
            elif current_section == "EXPERIENCE":
                experience_blocks.append(line)
            elif current_section == "PROJECTS":
                project_blocks.append(line)
            elif current_section == "EDUCATION":
                education_lines.append(line)

        # Parse skills
        core_competencies: list[str] = []
        for s_line in skills_lines:
            content = s_line.split(":", 1)[-1] if ":" in s_line else s_line
            tokens = [t.strip() for t in content.split(",") if len(t.strip()) > 1]
            for tok in tokens:
                if tok not in core_competencies and len(tok) < 50:
                    core_competencies.append(tok)

        # Parse projects
        projects: list[ProjectItem] = []
        current_proj: Optional[dict] = None
        for p_line in project_blocks:
            if p_line.startswith("•") or p_line.startswith("-") or p_line.startswith("*"):
                bullet = p_line.lstrip("•-* ").strip()
                if bullet.lower().startswith("technologies:"):
                    tech_str = bullet.split(":", 1)[-1]
                    if current_proj:
                        current_proj["technologies"] = [t.strip() for t in tech_str.split(",") if t.strip()]
                else:
                    if current_proj:
                        current_proj["responsibilities_and_outcomes"].append(bullet)
            else:
                # New project header
                if current_proj:
                    projects.append(ProjectItem(**current_proj))
                title = p_line.split("(")[0].strip()
                link = None
                for lk in links:
                    if title.lower().replace(" ", "-") in lk.lower():
                        link = lk
                current_proj = {
                    "title": title,
                    "description": p_line,
                    "technologies": [],
                    "responsibilities_and_outcomes": [],
                    "link": link,
                }
        if current_proj:
            projects.append(ProjectItem(**current_proj))

        # Parse work experience
        work_experience: list[WorkExperienceItem] = []
        current_exp: Optional[dict] = None
        for e_line in experience_blocks:
            if e_line.startswith("•") or e_line.startswith("-") or e_line.startswith("*"):
                bullet = e_line.lstrip("•-* ").strip()
                if bullet.lower().startswith("technologies:"):
                    tech_str = bullet.split(":", 1)[-1]
                    if current_exp:
                        current_exp["tools_and_methods"] = [t.strip() for t in tech_str.split(",") if t.strip()]
                else:
                    if current_exp:
                        current_exp["responsibilities_and_achievements"].append(bullet)
            else:
                if current_exp:
                    work_experience.append(WorkExperienceItem(**current_exp))
                parts = e_line.split(",")
                role_title = parts[0].strip() if parts else e_line
                employer = parts[1].split("(")[0].strip() if len(parts) > 1 else "Organization"
                current_exp = {
                    "role_title": role_title,
                    "employer": employer,
                    "responsibilities_and_achievements": [],
                    "tools_and_methods": [],
                }
        if current_exp:
            work_experience.append(WorkExperienceItem(**current_exp))

        # Parse education
        education: list[EducationItem] = []
        if education_lines:
            first_edu = education_lines[0]
            second_edu = education_lines[1] if len(education_lines) > 1 else ""
            education.append(
                EducationItem(
                    institution=first_edu.split("20")[0].strip(),
                    degree_name=second_edu.split("-")[0].strip() or "Computer Engineering",
                    field_of_study=second_edu.strip() if second_edu else None,
                )
            )

        summary = (
            f"Candidate profile for {candidate_name} with {len(projects)} key technical deliverables and "
            f"{len(work_experience)} verified roles in AI/ML engineering."
        )

        return ResumeParsedSections(
            candidate_name=candidate_name,
            email=email,
            phone=phone,
            portfolio_links=links,
            professional_summary=summary,
            work_experience=work_experience,
            projects=projects,
            core_competencies=core_competencies,
            education=education,
            certifications_and_licenses=[],
            raw_text=resume_text,
        )


# Global singleton instance
groq_parser = UniversalResumeParser()


async def parse_resume_with_groq(
    resume_text: str,
    initial_links: Optional[list[str]] = None,
    filename: str = "resume.txt",
) -> ResumeParsedSections:
    """Convenience functional interface for structured Groq parsing."""
    return await groq_parser.parse_resume_text(
        resume_text=resume_text,
        filename=filename,
        initial_links=initial_links,
    )
