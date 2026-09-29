from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class WorkExperienceItem(BaseModel):
    employer: str = Field(description="Company, hospital, clinic, firm, or organization name")
    role_title: str = Field(description="Exact job title held")
    start_date: Optional[str] = Field(None, description="Start date (e.g., '03/2021' or '2019')")
    end_date: Optional[str] = Field(None, description="End date (e.g., '08/2023') or 'Present'")
    is_current: bool = Field(default=False, description="Whether the candidate is currently in this role")
    responsibilities_and_achievements: List[str] = Field(
        default_factory=list,
        description="Quantified outcomes, business impact, clinical procedures, or deliverables",
    )
    tools_and_methods: List[str] = Field(
        default_factory=list,
        description="Domain tools, software, clinical equipment, legal frameworks, or methodologies used",
    )


class EducationItem(BaseModel):
    institution: str = Field(description="University, college, or academic institution name")
    degree_name: str = Field(description="Degree or qualification (e.g., 'Bachelor of Science', 'MD', 'JD', 'MBA')")
    field_of_study: Optional[str] = Field(None, description="Major, field, or specialization (e.g., 'Nursing', 'Computer Science', 'Accounting')")
    graduation_year: Optional[int] = Field(None, description="Graduation year if available")


class ProjectItem(BaseModel):
    title: str = Field(description="Name or title of project, key deliverable, or technical initiative")
    description: Optional[str] = Field(None, description="Overview of the system, product, or research project")
    technologies: List[str] = Field(
        default_factory=list,
        description="Technologies, frameworks, models, or domain tools used",
    )
    responsibilities_and_outcomes: List[str] = Field(
        default_factory=list,
        description="Key features built, metrics achieved, or business impact",
    )
    link: Optional[str] = Field(None, description="Project URL, GitHub repo, live demo, or patent publication")


class ResumeParsedSections(BaseModel):
    candidate_name: str = Field(description="Full legal or professional name of candidate")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    location: Optional[str] = Field(None, description="City, state, or country of residence")
    portfolio_links: List[str] = Field(
        default_factory=list,
        description="LinkedIn, portfolio, GitHub, or professional license registry URLs",
    )
    professional_summary: str = Field(
        default="",
        description="Executive headline, professional summary, or career objective statement",
    )
    work_experience: List[WorkExperienceItem] = Field(
        default_factory=list,
        description="Chronological work and clinical/practical experience records",
    )
    projects: List[ProjectItem] = Field(
        default_factory=list,
        description="Key projects, technical initiatives, research, publications, or client deliverables",
    )
    core_competencies: List[str] = Field(
        default_factory=list,
        description="Key domain skills, methodologies, clinical competencies, or technical capabilities",
    )
    competencies_by_category: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Skills categorized by domain functional buckets (e.g., 'Clinical Care', 'Financial Analysis', 'Cloud Infrastructure')",
    )
    education: List[EducationItem] = Field(
        default_factory=list,
        description="Formal academic degrees and qualifications",
    )
    certifications_and_licenses: List[str] = Field(
        default_factory=list,
        description="State licenses (RN, Bar, CPA, PE), board certifications, industry credentials, or major portfolio projects",
    )
    raw_text: Optional[str] = Field(None, description="Extracted plaintext of resume for auditability and full-state context")

    def format_for_evaluation(self) -> str:
        """Serializes the structured resume into a clean, dense context string for TypeSafe System One engines."""
        lines = [
            f"=== CANDIDATE PROFILE: {self.candidate_name} ===",
            f"Contact: {self.email or 'N/A'} | {self.phone or 'N/A'} | Location: {self.location or 'N/A'}",
            f"Summary: {self.professional_summary}",
            "\n--- CORE COMPETENCIES ---",
            ", ".join(self.core_competencies) if self.core_competencies else "None listed",
            "\n--- CERTIFICATIONS & LICENSES ---",
            ", ".join(self.certifications_and_licenses) if self.certifications_and_licenses else "None listed",
            "\n--- WORK EXPERIENCE ---",
        ]
        for exp in self.work_experience:
            dates = f"{exp.start_date or '?'} - {exp.end_date or ('Present' if exp.is_current else '?')}"
            lines.append(f"• {exp.role_title} at {exp.employer} ({dates})")
            if exp.tools_and_methods:
                lines.append(f"  Methods/Tools: {', '.join(exp.tools_and_methods)}")
            for ach in exp.responsibilities_and_achievements:
                lines.append(f"  - {ach}")

        if self.projects:
            lines.append("\n--- KEY PROJECTS & DELIVERABLES ---")
            for proj in self.projects:
                tech = f" (Tech: {', '.join(proj.technologies)})" if proj.technologies else ""
                lines.append(f"• {proj.title}{tech}")
                if proj.description:
                    lines.append(f"  Description: {proj.description}")
                for outcome in proj.responsibilities_and_outcomes:
                    lines.append(f"  - {outcome}")
                if proj.link:
                    lines.append(f"  Link: {proj.link}")

        lines.append("\n--- EDUCATION ---")
        for edu in self.education:
            year = f" ({edu.graduation_year})" if edu.graduation_year else ""
            field = f" in {edu.field_of_study}" if edu.field_of_study else ""
            lines.append(f"• {edu.degree_name}{field} - {edu.institution}{year}")
        return "\n".join(lines)

    def to_typesafe_state(self) -> str:
        """Serializes candidate profile into typesafe context string for System One evaluation."""
        return self.format_for_evaluation()


# Canonical alias for backward compatibility across endpoints and tests
ParsedResumeSections = ResumeParsedSections
