from __future__ import annotations

import statistics


def simple_volatility_proxy(series: list[float]) -> float:
    if len(series) < 2:
        return 0.0
    return abs(series[-1] - series[-2])


def daily_return_volatility_pct(series: list[float], lookback: int = 14) -> float:
    if len(series) < 3:
        return 0.0
    window = series[-(lookback + 1) :]
    returns: list[float] = []
    for idx in range(1, len(window)):
        prev_close = window[idx - 1]
        close = window[idx]
        if prev_close == 0:
            continue
        returns.append(((close - prev_close) / prev_close) * 100.0)
    if len(returns) < 2:
        return 0.0
    return float(statistics.pstdev(returns))
