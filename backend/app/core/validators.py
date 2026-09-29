"""
CareerLens AI - Core Validators
Validates file extension, MIME types, magic bytes (%PDF), and size limits.
"""

from __future__ import annotations

from typing import Set
from fastapi import HTTPException, UploadFile, status
from app.core.config import settings

VALID_PDF_MIME_TYPES: Set[str] = {
    "application/pdf",
    "application/x-pdf",
    "application/acrobat",
    "applications/vnd.pdf",
    "text/pdf",
    "application/octet-stream",
}


def validate_pdf_metadata(file: UploadFile) -> None:
    """Validates file extension and declared MIME type before reading content."""
    filename = (file.filename or "").strip()
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File '{filename or 'unnamed'}' is not a PDF. All resumes must have a .pdf extension.",
        )

    content_type = (file.content_type or "").split(";")[0].strip().lower()
    if content_type not in VALID_PDF_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"File '{filename}' has invalid MIME type '{file.content_type}'. "
                "All uploaded files must have a valid PDF MIME type ('application/pdf')."
            ),
        )


def validate_pdf(file: UploadFile, data: bytes) -> None:
    """Validates uploaded PDF bytes against MIME type, size limit, and PDF magic bytes."""
    validate_pdf_metadata(file)

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(data) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB} MB.",
        )

    if not data.startswith(b"%PDF"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or corrupted PDF file. File does not contain valid PDF headers.",
        )
