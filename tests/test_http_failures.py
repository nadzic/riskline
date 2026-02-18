import pytest
import responses

from riskline.http import HttpRequestError, get_json


@responses.activate
def test_get_json_retries_429_then_succeeds() -> None:
    url = "https://example.test/retry"
    responses.get(url, status=429)
    responses.get(url, json={"ok": True}, status=200)

    payload = get_json(
        url,
        timeout_seconds=1,
        max_retries=1,
        backoff_seconds=0.0,
    )
    assert payload == {"ok": True}


@responses.activate
def test_get_json_raises_after_retry_exhausted() -> None:
    url = "https://example.test/fail"
    responses.get(url, status=500)
    responses.get(url, status=500)

    with pytest.raises(HttpRequestError):
        get_json(
            url,
            timeout_seconds=1,
            max_retries=1,
            backoff_seconds=0.0,
        )
