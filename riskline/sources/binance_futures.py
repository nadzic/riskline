from __future__ import annotations

from riskline.config import HttpConfig
from riskline.http import get_json


BINANCE_FUTURES_PREMIUM_INDEX_URL = "https://fapi.binance.com/fapi/v1/premiumIndex"
BINANCE_FUTURES_OI_URL = "https://fapi.binance.com/fapi/v1/openInterest"
BINANCE_FUTURES_FORCE_ORDERS_URL = "https://fapi.binance.com/fapi/v1/forceOrders"


def _classify_liquidation_proxy(order_count: int) -> str:
    if order_count >= 20:
        return "High"
    if order_count >= 8:
        return "Medium"
    return "Low"


def fetch_futures_snapshot(
    *,
    symbol: str = "BTCUSDT",
    http: HttpConfig,
    include_liquidations_proxy: bool = False,
) -> dict:
    premium = get_json(
        BINANCE_FUTURES_PREMIUM_INDEX_URL,
        params={"symbol": symbol},
        timeout_seconds=http.timeout_seconds,
        max_retries=http.max_retries,
        backoff_seconds=http.backoff_seconds,
    )
    oi = get_json(
        BINANCE_FUTURES_OI_URL,
        params={"symbol": symbol},
        timeout_seconds=http.timeout_seconds,
        max_retries=http.max_retries,
        backoff_seconds=http.backoff_seconds,
    )

    funding_rate = float(premium["lastFundingRate"])
    open_interest = float(oi["openInterest"])
    mark_price = float(premium["markPrice"]) if "markPrice" in premium else None

    liquidations_proxy = None
    if include_liquidations_proxy:
        force_orders = get_json(
            BINANCE_FUTURES_FORCE_ORDERS_URL,
            params={"symbol": symbol, "limit": 50},
            timeout_seconds=http.timeout_seconds,
            max_retries=http.max_retries,
            backoff_seconds=http.backoff_seconds,
        )
        liquidations_proxy = _classify_liquidation_proxy(len(force_orders))

    return {
        "funding_rate": funding_rate,
        "open_interest": open_interest,
        "mark_price": mark_price,
        "liquidations_proxy": liquidations_proxy,
    }
