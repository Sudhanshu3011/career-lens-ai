"""
CareerLens AI - Dual-Gate LLM Rate Limiter & Concurrency Controller
Enforces strict 1-request-per-minute rate limiting with mutual exclusion (in_flight == 1 max)
to protect external Groq/LLM APIs from rate-limit exhaustion and concurrent queue spikes.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any, Callable, Coroutine, Optional
from app.core.logger import get_logger

logger = get_logger(__name__)


class DualGateLLMRateLimiter:
    """
    Enforces dual-gate protection for external LLM APIs:
    1. In-Flight Mutual Exclusion: Exactly 1 request in flight at any time across workers.
    2. Strict RPM Timing: Minimum interval (e.g. 60s) between request starts, plus post-completion cooldown.
    """

    def __init__(self, interval_seconds: float = 60.0, post_call_cooldown: float = 5.0) -> None:
        self.interval = float(interval_seconds)
        self.post_call_cooldown = float(post_call_cooldown)
        self.last_start_timestamp: float = 0.0
        self.last_complete_timestamp: float = 0.0
        self._in_flight: int = 0
        self._waiting_count: int = 0
        self._mutex = asyncio.Lock()

    @property
    def in_flight(self) -> int:
        """Returns the number of requests currently executing."""
        return self._in_flight

    @property
    def waiting_count(self) -> int:
        """Returns the number of tasks waiting in queue for the LLM."""
        return self._waiting_count

    async def execute(
        self,
        coro_func: Callable[..., Coroutine[Any, Any, Any]],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Executes an async LLM function with strict exclusivity and rate pacing.
        Guarantees that even if an LLM call takes > 60 seconds, no other call runs concurrently.
        """
        self._waiting_count += 1
        logger.info(
            "DualGateRateLimiter: Task enqueued. Waiting in queue: %d, in-flight: %d",
            self._waiting_count,
            self._in_flight,
        )

        async with self._mutex:
            self._waiting_count -= 1
            now = time.monotonic()

            # 1. Enforce cooldown and interval spacing
            time_since_start = now - self.last_start_timestamp
            time_since_complete = now - self.last_complete_timestamp

            wait_for_interval = max(0.0, self.interval - time_since_start)
            wait_for_cooldown = max(0.0, self.post_call_cooldown - time_since_complete)
            wait_time = max(wait_for_interval, wait_for_cooldown)

            if wait_time > 0 and self.last_start_timestamp > 0:
                logger.info(
                    "DualGateRateLimiter: Cooldown active. Waiting %.2fs before launching LLM call...",
                    wait_time,
                )
                await asyncio.sleep(wait_time)

            # 2. Mark in-flight active
            self._in_flight = 1
            self.last_start_timestamp = time.monotonic()
            logger.info("DualGateRateLimiter: LLM call started (in_flight=1).")

            try:
                # 3. Execute the LLM call
                result = await coro_func(*args, **kwargs)
                return result
            finally:
                # 4. Mark completion and clear in-flight
                self._in_flight = 0
                self.last_complete_timestamp = time.monotonic()
                elapsed = self.last_complete_timestamp - self.last_start_timestamp
                logger.info(
                    "DualGateRateLimiter: LLM call completed in %.2fs (in_flight=0).",
                    elapsed,
                )


# Global singleton: 1 request/min with 5s post-call cooldown
groq_rate_limiter = DualGateLLMRateLimiter(interval_seconds=60.0, post_call_cooldown=5.0)
