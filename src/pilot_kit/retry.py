"""Retry a chat model call when the backend fails transiently. This module is the only retry owner.

One logical model call gets at most `DEFAULT_ATTEMPTS` tries (the first call plus two retries) on
every provider. Provider SDK retries are switched off (`max_retries=0` for the ChatGPT provider, and
`ChatNVIDIA` has none), so the attempt count is the same for `openai` and `nim` and every retry is
visible here. Do not turn a vendor retry back on: the two layers would multiply.

Waits grow exponentially with jitter, capped at `max_delay`. A `Retry-After` header on the error
(seconds or an HTTP date) sets the wait instead, also capped. Each retry is reported to `on_retry`
and logged on the `pilot_kit.retry` logger with the error type and status only, never the message.

`ChatNVIDIA` has no retry setting, and wrapping it in `with_retry()` would stop it being a chat
model that agents can bind tools to. So the retry wraps the model *call*: in a graph node, or in an
agent middleware's `awrap_model_call`. Never wrap a whole graph or agent run with it: a replay would
call, and possibly bill, your other services again.

Pass `never_retry` exception types for anything that must not be repeated.
"""

from __future__ import annotations

import asyncio
import logging
import random
import re
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime

import aiohttp
import openai
import requests

logger = logging.getLogger(__name__)

DEFAULT_ATTEMPTS = 3
DEFAULT_DELAY = 5.0
DEFAULT_MAX_DELAY = 60.0

TRANSIENT = (
    ConnectionError,
    TimeoutError,
    aiohttp.ClientError,
    openai.APIConnectionError,  # includes APITimeoutError
    requests.exceptions.ConnectionError,
    requests.exceptions.Timeout,
)
RETRYABLE_HTTP_STATUS = frozenset({429, 500, 502, 503, 504})
# A 429 with one of these codes means the plan or quota is used up. Waiting will not fix it.
PERMANENT_ERROR_CODES = frozenset({"usage_limit_reached", "insufficient_quota"})
# langchain-nvidia-ai-endpoints raises HTTP failures as a plain Exception("[503] ...").
_NIM_HTTP_TRANSIENT = re.compile(r"^\[(429|500|502|503|504)\]")


def is_transient(exc: Exception, never_retry: tuple[type[Exception], ...] = ()) -> bool:
    if never_retry and isinstance(exc, never_retry):
        return False
    if isinstance(exc, aiohttp.ClientResponseError):
        # A 401, 403 or 404 will not fix itself, so do not wait and retry it.
        return exc.status in RETRYABLE_HTTP_STATUS
    if isinstance(exc, openai.APIStatusError):
        return exc.status_code in RETRYABLE_HTTP_STATUS and exc.code not in PERMANENT_ERROR_CODES
    if isinstance(exc, TRANSIENT):
        return True
    return type(exc) is Exception and bool(_NIM_HTTP_TRANSIENT.match(str(exc)))


def http_status(exc: Exception) -> int | None:
    status = getattr(exc, "status_code", None) or getattr(exc, "status", None)
    return status if isinstance(status, int) else None


def retry_after(exc: Exception) -> float | None:
    """Seconds the server asked us to wait, from a `Retry-After` header on the error, if any."""
    response = getattr(exc, "response", None)
    headers = getattr(response, "headers", None) or getattr(exc, "headers", None)
    value = headers.get("retry-after") if headers else None
    if not value:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        pass
    try:
        when = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=UTC)
    return max(0.0, (when - datetime.now(UTC)).total_seconds())


def backoff(attempt: int, *, delay: float, max_delay: float) -> float:
    """Exponential backoff with equal jitter: half the step is fixed, half is random."""
    step = min(max_delay, delay * 2 ** (attempt - 1))
    return step / 2 + random.uniform(0, step / 2)


async def with_retries[T](
    call: Callable[[], Awaitable[T]],
    *,
    attempts: int = DEFAULT_ATTEMPTS,
    delay: float = DEFAULT_DELAY,
    max_delay: float = DEFAULT_MAX_DELAY,
    on_retry: Callable[[int, Exception], None] | None = None,
    never_retry: tuple[type[Exception], ...] = (),
) -> T:
    for attempt in range(1, attempts + 1):
        try:
            return await call()
        except Exception as exc:
            if attempt == attempts or not is_transient(exc, never_retry):
                raise
            asked = retry_after(exc)
            wait = (
                min(max_delay, asked)
                if asked is not None
                else backoff(attempt, delay=delay, max_delay=max_delay)
            )
            logger.warning(
                "retry %d of %d in %.1fs after %s%s",
                attempt,
                attempts - 1,
                wait,
                type(exc).__name__,
                f" (HTTP {status})" if (status := http_status(exc)) else "",
            )
            if on_retry:
                on_retry(attempt, exc)
            await asyncio.sleep(wait)
    raise AssertionError("unreachable")
