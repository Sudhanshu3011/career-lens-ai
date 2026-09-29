"""
Pytest global fixtures for CareerLens AI test suite.
"""

import os
import pytest
from app.core.rate_limiter import groq_rate_limiter


@pytest.fixture(autouse=True)
def configure_test_rate_limiter():
    """
    Sets rate limiter cooldown to 0.0s during test execution so unit tests
    run in milliseconds without 60s production sleeps.
    """
    prev_interval = groq_rate_limiter.interval
    prev_cooldown = groq_rate_limiter.post_call_cooldown

    groq_rate_limiter.interval = 0.0
    groq_rate_limiter.post_call_cooldown = 0.0
    yield
    groq_rate_limiter.interval = prev_interval
    groq_rate_limiter.post_call_cooldown = prev_cooldown
