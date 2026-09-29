"""
CareerLens AI - API v1 Master Router
Aggregates jobs, resumes, and system health endpoint routers into a clean API contract.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints.analysis import router as health_router
from app.api.v1.endpoints.jobs import router as jobs_router
from app.api.v1.endpoints.resumes import router as resumes_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(jobs_router)
api_router.include_router(resumes_router)

__all__ = ["api_router"]
