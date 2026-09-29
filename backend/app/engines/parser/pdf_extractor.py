"""
CareerLens AI - Clean Layout-Aware PDF Text Extractor
Extracts raw text, multi-column blocks, and hyperlinks from PDF bytes using pdfplumber.
"""

from __future__ import annotations

import io
from typing import List, Tuple
import pdfplumber

from app.core.logger import get_logger

logger = get_logger(__name__)


def extract_text_and_links_from_pdf(pdf_bytes: bytes) -> Tuple[str, List[str]]:
    """
    Extracts layout-aware plaintext and embedded hyperlinks from PDF bytes.
    Handles single-column, dual-column, and tabular layouts.
    Returns: (extracted_text, hyperlinks)
    """
    extracted_text_pages: List[str] = []
    extracted_hyperlinks: List[str] = []

    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page_idx, page in enumerate(pdf.pages):
                # Extract embedded URLs
                if hasattr(page, "hyperlinks") and page.hyperlinks:
                    for link in page.hyperlinks:
                        uri = link.get("uri")
                        if uri and uri not in extracted_hyperlinks:
                            extracted_hyperlinks.append(uri)

                # Extract text using layout preservation
                page_text = page.extract_text(layout=True)
                if not page_text or len(page_text.strip()) < 20:
                    # Fallback to standard flow extraction
                    page_text = page.extract_text(layout=False) or ""

                if page_text.strip():
                    extracted_text_pages.append(page_text.strip())

        full_text = "\n\n--- PAGE BREAK ---\n\n".join(extracted_text_pages)
        char_count = len(full_text.strip())

        # Character length validation
        if char_count < 80:
            raise ValueError(
                f"Insufficient readable text extracted ({char_count} characters). "
                "The PDF appears to be a scanned image without an OCR layer, blank, or protected. "
                "Minimum required readable length is 80 characters."
            )

        if char_count > 30000:
            logger.warning(
                f"Extracted resume text ({char_count} chars) exceeds safety limits. "
                "Truncating to 25,000 characters to prevent prompt overflow."
            )
            full_text = full_text[:25000]

        return full_text, extracted_hyperlinks

    except ValueError:
        # Re-raise explicit validation errors
        raise
    except Exception as exc:
        logger.error(f"Failed to extract text from PDF bytes: {exc}", exc_info=True)
        # Attempt fallback to lossy utf-8 decoding
        try:
            fallback = pdf_bytes.decode("utf-8", errors="ignore")
            if len(fallback.strip()) >= 80:
                return fallback[:25000], []
        except Exception:
            pass
        raise ValueError(f"Unable to read PDF file: {exc}. Please verify the file is a valid, uncorrupted PDF.")
