from __future__ import annotations

import time
from typing import Any

import requests


class HttpRequestError(RuntimeError):
    """Raised when an HTTP call cannot be completed successfully."""


def get_json(
    url: str,
    *,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout_seconds: int = 12,
    max_retries: int = 3,
    backoff_seconds: float = 1.0,
) -> Any:
    last_error: Exception | None = None
    attempts = max(1, max_retries + 1)

    for attempt in range(attempts):
        try:
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=timeout_seconds,
            )
            should_retry = response.status_code == 429 or response.status_code >= 500
            if should_retry and attempt < attempts - 1:
                sleep_seconds = backoff_seconds * (2**attempt)
                time.sleep(sleep_seconds)
                continue

            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as exc:
            last_error = exc
            if attempt < attempts - 1:
                sleep_seconds = backoff_seconds * (2**attempt)
                time.sleep(sleep_seconds)
                continue
            break

    raise HttpRequestError(f"HTTP request failed for {url}: {last_error}")
