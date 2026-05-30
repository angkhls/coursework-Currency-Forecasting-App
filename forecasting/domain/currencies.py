"""Справочник валют НБРБ и торговых пар (XXX/BYN)."""

from typing import Dict, Tuple

# ID и масштаб котировки в API НБРБ (exrates, periodicity=0)
NBRB_CURRENCY_IDS: Dict[str, int] = {
    "USD": 431,
    "EUR": 451,
    "RUB": 456,
    "CNY": 462,
    "GBP": 429,
    "PLN": 452,
    "AED": 513,
    "CHF": 426,
    "UAH": 449,
    "TRY": 460,
}

# Официальный масштаб котировки НБРБ (Cur_Scale в ответе API)
NBRB_QUOTE_SCALE: Dict[str, int] = {
    "USD": 1,
    "EUR": 1,
    "GBP": 1,
    "CHF": 1,
    "RUB": 100,
    "CNY": 10,
    "PLN": 10,
    "AED": 10,
    "UAH": 100,
    "TRY": 10,
}

CURRENCY_CODES: Tuple[str, ...] = tuple(NBRB_CURRENCY_IDS.keys())

CURRENCY_PAIRS: Tuple[str, ...] = tuple(f"{code}_BYN" for code in CURRENCY_CODES)

PAIR_LABELS: Dict[str, str] = {
    f"{code}_BYN": f"{code} / BYN" for code in CURRENCY_CODES
}
