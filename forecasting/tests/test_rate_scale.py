import pytest

from main import _rate_stored_without_scale


@pytest.mark.parametrize(
    "rate,scale,expected",
    [
        (2.7596, 1, False),
        (3.872, 100, True),
        (6.2194, 100, True),
        (0.6012, 10, True),
        (0.06012, 10, False),
        (0.03872, 100, False),
        (4.0446, 10, True),
    ],
)
def test_detects_unscaled_nbrb_rates(rate, scale, expected):
    assert _rate_stored_without_scale(rate, scale) is expected
