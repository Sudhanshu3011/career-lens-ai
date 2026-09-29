"""
CareerLens AI - Universal Dynamic Question Factory
Dynamically synthesizes bespoke TypeSafe assessment questions and ascending criteria from any Job Description.
Universal across all industries (Healthcare, Finance, Legal, Tech, Sales, Operations).
Traced in LangSmith.
"""

from __future__ import annotations

import json
from typing import Optional
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.core.config import settings
from app.core.logger import get_logger
from app.core.rate_limiter import groq_rate_limiter
from app.models.domain.dynamic_blueprint import (
    AscendingAssessmentBlueprint,
    BackgroundClassificationBlueprint,
    EvaluationQuestionsBlueprint,
    MandatoryDealbreakerBlueprint,
)

logger = get_logger(__name__)

EVALUATION_QUESTIONS_SYSTEM_PROMPT = """
You are an expert Senior Recruiter and Talent Assessment Architect across all professional industries (Technology, Healthcare, Finance, Legal, Operations, Sales, and Engineering).

Analyze the target Job Description (JD) and produce the exact assessment questions and criteria required to objectively evaluate applicants for this specific requisition.

CRITICAL INSTRUCTIONS:
1. UNIVERSAL DOMAIN ADAPTATION:
   - Identify the exact profession and industry of the job description.
   - Tailor the questions, levels, and mandatory criteria directly to the domain standards of that profession.
2. SYNTHESIZE SEVEN ESSENTIAL EVALUATION CRITERIA:
   - `domain_alignment`: A question and 3 mutually exclusive background categories:
     * direct_domain_match: Core hands-on professional practice in this specific role and discipline.
     * adjacent_domain_transfer: Related functional background with transferable competencies but missing direct specialization.
     * unrelated_background: Unrelated career background with negligible functional overlap.
   - `seniority_assessment`: A question and 6 strictly ascending levels of career maturity (Level 0 to 5) matching the JD's seniority demands.
   - `competency_depth_assessment`: A question and 6 strictly ascending levels of practical capability (Level 0 to 5), explicitly referencing the key tools, methods, regulations, or techniques required by the JD.
   - `experience_duration_assessment`: A question and 6 strictly ascending levels of relevant practical experience duration (Level 0 to 5), matching the tenure and years demanded by the JD.
   - `education_credentials_assessment`: A question and 6 strictly ascending levels of educational relevance and academic credentials (Level 0 to 5), evaluating whether the candidate's degree, major, or coursework directly matches the domain.
   - `evidence_quality_assessment`: A question and 6 strictly ascending levels (Level 0 to 5) measuring verifiable achievements, metrics, and concrete business/operational impact.
   - `mandatory_dealbreakers`: Direct yes/no verification questions for every strict, non-negotiable requirement (e.g. required state licenses, certifications, mandatory minimum experience, degrees, or clearances).


---
### WORKED EXAMPLE 1 (Healthcare / Nursing):
[JOB REQUISITION]
Role: Critical Care / ICU Registered Nurse (RN)
Description: "Requires minimum 3+ years of acute care ICU clinical experience. Mandatory: Active State RN License, BLS, ACLS. Core: Invasive hemodynamic monitoring, mechanical ventilation, vasoactive drip titration. BSN preferred."

[EXPECTED OUTPUT]
{
  "role_title": "Critical Care / ICU Registered Nurse (RN)",
  "seniority_target": "Mid-to-Senior Staff Nurse",
  "domain_alignment": {
    "question": "Classify the candidate's clinical nursing background against the ICU Registered Nurse requisition:",
    "options": {
      "direct_domain_match": "Experienced acute care ICU or critical care staff nurse with direct bedside critical patient management.",
      "adjacent_domain_transfer": "Registered Nurse with telemetry, emergency department (ED), or step-down experience, but limited ICU exposure.",
      "unrelated_background": "Non-clinical healthcare roles, outpatient clinic only, or non-nursing backgrounds."
    }
  },
  "seniority_assessment": {
    "question": "Rate the candidate's clinical nursing seniority against the target ICU Staff Nurse requisition (3+ years required):",
    "levels": [
      "Level 0: Nursing student, new graduate nurse, or unlicensed healthcare worker.",
      "Level 1: Novice Nurse (0-1 year) completing nurse residency or orientation, requiring direct preceptor supervision.",
      "Level 2: Competent Staff Nurse (1-3 years) independently caring for standard acute care/ICU patients.",
      "Level 3: Experienced Critical Care Nurse (3-6 years) adeptly managing complex multi-organ failure patients, titrating critical drips.",
      "Level 4: Senior ICU Nurse / Charge Nurse (6-10 years) running unit shifts, precepting new nurses, leading rapid response/code blue.",
      "Level 5: Clinical Nurse Specialist / Nurse Manager (10+ years) driving ICU clinical protocols, unit quality, and hospital-wide standards."
    ]
  },
  "competency_depth_assessment": {
    "question": "Rate the candidate's clinical competency depth in ICU care (mechanical ventilation, hemodynamic monitoring, and vasoactive drips):",
    "levels": [
      "Level 0: No practical clinical exposure to ICU patient management or critical care protocols.",
      "Level 1: Academic nursing knowledge or observational rotation without independent patient assignment.",
      "Level 2: Basic telemetry, med-surg, or outpatient care lacking advanced ventilation or invasive line management.",
      "Level 3: Routine management of ventilated patients, arterial lines, central lines, and standard IV vasoactive titrations.",
      "Level 4: Advanced critical care mastery: Managing patients on ECMO/CRRT, complex hemodynamic instability, and emergency intubation assist.",
      "Level 5: Unit super-user / clinical educator: Protocols development for critical care, advanced life support training, and critical incident leadership."
    ]
  },
  "experience_duration_assessment": {
    "question": "Rate the candidate's total verified acute care ICU clinical experience duration against the 3+ years requirement:",
    "levels": [
      "Level 0: No acute care or ICU bedside experience.",
      "Level 1: Less than 1 year in acute care or critical care setting.",
      "Level 2: 1-2 years of clinical ICU experience.",
      "Level 3: 3-5 years of direct acute ICU bedside experience (meets baseline requirement).",
      "Level 4: 5-8 years of seasoned ICU nursing experience.",
      "Level 5: 8+ years of dedicated critical care / trauma ICU clinical tenure."
    ]
  },
  "education_credentials_assessment": {
    "question": "Rate the relevance and accreditation of candidate's nursing education against the ICU RN requisition:",
    "levels": [
      "Level 0: No nursing degree or non-accredited nursing program.",
      "Level 1: Licensed Practical Nurse (LPN/LVN) diploma.",
      "Level 2: Associate Degree in Nursing (ADN / ASN).",
      "Level 3: Bachelor of Science in Nursing (BSN) from accredited nursing school.",
      "Level 4: Master of Science in Nursing (MSN) or acute care clinical specialty focus.",
      "Level 5: Doctor of Nursing Practice (DNP) or advanced practice credential."
    ]
  },
  "evidence_quality_assessment": {
    "question": "Rate the quality and specificity of clinical achievements and patient care outcomes in the candidate's record:",
    "levels": [
      "Level 0: No clinical details, hospital affiliations, or unit context provided.",
      "Level 1: Vague generic duties with no unit acuity or patient caseload details.",
      "Level 2: Standard duty descriptions listing unit type and basic nursing tasks without quality or safety indicators.",
      "Level 3: Detailed clinical track record with unit bed count, patient-to-nurse ratios, and specific procedures handled.",
      "Level 4: Strong clinical evidence including hospital designations (Magnet, Level 1 Trauma) or quality committee participation.",
      "Level 5: Exceptional leadership impact: Unit practice council chair, published clinical research, or regional nursing excellence award."
    ]
  },
  "mandatory_dealbreakers": [
    { "name": "Active State RN License", "question": "Does the candidate hold an active, unencumbered Registered Nurse (RN) license?" },
    { "name": "BLS and ACLS Certifications", "question": "Does the candidate hold active Basic Life Support (BLS) and Advanced Cardiovascular Life Support (ACLS) certifications?" },
    { "name": "Minimum 3 Years ICU Experience", "question": "Does the candidate have verified work experience demonstrating at least 3 years in an acute ICU or critical care setting?" }
  ]
}

---
### WORKED EXAMPLE 2 (Technology / AI Engineering):
[JOB REQUISITION]
Role: Senior Generative AI & ML Engineer
Description: "Minimum 4+ years of professional engineering experience. Must-have: Machine Learning (ML), PyTorch, LLMs, LangChain, Vector DBs, AWS. BS/MS in CS or related field."

[EXPECTED OUTPUT]
{
  "role_title": "Senior Generative AI & ML Engineer",
  "seniority_target": "Senior Engineer",
  "domain_alignment": {
    "question": "Classify the candidate's professional background against the Senior Generative AI & ML Engineer requisition:",
    "options": {
      "direct_domain_match": "Hands-on engineering background in Machine Learning, PyTorch, LLMs, LangChain, or AI infrastructure.",
      "adjacent_domain_transfer": "Software or DevOps engineer with standard web/cloud experience but minimal hands-on ML/GenAI model delivery.",
      "unrelated_background": "Non-engineering backgrounds such as sales, marketing, business development, HR, or operations."
    }
  },
  "seniority_assessment": {
    "question": "Rate the candidate's career seniority against the target Senior Engineer requisition (4+ years required):",
    "levels": [
      "Level 0: Student, intern, or academic research without full-time commercial engineering experience.",
      "Level 1: Junior Engineer (0-2 years) with foundational coding skills requiring direct task oversight.",
      "Level 2: Mid-Level Engineer (2-4 years) independently shipping ML/AI features and production components.",
      "Level 3: Senior Engineer (4-7 years) autonomously architecting GenAI pipelines, RAG systems, and guiding juniors.",
      "Level 4: Lead / Staff Engineer (7-10 years) driving multi-team AI initiatives, infrastructure scale, and model strategy.",
      "Level 5: Principal Architect (10+ years) leading company-wide AI strategy, foundational model research, or VP of AI."
    ]
  },
  "competency_depth_assessment": {
    "question": "Rate the candidate's practical depth in the required stack (PyTorch, LLMs, LangChain, Vector DBs, and AWS):",
    "levels": [
      "Level 0: No practical exposure to PyTorch, LLMs, Vector DBs, or Machine Learning workflows.",
      "Level 1: Surface-level keyword mention or basic theoretical knowledge without code delivery.",
      "Level 2: Tutorial, hobby, or academic projects using pre-trained HuggingFace models or simple API calls.",
      "Level 3: Commercial delivery of GenAI/RAG pipelines using LangChain, Vector DBs, and Python APIs.",
      "Level 4: Production mastery: Fine-tuning LLMs, optimizing GPU inference latency on AWS, and architecting complex agentic flows.",
      "Level 5: Deep architectural mastery: Custom model training, CUDA/kernel optimizations, distributed multi-GPU serving, and core GenAI research."
    ]
  },
  "experience_duration_assessment": {
    "question": "Rate the candidate's total verified professional engineering experience duration against the 4+ years requirement:",
    "levels": [
      "Level 0: No commercial software or ML engineering experience.",
      "Level 1: 0-2 years of software engineering or data science experience.",
      "Level 2: 2-4 years of commercial engineering experience.",
      "Level 3: 4-6 years of solid, demonstrated software/ML engineering experience (meets baseline requirement).",
      "Level 4: 6-9 years of extensive engineering tenure exceeding baseline expectations.",
      "Level 5: 10+ years of deep engineering experience, technical leadership, and architect-level tenure."
    ]
  },
  "education_credentials_assessment": {
    "question": "Rate the relevance and accreditation of candidate's academic degrees against the Computer Science / Quantitative requirement:",
    "levels": [
      "Level 0: No degree or completely non-technical/unrelated field with no quantitative coursework.",
      "Level 1: Self-taught or non-degree coding bootcamps with portfolio projects.",
      "Level 2: Associate degree or minor in STEM/quantitative discipline.",
      "Level 3: Bachelor's degree (BS/B.Tech) in Computer Science, Data Science, Math, or Engineering.",
      "Level 4: Master's degree (MS/M.Tech) in Computer Science, AI, or Machine Learning.",
      "Level 5: Ph.D. in Computer Science, Machine Learning, or related computational discipline."
    ]
  },
  "evidence_quality_assessment": {
    "question": "Rate the verifiable quality of achievements and engineering metrics in the candidate's track record:",
    "levels": [
      "Level 0: Zero verifiable evidence or project descriptions provided.",
      "Level 1: Vague assertions with no context, deliverables, or stack details.",
      "Level 2: Basic descriptions of projects with tools listed, but lacking quantifiable scale or impact metrics.",
      "Level 3: Specific commercial implementations detailing business context, architecture, and technology deliverables.",
      "Level 4: Strong production evidence with verified performance metrics (e.g., 'reduced latency by 40%', 'served 2M queries/day').",
      "Level 5: Exceptional verifiable impact: Patents, published benchmarks, open-source adoption, or major commercial cost reductions."
    ]
  },
  "mandatory_dealbreakers": [
    { "name": "Minimum 4 Years Experience", "question": "Does the candidate's verified work timeline demonstrate at least 4 full years of professional engineering experience?" },
    { "name": "Core Machine Learning & PyTorch", "question": "Does the candidate have verified, hands-on commercial experience in Machine Learning and PyTorch?" },
    { "name": "LLM & RAG Pipeline Delivery", "question": "Does the candidate possess concrete work evidence implementing Large Language Models, LangChain, or RAG architectures?" },
    { "name": "Quantitative Degree Requirement", "question": "Does the candidate hold a Bachelor's, Master's, or higher degree in Computer Science, Data Science, Engineering, or a related quantitative field?" }
  ]
}
"""


