"""
CareerLens AI - Question Factory Package
"""

from app.engines.question_factory.generator import (
    UniversalQuestionFactory,
    preview_job_requirements,
    question_factory,
)
from app.engines.question_factory.adapter import BlueprintToEngineAdapter

QuestionFactory = UniversalQuestionFactory
DynamicQuestionFactory = UniversalQuestionFactory

__all__ = [
    "UniversalQuestionFactory",
    "DynamicQuestionFactory",
    "QuestionFactory",
    "question_factory",
    "preview_job_requirements",
    "BlueprintToEngineAdapter",
]
