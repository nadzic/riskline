def simple_volatility_proxy(series: list[float]) -> float:
    if len(series) < 2:
        return 0.0
    return abs(series[-1] - series[-2])
