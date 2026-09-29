"""
CareerLens AI - API v1 Master Router
Aggregates enterprise, sessions, and analysis endpoint routers into a cohesive API contract.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints.analysis import router as analysis_router
from app.api.v1.endpoints.enterprise import router as enterprise_router
from app.api.v1.endpoints.sessions import router as session_router

api_router = APIRouter()

api_router.include_router(analysis_router)
api_router.include_router(session_router)
api_router.include_router(enterprise_router)

__all__ = ["api_router"]
