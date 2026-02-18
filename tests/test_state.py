from riskline.state import RiskState, compute_oi_delta_pct, should_send_alert


def test_compute_oi_delta_pct() -> None:
    assert compute_oi_delta_pct(100.0, 110.0) == 10.0
    assert compute_oi_delta_pct(None, 110.0) is None


def test_should_send_first_alert() -> None:
    state = RiskState()
    send, reason = should_send_alert(
        state=state,
        current_regime="NEUTRAL",
        cooldown_hours=6,
        now_ts=1000,
    )
    assert send is True
    assert reason == "first_alert"


def test_should_send_on_regime_flip() -> None:
    state = RiskState(last_alert_ts=1000, last_regime="NEUTRAL")
    send, reason = should_send_alert(
        state=state,
        current_regime="RISK_ON_EUPHORIA",
        cooldown_hours=6,
        now_ts=2000,
    )
    assert send is True
    assert reason == "regime_flip"


def test_should_respect_cooldown_when_regime_same() -> None:
    state = RiskState(last_alert_ts=1000, last_regime="NEUTRAL")
    send, reason = should_send_alert(
        state=state,
        current_regime="NEUTRAL",
        cooldown_hours=6,
        now_ts=2000,
    )
    assert send is False
    assert reason == "cooldown_active"
