"""
CareerLens AI - Speculative Evaluation and Multiplier Package
"""

from app.engines.evaluation.speculative_fanout import (
    DEFAULT_MULTIPLIERS,
    SpeculativeFanoutEvaluator,
    speculative_evaluator,
)

SpeculativeEvaluator = SpeculativeFanoutEvaluator

__all__ = [
    "SpeculativeFanoutEvaluator",
    "SpeculativeEvaluator",
    "speculative_evaluator",
    "DEFAULT_MULTIPLIERS",
]
