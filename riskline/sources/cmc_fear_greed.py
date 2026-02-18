from __future__ import annotations

from riskline.config import HttpConfig
from riskline.http import get_json


CMC_FNG_URL = "https://pro-api.coinmarketcap.com/v3/fear-and-greed/latest"


def fetch_fear_greed(*, api_key: str, http: HttpConfig) -> dict:
    payload = get_json(
        CMC_FNG_URL,
        headers={"X-CMC_PRO_API_KEY": api_key},
        timeout_seconds=http.timeout_seconds,
        max_retries=http.max_retries,
        backoff_seconds=http.backoff_seconds,
    )
    data = payload.get("data", {})
    value = data.get("value")
    label = data.get("value_classification") or data.get("label") or "Unknown"
    timestamp = data.get("update_time") or data.get("timestamp")

    if value is None:
        raise ValueError("CoinMarketCap fear & greed payload missing value")

    return {
        "value": int(value),
        "label": str(label),
        "timestamp": timestamp,
    }
