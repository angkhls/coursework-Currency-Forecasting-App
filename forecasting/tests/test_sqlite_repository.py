from datetime import date

import pytest
import pytest_asyncio

from domain.models import CurrencyRate
from infrastructure.sqlite_repository import SqliteCurrencyRateRepository


@pytest_asyncio.fixture
async def repo(tmp_path):
    repository = SqliteCurrencyRateRepository(str(tmp_path / "rates.db"))
    await repository.connect()
    yield repository
    await repository.close()


def _rate(currency: str, day: int, value: float) -> CurrencyRate:
    return CurrencyRate(currency=currency, date=date(2026, 5, day), rate=value)


@pytest.mark.asyncio
async def test_save_and_get_by_date(repo):
    await repo.save(_rate("USD", 30, 2.7596))
    found = await repo.get_by_currency_and_date("USD", date(2026, 5, 30))

    assert found is not None
    assert found.currency == "USD"
    assert found.rate == pytest.approx(2.7596)


@pytest.mark.asyncio
async def test_get_by_date_missing_returns_none(repo):
    assert await repo.get_by_currency_and_date("USD", date(2026, 5, 30)) is None


@pytest.mark.asyncio
async def test_save_overwrites_same_currency_and_date(repo):
    await repo.save(_rate("USD", 30, 2.7))
    await repo.save(_rate("USD", 30, 2.9))

    found = await repo.get_by_currency_and_date("USD", date(2026, 5, 30))
    assert found.rate == pytest.approx(2.9)


@pytest.mark.asyncio
async def test_save_many_empty_is_noop(repo):
    await repo.save_many([])
    assert await repo.get_latest("USD") is None


@pytest.mark.asyncio
async def test_save_many_and_history_is_sorted_and_filtered(repo):
    await repo.save_many(
        [
            _rate("USD", 12, 2.72),
            _rate("USD", 10, 2.70),
            _rate("USD", 11, 2.71),
            _rate("USD", 20, 2.80),
            _rate("EUR", 11, 3.00),
        ]
    )

    history = await repo.get_history("USD", date(2026, 5, 10), date(2026, 5, 12))

    assert [h.date.day for h in history] == [10, 11, 12]
    assert all(h.currency == "USD" for h in history)


@pytest.mark.asyncio
async def test_get_latest_returns_most_recent(repo):
    await repo.save_many([_rate("USD", 10, 2.70), _rate("USD", 25, 2.75)])
    latest = await repo.get_latest("USD")

    assert latest.date == date(2026, 5, 25)
    assert latest.rate == pytest.approx(2.75)


@pytest.mark.asyncio
async def test_get_latest_unknown_currency_returns_none(repo):
    assert await repo.get_latest("EUR") is None


@pytest.mark.asyncio
async def test_delete_currency_removes_only_that_currency(repo):
    await repo.save_many([_rate("USD", 10, 2.7), _rate("EUR", 10, 3.0)])
    await repo.delete_currency("USD")

    assert await repo.get_latest("USD") is None
    assert await repo.get_latest("EUR") is not None


@pytest.mark.asyncio
async def test_close_is_idempotent(tmp_path):
    repository = SqliteCurrencyRateRepository(str(tmp_path / "x.db"))
    await repository.connect()
    await repository.close()
    await repository.close()