class UniversalQuestionFactory:
    """Generates dynamic assessment blueprints from JDs using ChatGroq and LangSmith."""

    def __init__(self, model_name: Optional[str] = None):
        configured = model_name or settings.GROQ_MODEL
        if "qwen" in configured.lower() or "llama" in configured.lower():
            configured = "openai/gpt-oss-120b"
        self.model_name = configured
        self._llm = None

    def _get_llm(self) -> ChatGroq:
        if self._llm is None:
            if not settings.GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY is required to generate dynamic evaluation blueprints.")
            self._llm = ChatGroq(
                model=self.model_name,
                temperature=0.0,
                api_key=settings.GROQ_API_KEY,
                max_retries=2,
                request_timeout=40.0,
            )
        return self._llm

    async def generate_blueprint(
        self,
        job_description: str,
        role_title: str = "Target Position",
    ) -> EvaluationQuestionsBlueprint:
        """Synthesizes dynamic questions and criteria from a raw JD."""
        try:
            llm = self._get_llm()
            structured_llm = llm.with_structured_output(EvaluationQuestionsBlueprint)

            prompt = ChatPromptTemplate.from_messages(
                [
                    SystemMessage(content=EVALUATION_QUESTIONS_SYSTEM_PROMPT),
                    (
                        "human",
                        "Analyze the following job requisition and produce the evaluation blueprint:\n\n"
                        "ROLE TITLE: {role_title}\n\n"
                        "JOB DESCRIPTION:\n{job_description}",
                    ),
                ]
            )

            chain = prompt | structured_llm

            config = {
                "tags": ["careerlens", "question_factory", "groq", "universal"],
                "metadata": {
                    "role_title": role_title,
                    "model": self.model_name,
                },
            }

            blueprint: EvaluationQuestionsBlueprint = await groq_rate_limiter.execute(
                chain.ainvoke,
                {
                    "role_title": role_title,
                    "job_description": job_description[:12000],
                },
                config=config,
            )

            logger.info(
                f"Generated dynamic evaluation blueprint for '{blueprint.role_title}' with {len(blueprint.mandatory_dealbreakers)} mandatory dealbreakers"
            )
            return blueprint

        except Exception as exc:
            logger.error(
                f"Dynamic blueprint generation failed: {exc}. Using deterministic fallback blueprint.",
                exc_info=True,
            )
            return self._fallback_blueprint(job_description, role_title)

    def _fallback_blueprint(
        self,
        job_description: str,
        role_title: str,
    ) -> EvaluationQuestionsBlueprint:
        """Fallback blueprint when Groq is unreachable."""
        return EvaluationQuestionsBlueprint(
            role_title=role_title,
            seniority_target="Professional / Mid-Senior",
            domain_alignment=BackgroundClassificationBlueprint(
                question=f"Classify the candidate's professional background against the {role_title} requisition:",
                options={
                    "direct_domain_match": f"Core hands-on professional tenure in {role_title} and direct required disciplines.",
                    "adjacent_domain_transfer": "Related professional background with transferable skills but indirect specialization.",
                    "unrelated_background": "Completely unrelated career field with negligible relevant overlap.",
                },
            ),
            seniority_assessment=AscendingAssessmentBlueprint(
                question=f"Rate candidate career seniority against {role_title} expectations:",
                levels=[
                    "Level 0: Student, intern, or entry-level novice without full-time commercial experience.",
                    "Level 1: Junior Practitioner (0-2 years) requiring direct oversight.",
                    "Level 2: Mid-Level Practitioner (2-4 years) working independently on standard assignments.",
                    "Level 3: Senior Specialist (4-7 years) autonomously leading initiatives and mentoring.",
                    "Level 4: Staff / Lead / Director (7-10 years) guiding strategy, operations, and cross-functional teams.",
                    "Level 5: Principal / Executive (10+ years) directing organization-wide policy and practice.",
                ],
            ),
            competency_depth_assessment=AscendingAssessmentBlueprint(
                question=f"Rate candidate's competency depth in the core skills and tools required for {role_title}:",
                levels=[
                    "Level 0: No practical exposure to the required domain tools or methods.",
                    "Level 1: Theoretical knowledge or casual exposure without commercial application.",
                    "Level 2: Basic hands-on execution on guided or routine assignments.",
                    "Level 3: Proficient independent practitioner executing standard industry workflows.",
                    "Level 4: Advanced domain expert solving complex anomalies and optimizing systems.",
                    "Level 5: Master practitioner, author of industry best-practices, or acknowledged authority.",
                ],
            ),
            experience_duration_assessment=AscendingAssessmentBlueprint(
                question=f"Rate candidate's total relevant practical experience duration against {role_title} requirements:",
                levels=[
                    "Level 0: No commercial experience or less than 1 year in a related field.",
                    "Level 1: 1-2 years of relevant practical hands-on experience.",
                    "Level 2: 2-4 years of verified commercial experience.",
                    "Level 3: 4-6 years of solid, demonstrated professional experience.",
                    "Level 4: 6-9 years of extensive track record exceeding standard requirements.",
                    "Level 5: 10+ years of deep domain experience and industry veteran status.",
                ],
            ),
            education_credentials_assessment=AscendingAssessmentBlueprint(
                question=f"Rate the relevance and accreditation of candidate's academic degrees to {role_title}:",
                levels=[
                    "Level 0: No degree listed or completely unrelated field without relevant coursework.",
                    "Level 1: Non-degree certifications or coursework in related domain.",
                    "Level 2: Associate degree or minor in a relevant discipline.",
                    "Level 3: Accredited Bachelor's degree in a directly relevant field of study.",
                    "Level 4: Master's degree in the exact or directly adjacent technical/professional specialization.",
                    "Level 5: Doctorate (Ph.D.), terminal degree, or prestigious specialized postgraduate credential.",
                ],
            ),
            evidence_quality_assessment=AscendingAssessmentBlueprint(
                question="Rate the verifiable quality and impact of the candidate's achievements:",
                levels=[
                    "Level 0: No verifiable accomplishments or deliverables listed.",
                    "Level 1: Generic duty list with zero metrics or outcomes.",
                    "Level 2: Descriptive project summaries lacking quantified impact.",
                    "Level 3: Solid commercial deliverables with clear scope and context.",
                    "Level 4: Highly quantified achievements with proven revenue, efficiency, or clinical outcomes.",
                    "Level 5: Transformative industry impact, awards, published innovations, or patents.",
                ],
            ),
            mandatory_dealbreakers=[
                MandatoryDealbreakerBlueprint(
                    name="Core Experience Requirement",
                    question=f"Does the candidate demonstrate sufficient verified professional experience in {role_title}?",
                )
            ],
        )


