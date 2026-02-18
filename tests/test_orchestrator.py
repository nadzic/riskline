from pathlib import Path

import main as app_main
from riskline.config import AppConfig, HttpConfig, Symbols, Thresholds
from riskline.state import load_state


def _config(state_path: Path) -> AppConfig:
    return AppConfig(
        poll_interval_minutes=30,
        alert_cooldown_hours=6,
        state_file=str(state_path),
        thresholds=Thresholds(
            fear_greed_buy=20,
            fear_greed_sell=70,
            funding_short_crowded=-0.0001,
            funding_long_crowded=0.0001,
            trend_risk_off_pct=-1.0,
            oi_deleveraging_pct=-2.0,
            oi_leverage_build_pct=2.0,
            high_volatility_pct=3.0,
        ),
        symbols=Symbols(futures="BTCUSDT", spot="BTCUSDT"),
        http=HttpConfig(timeout_seconds=1, max_retries=0, backoff_seconds=0.0),
        cmc_api_key="x",
        telegram_bot_token="y",
        telegram_chat_id="z",
        dry_run=False,
        enable_liquidations_proxy=False,
    )


def test_run_once_end_to_end_with_mocks(tmp_path, monkeypatch) -> None:
    state_path = tmp_path / "state.json"
    monkeypatch.setattr(app_main, "load_config", lambda: _config(state_path))
    monkeypatch.setattr(
        app_main,
        "fetch_fear_greed",
        lambda **kwargs: {"value": 10, "label": "Extreme Fear"},
    )
    monkeypatch.setattr(
        app_main,
        "fetch_futures_snapshot",
        lambda **kwargs: {
            "funding_rate": -0.0002,
            "open_interest": 1000.0,
            "mark_price": 70000.0,
            "liquidations_proxy": None,
        },
    )
    monkeypatch.setattr(
        app_main,
        "fetch_daily_klines",
        lambda **kwargs: [100.0] * 250,
    )

    calls = {"sent": 0}

    def _fake_send(**kwargs) -> None:
        calls["sent"] += 1
        assert "RISKLINE ALERT" in kwargs["text"]

    monkeypatch.setattr(app_main, "send_telegram_alert", _fake_send)

    result = app_main.run_once()
    assert result == 0
    assert calls["sent"] == 1

    state = load_state(str(state_path))
    assert state.last_regime != ""
    assert state.prev_oi == 1000.0
