from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class BackgroundClassificationBlueprint(BaseModel):
    question: str = Field(
        description="Recruiter instruction classifying the candidate's domain background"
    )
    options: Dict[str, str] = Field(
        description="Three mutually exclusive options: 'direct_domain_match', 'adjacent_domain_transfer', 'unrelated_background'"
    )


class AscendingAssessmentBlueprint(BaseModel):
    question: str = Field(description="Recruiter rating instruction")
    levels: List[str] = Field(
        description="Strictly ordered list of ascending levels from Level 0 to Level 5"
    )


class MandatoryDealbreakerBlueprint(BaseModel):
    name: str = Field(
        description="Short human-readable label (e.g., 'Active State RN License', 'CPA Certification', 'Minimum 4 Years Experience')"
    )
    question: str = Field(description="Direct yes/no verification question")


class EvaluationQuestionsBlueprint(BaseModel):
    role_title: str = Field(description="Normalized job title")
    seniority_target: str = Field(description="Target seniority level extracted from the JD")
    domain_alignment: BackgroundClassificationBlueprint = Field(
        description="Choice classification blueprint for domain background fit"
    )
    seniority_assessment: AscendingAssessmentBlueprint = Field(
        description="Score rating blueprint (0 to 5) for candidate seniority level fit"
    )
    competency_depth_assessment: AscendingAssessmentBlueprint = Field(
        description="Score rating blueprint (0 to 5) for core domain competencies & tools mastery"
    )
    experience_duration_assessment: Optional[AscendingAssessmentBlueprint] = Field(
        default=None,
        description="Score rating blueprint (0 to 5) for relevant practical experience duration and hands-on track record",
    )
    education_credentials_assessment: Optional[AscendingAssessmentBlueprint] = Field(
        default=None,
        description="Score rating blueprint (0 to 5) for educational domain relevance and academic credentials",
    )
    evidence_quality_assessment: AscendingAssessmentBlueprint = Field(
        description="Score rating blueprint (0 to 5) for quantifiable impact and verified deliverables"
    )
    mandatory_dealbreakers: List[MandatoryDealbreakerBlueprint] = Field(
        default_factory=list,
        description="Binary Noul gate blueprints for non-negotiable hard requirements",
    )