# Global singleton instance
question_factory = UniversalQuestionFactory()


async def preview_job_requirements(
    job_description: str,
    job_role: str = "",
    pipeline_mode: str = "typesafe",
) -> dict:
    """
    Generates transparent requirement preview using UniversalQuestionFactory.
    Compiles the LLM blueprint into the exact typed question schema (Choice, Score, Noul)
    fed to Laya or Jev with full criteria rubrics.
    """
    from app.engines.question_factory.adapter import BlueprintToEngineAdapter

    # 1. Synthesize dynamic blueprint from the target JD
    blueprint = await question_factory.generate_blueprint(
        job_description=job_description,
        role_title=job_role or "Target Position",
    )

    # 2. Compile blueprint into exact TypeSafe / Laya System One questions
    raw_questions, gate_registry = BlueprintToEngineAdapter.compile_questions(blueprint)

    # 3. Format exact questions dictionary with primitive types and criteria as fed to Laya / Jev
    laya_questions: dict[str, dict] = {}
    for q_id, q_obj in raw_questions.items():
        if isinstance(q_obj, dict):
            q_type = q_obj.get("type", "choice").lower()
            inst = q_obj.get("instructions", "")
            crit = q_obj.get("criteria")
        else:
            q_type = getattr(q_obj, "type", "choice").lower()
            inst = getattr(q_obj, "instructions", "")
            crit = getattr(q_obj, "criteria", None)

        if q_type == "score":
            crit_list = (
                crit
                if isinstance(crit, list)
                else ["Level 0", "Level 1", "Level 2", "Level 3", "Level 4", "Level 5"]
            )
            laya_questions[q_id] = {
                "type": "score",
                "primitive": "Score",
                "scale": "0 to 5 (Ordered Rating)",
                "instructions": inst,
                "criteria": crit_list,
            }
        elif q_type == "noul":
            noul_entry = {
                "type": "noul",
                "primitive": "Noul",
                "scale": "Binary Truth Judgment P(True) in [0.0, 1.0]",
                "instructions": inst,
            }
            if isinstance(crit, dict):
                noul_entry["criteria"] = crit
            laya_questions[q_id] = noul_entry
        else:  # choice
            crit_dict = crit if isinstance(crit, dict) else {"general": "General"}
            laya_questions[q_id] = {
                "type": "choice",
                "primitive": "Choice",
                "scale": "Categorical Classification",
                "instructions": inst,
                "criteria": crit_dict,
            }

    # 4. Human-readable suggested requirements for recruiter UI
    suggested_requirements = []
    # Mandatory hard gates
    for gate in blueprint.mandatory_dealbreakers:
        suggested_requirements.append(
            {
                "name": gate.name,
                "category": "Mandatory Requirement",
                "is_hard_requirement": True,
                "target_years": None,
                "description": f"Mandatory qualification: {gate.name}",
                "suggested_gate_question": gate.question,
                "suggested_direct_question": f"Is there verified direct evidence for '{gate.name}'?",
                "suggested_strength_question": f"Rate depth and verified impact in '{gate.name}' (0-5).",
            }
        )

    # Competency benchmark levels
    for idx, lvl in enumerate(blueprint.competency_depth_assessment.levels):
        if idx >= 2:
            suggested_requirements.append(
                {
                    "name": f"Competency Benchmark Level {idx}",
                    "category": "Core Competency",
                    "is_hard_requirement": False,
                    "target_years": None,
                    "description": lvl,
                    "suggested_gate_question": None,
                    "suggested_direct_question": None,
                    "suggested_strength_question": blueprint.competency_depth_assessment.question,
                }
            )

    preview_questions_summary = {
        "domain_alignment_question": blueprint.domain_alignment.question,
        "seniority_question": blueprint.seniority_assessment.question,
        "competency_question": blueprint.competency_depth_assessment.question,
        "evidence_question": blueprint.evidence_quality_assessment.question,
        "mandatory_gates_count": len(blueprint.mandatory_dealbreakers),
        "total_requirements_count": len(suggested_requirements),
    }

    return {
        "success": True,
        "job_role": blueprint.role_title,
        "seniority_score": 4.0 if "senior" in blueprint.seniority_target.lower() else 3.0,
        "seniority_label": blueprint.seniority_target,
        "role_family": blueprint.role_title,
        "domain": blueprint.role_title,
        "total_detected_skills": len(suggested_requirements),
        "detected_skills_by_category": {
            "Mandatory Requirements": [g.name for g in blueprint.mandatory_dealbreakers]
        },
        "suggested_requirements": suggested_requirements,
        "preview_questions_summary": preview_questions_summary,
        "laya_questions": laya_questions,
        "blueprint": blueprint.model_dump(),
    }


DynamicQuestionFactory = UniversalQuestionFactory

