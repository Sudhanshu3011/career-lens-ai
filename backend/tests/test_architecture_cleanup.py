import pytest


def test_obsolete_modules_removed():
    with pytest.raises(ImportError):
        import app.tools.job_matcher  # type: ignore
    with pytest.raises(ImportError):
        import app.tools.job_search  # type: ignore
    with pytest.raises(ImportError):
        import app.tools.diagnostic_feedback_generator  # type: ignore
