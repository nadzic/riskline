from __future__ import annotations

from riskline.config import HttpConfig
from riskline.http import get_json


BINANCE_SPOT_KLINES_URL = "https://api.binance.com/api/v3/klines"


def fetch_daily_klines(
    *,
    symbol: str = "BTCUSDT",
    limit: int = 300,
    http: HttpConfig,
) -> list[float]:
    payload = get_json(
        BINANCE_SPOT_KLINES_URL,
        params={"symbol": symbol, "interval": "1d", "limit": limit},
        timeout_seconds=http.timeout_seconds,
        max_retries=http.max_retries,
        backoff_seconds=http.backoff_seconds,
    )
    closes: list[float] = []
    for row in payload:
        # Binance kline format: [open_time, open, high, low, close, ...]
        closes.append(float(row[4]))
    if not closes:
        raise ValueError("No daily closes returned from Binance spot klines")
    return closes
