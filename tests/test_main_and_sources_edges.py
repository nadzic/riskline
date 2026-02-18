import pytest
import responses

import main as app_main
from riskline.config import ConfigError, HttpConfig
from riskline.sources.binance_futures import fetch_futures_snapshot
from riskline.sources.binance_spot import fetch_daily_klines
from riskline.sources.cmc_fear_greed import fetch_fear_greed


def test_main_exits_with_code_2_on_config_error(monkeypatch) -> None:
    monkeypatch.setattr(app_main, "run_once", lambda: (_ for _ in ()).throw(ConfigError("bad cfg")))
    with pytest.raises(SystemExit) as exc:
        app_main.main()
    assert exc.value.code == 2


def test_main_exits_with_code_1_on_unexpected_error(monkeypatch) -> None:
    monkeypatch.setattr(app_main, "run_once", lambda: (_ for _ in ()).throw(RuntimeError("boom")))
    with pytest.raises(SystemExit) as exc:
        app_main.main()
    assert exc.value.code == 1


@responses.activate
def test_fetch_fear_greed_raises_when_value_missing() -> None:
    responses.get(
        "https://pro-api.coinmarketcap.com/v3/fear-and-greed/latest",
        json={"data": {"value_classification": "Fear"}},
        status=200,
    )
    with pytest.raises(ValueError, match="missing value"):
        fetch_fear_greed(
            api_key="k",
            http=HttpConfig(timeout_seconds=1, max_retries=0, backoff_seconds=0.0),
        )


@responses.activate
def test_fetch_daily_klines_raises_when_empty_payload() -> None:
    responses.get(
        "https://api.binance.com/api/v3/klines",
        json=[],
        status=200,
    )
    with pytest.raises(ValueError, match="No daily closes"):
        fetch_daily_klines(
            symbol="BTCUSDT",
            http=HttpConfig(timeout_seconds=1, max_retries=0, backoff_seconds=0.0),
        )


@responses.activate
def test_fetch_futures_snapshot_without_mark_price_and_force_orders_medium() -> None:
    responses.get(
        "https://fapi.binance.com/fapi/v1/premiumIndex",
        json={"lastFundingRate": "0.0001"},
        status=200,
    )
    responses.get(
        "https://fapi.binance.com/fapi/v1/openInterest",
        json={"openInterest": "10"},
        status=200,
    )
    responses.get(
        "https://fapi.binance.com/fapi/v1/forceOrders",
        json=[{"id": 1}] * 10,
        status=200,
    )

    snapshot = fetch_futures_snapshot(
        symbol="BTCUSDT",
        http=HttpConfig(timeout_seconds=1, max_retries=0, backoff_seconds=0.0),
        include_liquidations_proxy=True,
    )
    assert snapshot["mark_price"] is None
    assert snapshot["liquidations_proxy"] == "Medium"


@responses.activate
def test_fetch_futures_snapshot_force_orders_low_classification() -> None:
    responses.get(
        "https://fapi.binance.com/fapi/v1/premiumIndex",
        json={"lastFundingRate": "0.0001", "markPrice": "1"},
        status=200,
    )
    responses.get(
        "https://fapi.binance.com/fapi/v1/openInterest",
        json={"openInterest": "10"},
        status=200,
    )
    responses.get(
        "https://fapi.binance.com/fapi/v1/forceOrders",
        json=[{"id": 1}] * 2,
        status=200,
    )

    snapshot = fetch_futures_snapshot(
        symbol="BTCUSDT",
        http=HttpConfig(timeout_seconds=1, max_retries=0, backoff_seconds=0.0),
        include_liquidations_proxy=True,
    )
    assert snapshot["liquidations_proxy"] == "Low"
