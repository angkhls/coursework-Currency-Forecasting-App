from typing import List, Tuple

import pandas as pd

from domain.models import ChartPoint, CurrencyRate, TechnicalLevels

SMA_WINDOW = 20
EMA_WINDOW = 20


def compute_sma(values: pd.Series, window: int = SMA_WINDOW) -> pd.Series:
    """SMA(n): скользящее среднее до n точек; линия видна на всём графике."""
    if len(values) == 0:
        return values
    return values.rolling(window=window, min_periods=1).mean()


def compute_ema(values: pd.Series, window: int = EMA_WINDOW) -> pd.Series:
    """EMA(n): экспоненциальное сглаживание (span=n)."""
    if len(values) == 0:
        return values
    return values.ewm(span=window, adjust=False, min_periods=1).mean()


def support_resistance(values: pd.Series, window: int = 20) -> Tuple[float, float]:
    recent = values.tail(min(window, len(values)))
    return float(recent.min()), float(recent.max())


def build_chart_points(rates: List[CurrencyRate]) -> Tuple[List[ChartPoint], TechnicalLevels]:
    if not rates:
        return [], TechnicalLevels(support=0.0, resistance=0.0)

    series = pd.Series(
        [r.rate for r in rates],
        index=pd.DatetimeIndex([r.date for r in rates]),
    )
    sma = compute_sma(series)
    ema = compute_ema(series)
    support, resistance = support_resistance(series)

    points = [
        ChartPoint(
            date=r.date,
            rate=r.rate,
            sma_20=round(float(sma.iloc[i]), 4) if pd.notna(sma.iloc[i]) else None,
            ema_20=round(float(ema.iloc[i]), 4) if pd.notna(ema.iloc[i]) else None,
            is_weekend=r.date.weekday() >= 5,
        )
        for i, r in enumerate(rates)
    ]
    return points, TechnicalLevels(support=round(support, 4), resistance=round(resistance, 4))
