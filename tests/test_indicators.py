from riskline.indicators.trend import is_risk_off, ma200, pct_distance_from_ma
from riskline.indicators.volatility import daily_return_volatility_pct


def test_ma200_returns_none_when_not_enough_data() -> None:
    assert ma200([1.0] * 50) is None


def test_ma200_returns_average_last_200() -> None:
    closes = list(range(1, 301))
    expected = sum(closes[-200:]) / 200
    assert ma200(closes) == expected


def test_pct_distance_and_risk_off() -> None:
    pct = pct_distance_from_ma(price=95.0, moving_average=100.0)
    assert pct == -5.0
    assert is_risk_off(95.0, 100.0, -1.0) is True


def test_daily_return_volatility_pct_non_negative() -> None:
    closes = [100, 101, 99, 100, 102, 98, 101]
    assert daily_return_volatility_pct(closes) >= 0.0
