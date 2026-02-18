from riskline.engine.decision import Decision
from riskline.engine.format_message import format_alert
from riskline.engine.score import ScoreResult


def test_format_alert_contains_critical_sections() -> None:
    text = format_alert(
        fear_greed_value=5,
        fear_greed_label="Extreme Fear",
        btc_price=70753.0,
        trend_pct_vs_200d=-3.8,
        funding_rate=-0.00028,
        oi_delta_pct=-7.0,
        liquidations_proxy="High",
        score=ScoreResult(
            score=24,
            regime="EXTREME_FEAR_RISK_OFF",
            diagnostics={},
        ),
        decision=Decision(action="BUY", guidance="DCA-BUY (3 tranches) / Reduce leverage"),
        send_reason="regime_flip",
    )
    assert "RISKLINE ALERT" in text
    assert "F&G: 5 (Extreme Fear)" in text
    assert "Action: DCA-BUY (3 tranches) / Reduce leverage" in text
