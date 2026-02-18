import responses

from riskline.config import HttpConfig
from riskline.sources.binance_futures import fetch_futures_snapshot
from riskline.sources.binance_spot import fetch_daily_klines
from riskline.sources.cmc_fear_greed import fetch_fear_greed


@responses.activate
def test_fetch_fear_greed_parses_payload() -> None:
    responses.get(
        "https://pro-api.coinmarketcap.com/v3/fear-and-greed/latest",
        json={"data": {"value": 12, "value_classification": "Extreme Fear"}},
        status=200,
    )
    data = fetch_fear_greed(
        api_key="test-key",
        http=HttpConfig(timeout_seconds=1, max_retries=0, backoff_seconds=0),
    )
    assert data["value"] == 12
    assert data["label"] == "Extreme Fear"


@responses.activate
def test_fetch_daily_klines_parses_close_series() -> None:
    responses.get(
        "https://api.binance.com/api/v3/klines",
        json=[
            [0, "1", "1", "1", "100", "0"],
            [0, "1", "1", "1", "101", "0"],
        ],
        status=200,
    )
    closes = fetch_daily_klines(
        symbol="BTCUSDT",
        http=HttpConfig(timeout_seconds=1, max_retries=0, backoff_seconds=0),
    )
    assert closes == [100.0, 101.0]


@responses.activate
def test_fetch_futures_snapshot_parses_payloads() -> None:
    responses.get(
        "https://fapi.binance.com/fapi/v1/premiumIndex",
        json={"lastFundingRate": "-0.0002", "markPrice": "70000"},
        status=200,
    )
    responses.get(
        "https://fapi.binance.com/fapi/v1/openInterest",
        json={"openInterest": "12345"},
        status=200,
    )
    responses.get(
        "https://fapi.binance.com/fapi/v1/forceOrders",
        json=[{"id": 1}] * 25,
        status=200,
    )
    snapshot = fetch_futures_snapshot(
        symbol="BTCUSDT",
        http=HttpConfig(timeout_seconds=1, max_retries=0, backoff_seconds=0),
        include_liquidations_proxy=True,
    )
    assert snapshot["funding_rate"] == -0.0002
    assert snapshot["open_interest"] == 12345.0
    assert snapshot["liquidations_proxy"] == "High"
