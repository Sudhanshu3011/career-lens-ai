"""
CareerLens AI - API Dependencies
Provides database session dependency and other shared endpoint dependencies.
"""

from __future__ import annotations

from typing import Generator
from sqlalchemy.orm import Session
from app.core.database import get_db

get_database_session = get_db

__all__ = ["get_db", "get_database_session", "Session"]
