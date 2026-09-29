"""
CareerLens AI - System Health & Verification Endpoints
"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["System Health"])


@router.get("/health", summary="Health check")
async def health_check():
    """System health check and pipeline status."""
    return {
        "status": "healthy",
        "service": "careerlens-enterprise",
        "version": "1.0.0",
        "pipeline": "universal-speculative-fanout",
    }
