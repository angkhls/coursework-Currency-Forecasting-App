import pytest

from service.metrics_calc import mape, rmse


def test_mape_perfect_prediction():
    actual = [1.0, 2.0, 3.0]
    assert mape(actual, actual) == 0.0


def test_mape_known_error():
    actual = [100.0, 200.0]
    predicted = [110.0, 180.0]
    # |10/100| + |20/200| = 0.1 + 0.1 → mean 0.1 → 10%
    assert mape(actual, predicted) == pytest.approx(10.0)


def test_rmse():
    actual = [1.0, 2.0, 3.0]
    predicted = [1.0, 2.0, 4.0]
    assert rmse(actual, predicted) == pytest.approx(0.5773503, rel=1e-4)
