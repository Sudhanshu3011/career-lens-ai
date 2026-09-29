"""
CareerLens AI - Layout and PDF Parsing Package
"""

from app.engines.parser.pdf_parser import parse_pdf_to_blocks, extract_text
from app.engines.parser.layout_analyzer import (
    detect_column_split,
    calculate_line_font_metrics,
)
from app.engines.parser.block_builder import (
    classify_section_header,
    assemble_blocks_from_lines,
    SECTION_TAXONOMY,
)

__all__ = [
    "parse_pdf_to_blocks",
    "extract_text",
    "detect_column_split",
    "calculate_line_font_metrics",
    "classify_section_header",
    "assemble_blocks_from_lines",
    "SECTION_TAXONOMY",
]
