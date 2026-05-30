import pytest

from service.pairs import pair_currencies, period_to_days


def test_pair_currencies_extracts_base():
    base, quote = pair_currencies("RUB_BYN")
    assert base == "RUB"
    assert quote is None


def test_pair_currencies_rejects_unknown():
    with pytest.raises(ValueError, match="Неизвестная валюта"):
        pair_currencies("XXX_BYN")


@pytest.mark.parametrize(
    "period,expected",
    [("day", 7), ("week", 7), ("month", 30), ("year", 365), ("unknown", 30)],
)
def test_period_to_days(period, expected):
    assert period_to_days(period) == expected
