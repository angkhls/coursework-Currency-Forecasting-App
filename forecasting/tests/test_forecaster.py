import math
from datetime import date, timedelta

import pandas as pd
import pytest

import service.forecaster as fc
from domain.models import CurrencyRate
from service.forecaster import (
    BaseForecast,
    SARIMAXForecaster,
    _enrich_flat_forecast,
    _next_business_days,
    _to_business_series,
    _volatility_margin,
)


def _weekday_rates(n: int, start: date = date(2026, 1, 5)) -> list[CurrencyRate]:
    """n курсов только по рабочим дням (2026-01-05 — понедельник)."""
    out, d, i = [], start, 0
    while len(out) < n:
        if d.weekday() < 5:
            out.append(
                CurrencyRate(
                    currency="USD",
                    date=d,
                    rate=round(2.70 + 0.02 * math.sin(i / 3) + 0.001 * i, 4),
                )
            )
            i += 1
        d += timedelta(days=1)
    return out


def test_base_forecast_is_abstract():
    with pytest.raises(TypeError):
        BaseForecast()  # type: ignore[abstract]


def test_next_business_days_skips_weekend():
    friday = date(2026, 5, 29)
    assert _next_business_days(friday, 3) == [
        date(2026, 6, 1),
        date(2026, 6, 2),
        date(2026, 6, 3),
    ]


def test_next_business_days_zero():
    assert _next_business_days(date(2026, 5, 29), 0) == []


def test_to_business_series_is_business_frequency():
    rates = _weekday_rates(30)
    series, business = _to_business_series(rates)
    assert len(series) >= 20
    assert series.index.dayofweek.max() < 5
    assert len(business) >= 20


def test_to_business_series_short_input_falls_back_to_rates():
    rates = _weekday_rates(5)
    series, business = _to_business_series(rates)
    assert business == rates
    assert len(series) == 5


def test_volatility_margin_constant_series_uses_floor():
    series = pd.Series([2.0] * 30)
    assert _volatility_margin(series, 5) == pytest.approx(2.0 * 0.008)


def test_volatility_margin_single_point_uses_absolute_floor():
    assert _volatility_margin(pd.Series([1.0]), 3) == pytest.approx(0.01)


def test_volatility_margin_grows_with_noise():
    noisy = pd.Series([2.0, 2.5, 1.8, 2.6, 1.9, 2.7] * 5)
    assert _volatility_margin(noisy, 7) > 2.0 * 0.008


def test_enrich_flat_forecast_empty_predictions_unchanged():
    series = pd.Series([1.0, 1.1, 1.2])
    empty = pd.Series([], dtype=float)
    assert _enrich_flat_forecast(series, empty).empty


def test_enrich_flat_forecast_adds_trend_when_flat():
    series = pd.Series([1.0 + 0.01 * i for i in range(20)])
    last = float(series.iloc[-1])
    flat = pd.Series([last] * 5, index=range(5))
    result = _enrich_flat_forecast(series, flat)
    assert result.iloc[0] == pytest.approx(last + 0.01)
    assert result.iloc[-1] == pytest.approx(last + 0.05)


def test_enrich_flat_forecast_keeps_non_flat_predictions():
    series = pd.Series([1.0 + 0.01 * i for i in range(20)])
    moving = pd.Series([1.3, 1.4, 1.5], index=range(3))
    assert _enrich_flat_forecast(series, moving).equals(moving)


def test_enrich_flat_forecast_keeps_when_history_is_flat():
    series = pd.Series([2.0] * 20)
    flat = pd.Series([2.0] * 3, index=range(3))
    assert _enrich_flat_forecast(series, flat).equals(flat)


def test_sarimax_predict_returns_business_day_points():
    rates = _weekday_rates(40)
    points = SARIMAXForecaster().predict(rates, 5)

    assert len(points) == 5
    assert all(p.date.weekday() < 5 for p in points)
    assert points[0].date > rates[-1].date
    assert [p.date for p in points] == sorted(p.date for p in points)
    assert all(p.lower is not None and p.upper is not None for p in points)
    assert all(p.lower <= p.upper for p in points)

    last = rates[-1].rate
    margin = _volatility_margin(_to_business_series(rates)[0], 5)
    assert all(abs(p.predicted_value - last) <= margin + 1e-3 for p in points)


def test_sarimax_predict_falls_back_when_first_fit_fails(monkeypatch):
    real = fc.SARIMAX
    calls: list = []

    def flaky(*args, **kwargs):
        calls.append(kwargs.get("seasonal_order"))
        if len(calls) == 1:
            raise RuntimeError("boom")
        return real(*args, **kwargs)

    monkeypatch.setattr(fc, "SARIMAX", flaky)
    points = SARIMAXForecaster().predict(_weekday_rates(40), 3)

    assert len(points) == 3
    assert calls[1] == (0, 0, 0, 0)