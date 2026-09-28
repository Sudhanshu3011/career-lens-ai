"""
CareerLens AI - Deterministic PDF Parser
Extracts layout-aware lines, font metadata, and hyperlinks without making any LLM calls.
"""

from __future__ import annotations

import io
import statistics
from typing import Any, Dict, List, Tuple
import pdfplumber

from app.models.candidate_profile import ResumeBlock
from app.parser.layout_analyzer import detect_column_split
from app.parser.block_builder import assemble_blocks_from_lines
from app.core.logger import get_logger

logger = get_logger(__name__)


def parse_pdf_to_blocks(pdf_bytes: bytes) -> Tuple[List[ResumeBlock], List[str], str, List[str]]:
    """
    Parses PDF bytes into structured ResumeBlock objects, hyperlinks, raw combined text, and header lines.
    Returns (blocks, hyperlinks, raw_text, header_lines).
    """
    extracted_hyperlinks: List[str] = []
    page_lines: List[List[Dict[str, Any]]] = []
    all_font_sizes: List[float] = []
    full_text_lines: List[str] = []
    header_lines: List[str] = []

    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            # 1. Extract hyperlinks
            for page in pdf.pages:
                if hasattr(page, "hyperlinks") and page.hyperlinks:
                    for h in page.hyperlinks:
                        uri = h.get("uri")
                        if uri:
                            extracted_hyperlinks.append(uri)

            # 2. Extract line objects
            for page_idx, page in enumerate(pdf.pages):
                split_x = detect_column_split(page)
                if split_x:
                    col1 = page.crop((0, 0, split_x, float(page.height)))
                    col2 = page.crop((split_x, 0, float(page.width), float(page.height)))
                    raw_lines = (col1.extract_text_lines(layout=False) or []) + (
                        col2.extract_text_lines(layout=False) or []
                    )
                else:
                    raw_lines = page.extract_text_lines(layout=False) or []

                current_page_items: List[Dict[str, Any]] = []
                for l in raw_lines:
                    text = l.get("text", "").strip()
                    if not text:
                        continue

                    full_text_lines.append(text)
                    if page_idx == 0 and len(header_lines) < 8:
                        header_lines.append(text)

                    chars = l.get("chars", [])
                    sizes = [float(c.get("size", 10.0)) for c in chars if c.get("size")]
                    avg_size = statistics.mean(sizes) if sizes else 10.0
                    all_font_sizes.append(avg_size)

                    is_bold = any(
                        "bold" in str(c.get("fontname", "")).lower()
                        or "black" in str(c.get("fontname", "")).lower()
                        or "cmbx" in str(c.get("fontname", "")).lower()
                        or "heavy" in str(c.get("fontname", "")).lower()
                        for c in chars
                    )

                    current_page_items.append({
                        "text": text,
                        "font_size": avg_size,
                        "is_bold": is_bold,
                        "y_pos": float(l.get("top", 0.0)),
                    })

                page_lines.append(current_page_items)

    except Exception as exc:
        logger.warning(f"pdfplumber structured extraction failed: {exc}. Using fallback text extraction.")
        return [], extracted_hyperlinks, pdf_bytes.decode("utf-8", errors="ignore"), []

    median_font = statistics.median(all_font_sizes) if all_font_sizes else 10.0
    blocks = assemble_blocks_from_lines(page_lines, median_font)
    full_text = "\n".join(full_text_lines)

    logger.info(
        f"Parsed PDF layout: blocks={len(blocks)}, text_length={len(full_text)} chars, "
        f"hyperlinks={len(extracted_hyperlinks)}, median_font={median_font:.1f}pt"
    )

    return blocks, extracted_hyperlinks, full_text, header_lines
