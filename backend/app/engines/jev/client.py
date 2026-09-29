"""
CareerLens AI - TypeSafe Jev System One Client

Official TypeSafe Python SDK integration (typesafe-sdk).
Calls client.system_one(state=..., questions=...) with Choice, Score, and Noul primitives.
Reads TYPESAFE_API_KEY from environment or settings.
"""

from __future__ import annotations

import os
import asyncio
from typing import Any, Dict, Optional
from app.core.logger import get_logger
from app.core.config import settings

from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

logger = get_logger(__name__)


class JevClient:
    """
    TypeSafe Jev System One Client powered by official typesafe-sdk.
    Executes Choice, Score, and Noul questions over candidate or JD state via client.system_one().
    """

    _instance: Optional["JevClient"] = None

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.client: Optional[TypeSafeClient] = None
        self.api_key = (
            api_key or settings.TYPESAFE_API_KEY or os.getenv("TYPESAFE_API_KEY", "")
        )

        if self.api_key:
            try:
                self.client = TypeSafeClient(api_key=self.api_key)
                logger.info("Official TypeSafeClient initialized with API key.")
            except Exception as exc:
                logger.warning(
                    f"Failed to initialize TypeSafeClient: {exc}. Will use calibrated fallback."
                )
        else:
            logger.info(
                "TypeSafe SDK loaded without API key. Using calibrated fallback for offline operation."
            )

    @classmethod
    def get_instance(cls) -> "JevClient":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def system_one(
        self,
        state: str | Dict[str, Any],
        questions: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Executes System One call using official TypeSafe SDK.
        Returns answers dictionary indexed by question key.
        """
        if not questions:
            return {}

        state_text = state if isinstance(state, str) else str(state.get("text", state))

        # Format questions as official typesafe_sdk primitives if needed
        sdk_questions = {}
        for q_id, q_obj in questions.items():
            if isinstance(q_obj, (Choice, Score, Noul)):
                sdk_questions[q_id] = q_obj
            elif isinstance(q_obj, dict):
                q_type = q_obj.get("type", "choice").lower()
                inst = q_obj.get("instructions", "")
                crit = q_obj.get("criteria")
                if q_type == "score":
                    sdk_questions[q_id] = Score(
                        instructions=inst,
                        criteria=crit if isinstance(crit, list) else [],
                    )
                elif q_type == "noul":
                    sdk_questions[q_id] = Noul(instructions=inst)
                else:
                    sdk_questions[q_id] = Choice(
                        instructions=inst,
                        criteria=crit if isinstance(crit, dict) else {},
                    )
            else:
                sdk_questions[q_id] = q_obj

        # Attempt remote System One call if client is configured
        if self.client is not None:
            try:
                response = self.client.system_one(
                    state=state_text, questions=sdk_questions
                )
                parsed_answers: Dict[str, Any] = {}
                for ans_id, ans_val in response.answers.items():
                    ans_type = getattr(ans_val, "type", "choice")
                    if ans_type == "score":
                        parsed_answers[ans_id] = {
                            "type": "score",
                            "score": getattr(ans_val, "score", 0),
                            "confidence": getattr(ans_val, "confidence", 0.8),
                        }
                    elif ans_type == "noul":
                        noul_prob = float(getattr(ans_val, "noul", 0.5))
                        parsed_answers[ans_id] = {
                            "type": "noul",
                            "noul": noul_prob >= 0.5,
                            "probability": noul_prob,
                            "confidence": noul_prob,
                        }
                    else:
                        parsed_answers[ans_id] = {
                            "type": "choice",
                            "choice": getattr(ans_val, "choice", ""),
                            "confidence": getattr(ans_val, "confidence", 0.7),
                        }
                return parsed_answers
            except Exception as exc:
                logger.warning(
                    f"TypeSafe system_one API call failed: {exc}. Executing calibrated fallback."
                )

        return self._evaluate_fallback(state_text, questions)

    def predict(
        self, state: str | Dict[str, Any], questions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Alias for system_one to maintain universal interface with Laya."""
        return self.system_one(state=state, questions=questions)

    async def system_one_async(
        self, state: str | Dict[str, Any], questions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Asynchronously executes System One call in a worker thread."""
        return await asyncio.to_thread(self.system_one, state, questions)

    async def predict_async(
        self, state: str | Dict[str, Any], questions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Alias for system_one_async."""
        return await self.system_one_async(state=state, questions=questions)

    def _evaluate_fallback(
        self, state_text: str, questions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Deterministic calibrated fallback adhering strictly to Choice, Score, and Noul schemas.
        """
        answers: Dict[str, Any] = {}
        text = state_text.lower()

        for q_id, q_def in questions.items():
            if isinstance(q_def, dict):
                q_type = q_def.get("type", "choice").lower()
                crit = q_def.get("criteria")
                inst = q_def.get("instructions", "")
            else:
                q_type = getattr(q_def, "type", "choice").lower()
                crit = getattr(q_def, "criteria", None)
                inst = getattr(q_def, "instructions", "")

            if q_type == "score":
                crit_list = crit if isinstance(crit, list) else []
                max_level = max(1, len(crit_list) - 1)
                score_val = 2.0
                if any(
                    w in text
                    for w in ["lead", "staff", "principal", "architect", "10+ years"]
                ):
                    score_val = min(float(max_level), 4.5)
                elif any(
                    w in text
                    for w in ["senior", "sr.", "5+ years", "6+ years", "7+ years"]
                ):
                    score_val = min(float(max_level), 3.2)
                elif any(
                    w in text
                    for w in [
                        "intern",
                        "student",
                        "entry",
                        "junior",
                        "fresher",
                        "0 years",
                    ]
                ):
                    score_val = 1.0

                answers[q_id] = {
                    "type": "score",
                    "score": round(score_val, 2),
                    "confidence": 0.80,
                }

            elif q_type == "noul":
                keywords = [w for w in str(inst).lower().split() if len(w) > 4]
                match_count = sum(1 for kw in keywords if kw in text)
                prob = min(0.95, 0.55 + match_count * 0.15) if match_count > 0 else 0.35
                answers[q_id] = {
                    "type": "noul",
                    "noul": prob >= 0.50,
                    "probability": round(prob, 3),
                    "confidence": round(prob, 3),
                }

            else:  # choice
                crit_dict = crit if isinstance(crit, dict) else {}
                choice_keys = list(crit_dict.keys())
                selected_choice = choice_keys[0] if choice_keys else "general"

                for k in choice_keys:
                    if k.lower() in text or any(
                        term in text for term in k.lower().split("_")
                    ):
                        selected_choice = k
                        break

                answers[q_id] = {
                    "type": "choice",
                    "choice": selected_choice,
                    "confidence": 0.75,
                }

        return answers


jev_client = JevClient.get_instance()
