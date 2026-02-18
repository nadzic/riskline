from __future__ import annotations


def ma200(closes: list[float]) -> float | None:
    if len(closes) < 200:
        return None
    return sum(closes[-200:]) / 200


def pct_distance_from_ma(price: float, moving_average: float | None) -> float | None:
    if moving_average is None or moving_average == 0:
        return None
    return ((price - moving_average) / moving_average) * 100.0


def is_risk_off(
    price: float,
    moving_average: float | None,
    risk_off_threshold_pct: float,
) -> bool:
    pct = pct_distance_from_ma(price, moving_average)
    if pct is None:
        return False
    return pct <= risk_off_threshold_pct
