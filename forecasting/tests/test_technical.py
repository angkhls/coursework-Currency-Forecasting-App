from datetime import date, timedelta

import pytest

from domain.models import CurrencyRate
from service.technical import build_chart_points, compute_ema, compute_sma, support_resistance


def _rates(values: list[float]) -> list[CurrencyRate]:
    start = date(2026, 1, 1)
    return [
        CurrencyRate(currency="USD", date=start + timedelta(days=i), rate=v)
        for i, v in enumerate(values)
    ]


def test_sma_first_value_equals_rate():
    import pandas as pd

    series = pd.Series([2.0, 4.0, 6.0])
    sma = compute_sma(series, window=20)
    assert sma.iloc[0] == pytest.approx(2.0)
    assert sma.iloc[-1] == pytest.approx(4.0)


def test_ema_reacts_to_changes():
    import pandas as pd

    series = pd.Series([1.0, 1.0, 5.0])
    ema = compute_ema(series, window=3)
    assert ema.iloc[-1] > ema.iloc[0]


def test_support_resistance():
    import pandas as pd

    series = pd.Series([1.0, 5.0, 3.0, 2.0])
    support, resistance = support_resistance(series, window=4)
    assert support == pytest.approx(1.0)
    assert resistance == pytest.approx(5.0)


def test_build_chart_points_includes_indicators():
    rates = _rates([2.7, 2.8, 2.75, 2.76, 2.77])
    points, levels = build_chart_points(rates)
    assert len(points) == 5
    assert points[-1].sma_20 is not None
    assert points[-1].ema_20 is not None
    assert levels.support <= levels.resistance
