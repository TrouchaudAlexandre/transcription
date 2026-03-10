from __future__ import annotations

import time
from typing import Callable, TypeVar


ResultT = TypeVar("ResultT")


def execute_with_retry(
    operation: Callable[[], ResultT],
    max_retries: int,
    base_delay_seconds: float,
    is_retryable: Callable[[Exception], bool],
) -> ResultT:
    effective_max_retries = max(0, max_retries)
    effective_base_delay = max(0.0, base_delay_seconds)

    for attempt in range(effective_max_retries + 1):
        try:
            return operation()
        except Exception as exc:
            if not is_retryable(exc) or attempt >= effective_max_retries:
                raise
            time.sleep(effective_base_delay * (2**attempt))

    raise RuntimeError("Retry loop exited unexpectedly")


def is_retryable_http_error(exc: Exception) -> bool:
    status_code = getattr(exc, "status_code", None)
    if status_code is None:
        status_code = getattr(exc, "status", None)
    if status_code in (408, 409, 429):
        return True
    if isinstance(status_code, int) and status_code >= 500:
        return True

    message = str(exc).lower()
    retryable_markers = (
        "timeout",
        "temporarily unavailable",
        "connection",
        "rate limit",
        "server error",
        "resource exhausted",
        "unavailable",
    )
    return any(marker in message for marker in retryable_markers)
