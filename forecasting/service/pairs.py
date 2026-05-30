from datetime import date
from typing import List

from domain.models import CurrencyCode, CurrencyPair, CurrencyRate

PAIR_LABELS: dict[CurrencyPair, str] = {
    "USD_BYN": "USD / BYN",
    "EUR_BYN": "EUR / BYN",
    "EUR_USD": "EUR / USD",
}


def pair_currencies(pair: CurrencyPair) -> tuple[CurrencyCode, CurrencyCode | None]:
    if pair == "USD_BYN":
        return "USD", None
    if pair == "EUR_BYN":
        return "EUR", None
    return "EUR", "USD"


def period_to_days(period: str) -> int:
    return {
        "day": 7,
        "week": 7,
        "month": 30,
        "year": 365,
    }.get(period, 30)


def build_pair_series(
    pair: CurrencyPair,
    usd: List[CurrencyRate],
    eur: List[CurrencyRate],
) -> List[CurrencyRate]:
    """Собирает временной ряд для пары из курсов НБРБ (в BYN или кросс-курс)."""
    if pair == "USD_BYN":
        return usd
    if pair == "EUR_BYN":
        return eur
    eur_by_date = {r.date: r.rate for r in eur}
    usd_by_date = {r.date: r.rate for r in usd}
    common = sorted(set(eur_by_date) & set(usd_by_date))
    return [
        CurrencyRate(currency="EUR", date=d, rate=eur_by_date[d] / usd_by_date[d])
        for d in common
    ]
