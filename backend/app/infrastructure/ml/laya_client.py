"""
CareerLens AI - Laya Model Client

Manages runtime connection to ConvAI Innovations' Laya non-autoregressive decision model.
Enforces PyTorch CPU thread capping (torch.set_num_threads=2) to prevent container CPU spikes.
"""

from __future__ import annotations

import os
import time
from typing import Any, Dict, Optional, Tuple
from app.core.logger import get_logger
from app.infrastructure.telemetry.laya_telemetry import LayaTelemetry

logger = get_logger(__name__)

# Ensure PyTorch CPU threads are capped to prevent CPU starvation
try:
    import torch

    if torch.get_num_threads() > 2:
        torch.set_num_threads(2)
    if hasattr(torch, "set_num_interop_threads"):
        try:
            torch.set_num_interop_threads(2)
        except RuntimeError:
            pass
except Exception:
    pass

try:
    import laya

    _LAYA_AVAILABLE = True
except ImportError:
    _LAYA_AVAILABLE = False
    logger.warning(
        "Laya library not installed. ML inference will use calibrated fallback."
    )


class LayaClient:
    """Singleton wrapper for ConvAI Innovations Laya Router."""

    _instance: Optional["LayaClient"] = None

    def __init__(self) -> None:
        self.router: Any = None
        self._init_router()

    def _init_router(self) -> None:
        if not _LAYA_AVAILABLE:
            return

        try:
            from app.core.config import settings

            hf_token = (
                os.environ.get("HF_TOKEN")
                or os.environ.get("HUGGING_FACE_HUB_TOKEN")
                or getattr(settings, "HF_TOKEN", "")
            )
            if hf_token:
                os.environ["HF_TOKEN"] = hf_token
                os.environ["HUGGING_FACE_HUB_TOKEN"] = hf_token

            hf_offline = os.environ.get("HF_HUB_OFFLINE")
            if hf_offline is None:
                os.environ["HF_HUB_OFFLINE"] = str(
                    getattr(settings, "HF_HUB_OFFLINE", 0)
                )

            self.router = laya.Router(token=hf_token or None, preload=False)
            logger.info("LayaClient initialized successfully with HF auth token")
        except Exception as exc:
            logger.warning(
                f"Failed to initialize Laya Router in LayaClient: {exc}. Using fallback."
            )
            self.router = None

    @classmethod
    def get_instance(cls) -> "LayaClient":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def is_available(self) -> bool:
        return self.router is not None

    def predict(
        self,
        prompt_text: str,
        questions: Dict[str, Any],
    ) -> Tuple[Dict[str, Any], LayaTelemetry]:
        """
        Executes non-autoregressive forward pass with telemetry logging.
        Returns (raw_answers, telemetry_object).
        """
        if self.router is None:
            raise RuntimeError("Laya Router is not initialized or unavailable.")

        start_time = time.perf_counter()
        result = self.router.predict({"text": prompt_text}, questions)
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        answers = result.get("answers", {})
        telemetry = LayaTelemetry(
            prompt_context=prompt_text,
            questions=questions,
            raw_model_answers=answers,
            model_name="convaiinnovations/laya",
            latency_ms=round(elapsed_ms, 2),
            metadata={
                "routing": result.get("routing"),
                "usage": result.get("usage"),
            },
        )
        return answers, telemetry


laya_client = LayaClient.get_instance()
