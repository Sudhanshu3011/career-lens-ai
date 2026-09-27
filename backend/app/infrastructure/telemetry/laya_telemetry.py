"""
CareerLens AI - Laya Telemetry Pipeline

Captures and formats transparent inference telemetry:
- Exact prompt text payload sent to Laya
- Exact questions, instructions, and criteria evaluated
- Raw probability distributions and model confidence
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional


@dataclass
class LayaTelemetry:
    """Telemetry envelope for a single candidate's Laya inference cycle."""

    prompt_context: str
    questions: Dict[str, Any]
    raw_model_answers: Dict[str, Any]
    model_name: str = "convaiinnovations/laya"
    latency_ms: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes telemetry record to JSON-safe dictionary."""
        return asdict(self)
