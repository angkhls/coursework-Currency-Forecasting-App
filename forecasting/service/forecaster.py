import pandas as pd
from abc import ABC, abstractmethod
from datetime import date, timedelta
from typing import List

import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX

from domain.models import CurrencyRate, ForecastPoint
from service.calendar_utils import filter_weekdays

# ─────────────────────────────────────────────
# ПАТТЕРН: Strategy (Стратегия)
# ─────────────────────────────────────────────


class BaseForecast(ABC):
    @abstractmethod
    def predict(self, rates: List[CurrencyRate], days: int) -> List[ForecastPoint]:
        ...


def _next_business_days(from_date: date, n: int) -> list[date]:
    out: list[date] = []
    d = from_date
    while len(out) < n:
        d += timedelta(days=1)
        if d.weekday() < 5:
            out.append(d)
    return out


def _to_business_series(rates: List[CurrencyRate]) -> pd.Series:
    business = filter_weekdays(rates)
    if len(business) < 20:
        business = rates
    series = pd.Series(
        data=[r.rate for r in business],
        index=pd.DatetimeIndex([r.date for r in business]),
        name="rate",
    ).sort_index()
    if len(series) >= 2:
        series = series.asfreq("B", method="ffill")
    return series, business


def _volatility_margin(series: pd.Series, steps: int) -> float:
    diffs = series.diff().dropna()
    daily_vol = float(diffs.std()) if len(diffs) else 0.0
    if not np.isfinite(daily_vol) or daily_vol < 1e-9:
        daily_vol = float(series.tail(20).std()) * 0.25 if len(series) > 1 else 0.0
    last = float(series.iloc[-1])
    margin = daily_vol * np.sqrt(max(steps, 1)) * 2.5
    return max(margin, last * 0.008, 0.01)


def _enrich_flat_forecast(series: pd.Series, predictions: pd.Series) -> pd.Series:
    """Если SARIMAX дал почти константу — добавляем тренд последних дней."""
    if len(predictions) == 0:
        return predictions
    last_val = float(series.iloc[-1])
    spread = float(predictions.max() - predictions.min())
    recent = series.tail(14)
    hist_spread = float(recent.max() - recent.min()) if len(recent) > 1 else 0.0
    threshold = max(last_val * 0.0003, 0.0008)

    if spread >= threshold or hist_spread < threshold:
        return predictions

    tail = recent.tail(8)
    if len(tail) < 2:
        return predictions

    slope = (float(tail.iloc[-1]) - float(tail.iloc[0])) / max(len(tail) - 1, 1)
    enriched = [last_val + slope * (i + 1) for i in range(len(predictions))]
    return pd.Series(enriched, index=predictions.index)


class SARIMAXForecaster(BaseForecast):
    def __init__(
        self,
        order: tuple = (1, 1, 1),
        seasonal_order: tuple = (1, 1, 1, 5),
    ):
        self.order = order
        self.seasonal_order = seasonal_order

    def predict(self, rates: List[CurrencyRate], days: int) -> List[ForecastPoint]:
        series, business = _to_business_series(rates)
        last_val = float(series.iloc[-1])

        try:
            model = SARIMAX(
                series,
                order=self.order,
                seasonal_order=self.seasonal_order,
                enforce_stationarity=False,
                enforce_invertibility=False,
            )
            result = model.fit(disp=False, maxiter=80)
            forecast_res = result.get_forecast(steps=days)
            predictions = forecast_res.predicted_mean
            conf_int = forecast_res.conf_int(alpha=0.2)
        except Exception:
            model = SARIMAX(
                series,
                order=(1, 1, 1),
                seasonal_order=(0, 0, 0, 0),
                enforce_stationarity=False,
                enforce_invertibility=False,
            )
            result = model.fit(disp=False, maxiter=80)
            forecast_res = result.get_forecast(steps=days)
            predictions = forecast_res.predicted_mean
            conf_int = forecast_res.conf_int(alpha=0.2)

        predictions = _enrich_flat_forecast(series, predictions)

        margin = _volatility_margin(series, days)
        predictions = predictions.clip(lower=last_val - margin, upper=last_val + margin)

        last_date = business[-1].date
        forecast_dates = _next_business_days(last_date, days)
        points: list[ForecastPoint] = []
        for i, val in enumerate(predictions):
            if i >= len(forecast_dates):
                break
            lower = upper = None
            if conf_int is not None and len(conf_int) > i:
                lower = round(float(conf_int.iloc[i, 0]), 4)
                upper = round(float(conf_int.iloc[i, 1]), 4)
            points.append(
                ForecastPoint(
                    date=forecast_dates[i],
                    predicted_value=round(float(val), 4),
                    lower=lower,
                    upper=upper,
                )
            )
        return points
