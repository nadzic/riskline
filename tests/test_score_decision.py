from riskline.config import Thresholds
from riskline.engine.decision import decide_action
from riskline.engine.score import compute_score


def _thresholds() -> Thresholds:
    return Thresholds(
        fear_greed_buy=20,
        fear_greed_sell=70,
        funding_short_crowded=-0.0001,
        funding_long_crowded=0.0001,
        trend_risk_off_pct=-1.0,
        oi_deleveraging_pct=-2.0,
        oi_leverage_build_pct=2.0,
        high_volatility_pct=3.0,
    )


def test_compute_score_buy_zone() -> None:
    result = compute_score(
        fear_greed_value=10,
        trend_pct_vs_200d=-2.0,
        funding_rate=-0.0002,
        oi_delta_pct=-3.0,
        volatility_pct=1.0,
        thresholds=_thresholds(),
    )
    assert result.score <= 35
    assert result.regime == "EXTREME_FEAR_RISK_OFF"


def test_compute_score_reduce_zone() -> None:
    result = compute_score(
        fear_greed_value=80,
        trend_pct_vs_200d=3.0,
        funding_rate=0.0003,
        oi_delta_pct=4.0,
        volatility_pct=4.0,
        thresholds=_thresholds(),
    )
    assert result.score >= 70
    assert result.regime == "RISK_ON_EUPHORIA"


def test_decide_action_thresholds() -> None:
    assert decide_action(30).action == "BUY"
    assert decide_action(50).action == "HOLD"
    assert decide_action(80).action == "REDUCE"
