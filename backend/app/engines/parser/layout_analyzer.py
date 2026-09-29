"""
CareerLens AI - PDF Spatial & Layout Analyzer
Detects multi-column splits, header typography, and line font metrics.
"""

from __future__ import annotations

import statistics
from typing import Any, Dict, List, Optional, Tuple
from app.core.logger import get_logger

logger = get_logger(__name__)


def detect_column_split(page: Any) -> Optional[float]:
    """
    Detects if a PDF page has a two-column layout by finding a vertical gutter
    between 30% and 75% width where few or no words cross, and both sides have content.
    Returns the x-coordinate split point, or None if single column.
    """
    try:
        words = page.extract_words()
        if not words or len(words) < 40:
            return None

        width = float(page.width)
        min_x = width * 0.30
        max_x = width * 0.75

        best_split = None
        min_crossings = 9999
        step = 5.0
        curr_x = min_x

        while curr_x <= max_x:
            left_words = [w for w in words if w["x1"] <= curr_x]
            right_words = [w for w in words if w["x0"] >= curr_x]
            crossing_words = [w for w in words if w["x0"] < curr_x < w["x1"]]

            if len(left_words) >= 20 and len(right_words) >= 20:
                if len(crossing_words) < min_crossings:
                    min_crossings = len(crossing_words)
                    best_split = curr_x
            curr_x += step

        if best_split is not None and min_crossings <= 1:
            return best_split
    except Exception as exc:
        logger.debug(f"detect_column_split exception: {exc}")
    return None


def calculate_line_font_metrics(lines: List[Dict[str, Any]]) -> Tuple[float, float]:
    """
    Calculates median line font size and max font size across extracted line objects.
    """
    all_sizes: List[float] = []
    for l in lines:
        chars = l.get("chars", [])
        sizes = [float(c.get("size", 10.0)) for c in chars if c.get("size")]
        if sizes:
            all_sizes.append(statistics.mean(sizes))

    if not all_sizes:
        return 10.0, 10.0

    return statistics.median(all_sizes), max(all_sizes)
