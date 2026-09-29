import pytest


def test_obsolete_modules_removed():
    with pytest.raises(ImportError):
        import app.tools.job_matcher  # type: ignore
    with pytest.raises(ImportError):
        import app.tools.job_search  # type: ignore
    with pytest.raises(ImportError):
        import app.tools.diagnostic_feedback_generator  # type: ignore
    with pytest.raises(ImportError):
        import app.parser.pdf_parser  # type: ignore
    with pytest.raises(ImportError):
        import app.extraction.entity_extractor  # type: ignore
    with pytest.raises(ImportError):
        import app.db.session  # type: ignore
    with pytest.raises(ImportError):
        import app.report.report_builder  # type: ignore
    with pytest.raises(ImportError):
        import app.validator.pdf_validator  # type: ignore
    with pytest.raises(ImportError):
        import app.services.enterprise_screening_service  # type: ignore
