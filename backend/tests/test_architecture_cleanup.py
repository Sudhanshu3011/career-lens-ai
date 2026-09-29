import pytest


def test_obsolete_modules_removed():
    """Verify that all obsolete deterministic and legacy modules raise ImportError."""
    obsolete_modules = [
        "app.tools.job_matcher",
        "app.tools.job_search",
        "app.tools.diagnostic_feedback_generator",
        "app.parser.pdf_parser",
        "app.extraction.entity_extractor",
        "app.db.session",
        "app.report.report_builder",
        "app.validator.pdf_validator",
        "app.services.enterprise_screening_service",
        "app.services.typesafe_pipeline",
        "app.data.tech_skills_db",
        "app.engines.extraction.entity_extractor",
        "app.engines.extraction.evidence_builder",
        "app.engines.extraction.jd_extractor",
        "app.engines.extraction.resume_entity_extractor",
        "app.engines.extraction.tech_keywords",
        "app.engines.evaluation.candidate_scorer",
        "app.engines.evaluation.composite_score",
        "app.engines.evaluation.requirement_matcher",
        "app.engines.evaluation.seniority_evaluator",
        "app.engines.parser.block_builder",
        "app.engines.parser.deterministic_parser",
        "app.engines.parser.layout_analyzer",
        "app.engines.parser.pdf_parser",
        "app.engines.jev.confidence",
        "app.engines.jev.questions",
        "app.engines.jev.rubric",
        "app.models.domain.candidate",
        "app.models.domain.decision",
        "app.models.domain.evidence",
        "app.models.domain.job",
        "app.utils.report_builder",
    ]

    for mod in obsolete_modules:
        with pytest.raises(ImportError):
            __import__(mod)
