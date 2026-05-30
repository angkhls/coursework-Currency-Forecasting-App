from datetime import date, timedelta
from typing import List

from domain.models import CurrencyRate, ForecastPoint


def is_weekend(d: date) -> bool:
    return d.weekday() >= 5


def filter_weekdays(rates: List[CurrencyRate]) -> List[CurrencyRate]:
    return [r for r in rates if not is_weekend(r.date)]


def count_weekdays_between(start: date, end: date) -> int:
    n = 0
    d = start
    while d <= end:
        if not is_weekend(d):
            n += 1
        d += timedelta(days=1)
    return n


def count_weekdays_after(start: date, calendar_days: int) -> int:
    """Рабочие дни в интервале (start, start+calendar_days]."""
    end = start + timedelta(days=calendar_days)
    return count_weekdays_between(start + timedelta(days=1), end)


def calendar_end_after_weekdays(from_date: date, weekday_count: int) -> date:
    """Последний календарный день после N рабочих дней от from_date."""
    d = from_date
    seen = 0
    while seen < weekday_count:
        d += timedelta(days=1)
        if not is_weekend(d):
            seen += 1
    return d


def expand_forecast_to_calendar(
    business_forecast: List[ForecastPoint],
    last_history_date: date,
    calendar_days: int,
) -> List[ForecastPoint]:
    """
    Разворачивает прогноз по рабочим дням на календарный горизонт.
    Суббота/воскресенье получают значение последнего рабочего дня.
    """
    if not business_forecast:
        return []

    by_weekday = {p.date: p for p in business_forecast if not is_weekend(p.date)}
    end = last_history_date + timedelta(days=calendar_days)
    out: List[ForecastPoint] = []
    last = business_forecast[0]
    d = last_history_date + timedelta(days=1)

    while d <= end:
        if not is_weekend(d) and d in by_weekday:
            last = by_weekday[d]
            out.append(
                ForecastPoint(
                    date=d,
                    predicted_value=last.predicted_value,
                    lower=last.lower,
                    upper=last.upper,
                )
            )
        else:
            out.append(
                ForecastPoint(
                    date=d,
                    predicted_value=last.predicted_value,
                    lower=last.lower,
                    upper=last.upper,
                )
            )
        d += timedelta(days=1)

    return out


def compute_y_domain(
    rates: List[float],
    extras: List[float] | None = None,
    padding_ratio: float = 0.06,
    min_padding: float = 0.02,
) -> tuple[float, float]:
    values = [v for v in rates if v is not None]
    if extras:
        values.extend(v for v in extras if v is not None)
    if not values:
        return 0.0, 1.0
    vmin, vmax = min(values), max(values)
    if vmin == vmax:
        pad = max(min_padding, vmin * 0.02)
        return round(vmin - pad, 4), round(vmax + pad, 4)
    pad = max((vmax - vmin) * padding_ratio, min_padding)
    return round(vmin - pad, 4), round(vmax + pad, 4)
