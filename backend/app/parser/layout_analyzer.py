"""
CareerLens AI - PDF Spatial & Layout Analyzer
Detects multi-column splits, header typography, and line font metrics.
"""

from __future__ import annotations

import statistics
from typing import Any, Dict, List, Optional, Tuple
import pdfplumber


def detect_column_split(page: Any) -> Optional[float]:
    """
    Detects two-column layouts by finding a central vertical gap with zero text.
    Returns x-coordinate of split if detected, else None.
    """
    words = page.extract_words()
    if not words or len(words) < 30:
        return None

    page_width = float(page.width)
    mid_min = page_width * 0.35
    mid_max = page_width * 0.65

    bins = [0] * int(page_width)
    for w in words:
        x0 = max(0, int(w["x0"]))
        x1 = min(int(page_width) - 1, int(w["x1"]))
        for x in range(x0, x1 + 1):
            bins[x] += 1

    min_gap_width = 15
    current_gap = 0
    best_gap_start = 0
    best_gap_width = 0

    for x in range(int(mid_min), int(mid_max)):
        if bins[x] == 0:
            if current_gap == 0:
                best_gap_start = x
            current_gap += 1
            if current_gap > best_gap_width:
                best_gap_width = current_gap
        else:
            current_gap = 0

    if best_gap_width >= min_gap_width:
        return float(best_gap_start + best_gap_width / 2)

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
