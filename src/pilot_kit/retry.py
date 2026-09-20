"""Retry a chat model call when the backend fails transiently.

`ChatNVIDIA` has no retry setting, and wrapping it in `with_retry()` would stop it being a chat
model that agents can bind tools to. So the retry wraps the model *call*: in a graph node, or in an
agent middleware's `awrap_model_call`. Never wrap a whole graph or agent run with it: a replay would
call, and possibly bill, your other services again.

Pass `never_retry` exception types for anything that already retries itself (for example a vendor
SDK) or that must not be repeated.
"""

from __future__ import annotations

import asyncio
import re
from collections.abc import Awaitable, Callable

import aiohttp
import requests

TRANSIENT = (
    ConnectionError,
    TimeoutError,
    aiohttp.ClientError,
    requests.exceptions.ConnectionError,
    requests.exceptions.Timeout,
)
RETRYABLE_HTTP_STATUS = frozenset({429, 500, 502, 503, 504})
# langchain-nvidia-ai-endpoints raises HTTP failures as a plain Exception("[503] ...").
_NIM_HTTP_TRANSIENT = re.compile(r"^\[(429|500|502|503|504)\]")


def is_transient(exc: Exception, never_retry: tuple[type[Exception], ...] = ()) -> bool:
    if never_retry and isinstance(exc, never_retry):
        return False
    if isinstance(exc, aiohttp.ClientResponseError):
        # A 401, 403 or 404 will not fix itself, so do not wait and retry it.
        return exc.status in RETRYABLE_HTTP_STATUS
    if isinstance(exc, TRANSIENT):
        return True
    return type(exc) is Exception and bool(_NIM_HTTP_TRANSIENT.match(str(exc)))


async def with_retries[T](
    call: Callable[[], Awaitable[T]],
    *,
    attempts: int = 3,
    delay: float = 5.0,
    on_retry: Callable[[int, Exception], None] | None = None,
    never_retry: tuple[type[Exception], ...] = (),
) -> T:
    for attempt in range(1, attempts + 1):
        try:
            return await call()
        except Exception as exc:
            if attempt == attempts or not is_transient(exc, never_retry):
                raise
            if on_retry:
                on_retry(attempt, exc)
            await asyncio.sleep(delay)
    raise AssertionError("unreachable")
