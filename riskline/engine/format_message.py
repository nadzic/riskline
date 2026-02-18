from __future__ import annotations

from riskline.engine.decision import Decision
from riskline.engine.score import ScoreResult


def _funding_label(funding_rate: float) -> str:
    if funding_rate <= -0.0001:
        return "Short crowded"
    if funding_rate >= 0.0001:
        return "Long crowded"
    return "Balanced"


def _oi_label(oi_delta_pct: float | None) -> str:
    if oi_delta_pct is None:
        return "n/a"
    if oi_delta_pct <= -2:
        return "Deleveraging"
    if oi_delta_pct >= 2:
        return "Leverage build-up"
    return "Stable"


def format_alert(
    *,
    fear_greed_value: int,
    fear_greed_label: str,
    btc_price: float,
    trend_pct_vs_200d: float | None,
    funding_rate: float,
    oi_delta_pct: float | None,
    liquidations_proxy: str | None,
    score: ScoreResult,
    decision: Decision,
    send_reason: str,
) -> str:
    trend_text = "n/a" if trend_pct_vs_200d is None else f"{trend_pct_vs_200d:+.2f}%"
    liq_text = liquidations_proxy or "n/a"

    lines = [
        "RISKLINE ALERT",
        f"Reason: {send_reason}",
        f"Regime: {score.regime} | Score: {score.score}",
        f"F&G: {fear_greed_value} ({fear_greed_label})",
        f"BTC: {btc_price:,.2f} | vs 200D: {trend_text}",
        f"Funding: {funding_rate * 100:.4f}%/8h ({_funding_label(funding_rate)})",
        f"OI 24h proxy: {('n/a' if oi_delta_pct is None else f'{oi_delta_pct:+.2f}%')} ({_oi_label(oi_delta_pct)})",
        f"Liq proxy: {liq_text}",
        f"Action: {decision.guidance}",
    ]
    return "\n".join(lines)
