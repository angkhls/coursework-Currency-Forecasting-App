from domain.currencies import CURRENCY_CODES, CURRENCY_PAIRS, PAIR_LABELS
from domain.models import CurrencyCode, CurrencyPair

ALL_PAIRS: list[CurrencyPair] = list(CURRENCY_PAIRS)  # type: ignore[assignment]


def pair_currencies(pair: CurrencyPair) -> tuple[CurrencyCode, None]:
    """Все пары — курс валюты к BYN."""
    suffix = "_BYN"
    if not pair.endswith(suffix):
        raise ValueError(f"Неизвестная пара: {pair}")
    base = pair[: -len(suffix)]
    if base not in CURRENCY_CODES:
        raise ValueError(f"Неизвестная валюта в паре: {pair}")
    return base, None  # type: ignore[return-value]


def period_to_days(period: str) -> int:
    return {
        "day": 7,
        "week": 7,
        "month": 30,
        "year": 365,
    }.get(period, 30)
