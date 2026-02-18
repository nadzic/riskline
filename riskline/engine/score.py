from __future__ import annotations

from dataclasses import dataclass

from riskline.config import Thresholds


@dataclass(frozen=True)
class ScoreResult:
    score: int
    regime: str
    diagnostics: dict[str, str]


def _clamp_score(value: int) -> int:
    return max(0, min(100, value))


def _regime_for_score(score: int, fear_greed: int, trend_risk_off: bool) -> str:
    if fear_greed <= 20 and trend_risk_off:
        return "EXTREME_FEAR_RISK_OFF"
    if score <= 35:
        return "RISK_OFF_BUY_ZONE"
    if score >= 70:
        return "RISK_ON_EUPHORIA"
    return "NEUTRAL"


def compute_score(
    *,
    fear_greed_value: int,
    trend_pct_vs_200d: float | None,
    funding_rate: float,
    oi_delta_pct: float | None,
    volatility_pct: float,
    thresholds: Thresholds,
) -> ScoreResult:
    score = 50
    diagnostics: dict[str, str] = {}

    if fear_greed_value <= thresholds.fear_greed_buy:
        score -= 20
        diagnostics["fear_greed"] = "Extreme Fear (buy bias)"
    elif fear_greed_value >= thresholds.fear_greed_sell:
        score += 20
        diagnostics["fear_greed"] = "Greed (sell bias)"
    else:
        diagnostics["fear_greed"] = "Neutral sentiment"

    trend_risk_off = (
        trend_pct_vs_200d is not None
        and trend_pct_vs_200d <= thresholds.trend_risk_off_pct
    )
    if trend_risk_off:
        score += 15
        diagnostics["trend"] = "Risk-off"
    else:
        score -= 5
        diagnostics["trend"] = "Risk-on/neutral"

    if funding_rate <= thresholds.funding_short_crowded:
        score -= 10
        diagnostics["funding"] = "Short crowded"
    elif funding_rate >= thresholds.funding_long_crowded:
        score += 10
        diagnostics["funding"] = "Long crowded"
    else:
        diagnostics["funding"] = "Balanced"

    if oi_delta_pct is None:
        diagnostics["oi"] = "No prior OI baseline"
    elif oi_delta_pct <= thresholds.oi_deleveraging_pct:
        score -= 10
        diagnostics["oi"] = "Deleveraging"
    elif oi_delta_pct >= thresholds.oi_leverage_build_pct:
        score += 10
        diagnostics["oi"] = "Leverage build-up"
    else:
        diagnostics["oi"] = "Stable"

    if volatility_pct >= thresholds.high_volatility_pct:
        score += 5
        diagnostics["volatility"] = "High"
    else:
        diagnostics["volatility"] = "Normal"

    score = _clamp_score(score)
    regime = _regime_for_score(score, fear_greed_value, trend_risk_off)
    return ScoreResult(score=score, regime=regime, diagnostics=diagnostics)
