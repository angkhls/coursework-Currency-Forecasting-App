from datetime import date
from typing import List, Optional
from unittest.mock import AsyncMock, patch

import pytest

from domain.models import CurrencyRate
from domain.repositories import CurrencyRateRepository
from infrastructure.nbrb_client import NbrbApiClient
from service.rate_service import RateService


class InMemoryRateRepository(CurrencyRateRepository):
    def __init__(self, rates: dict[str, CurrencyRate]):
        self._rates = rates

    async def save(self, rate: CurrencyRate) -> None:
        self._rates[rate.currency] = rate

    async def save_many(self, rates: List[CurrencyRate]) -> None:
        for rate in rates:
            await self.save(rate)

    async def get_by_currency_and_date(
        self, currency: str, target_date: date
    ) -> Optional[CurrencyRate]:
        rate = self._rates.get(currency)
        if rate and rate.date == target_date:
            return rate
        return None

    async def get_history(
        self, currency: str, from_date: date, to_date: date
    ) -> List[CurrencyRate]:
        rate = self._rates.get(currency)
        if rate and from_date <= rate.date <= to_date:
            return [rate]
        return []

    async def get_latest(self, currency: str) -> Optional[CurrencyRate]:
        return self._rates.get(currency)

    async def delete_currency(self, currency: str) -> None:
        self._rates.pop(currency, None)


@pytest.fixture
def rate_service() -> RateService:
    today = date(2026, 5, 30)
    repo = InMemoryRateRepository(
        {
            "USD": CurrencyRate(currency="USD", date=today, rate=2.7596),
            "RUB": CurrencyRate(currency="RUB", date=today, rate=0.03872),
            "TRY": CurrencyRate(currency="TRY", date=today, rate=0.06012),
        }
    )
    return RateService(repository=repo, nbrb_client=NbrbApiClient())


@pytest.mark.asyncio
async def test_convert_rub_to_usd(rate_service: RateService):
    with patch.object(rate_service, "_ensure_currency", new_callable=AsyncMock):
        result = await rate_service.convert(100, "RUB", "USD")
    expected = 100 * (0.03872 / 2.7596)
    assert result.result == pytest.approx(round(expected, 4))
    assert result.rate == pytest.approx(round(0.03872 / 2.7596, 6))


@pytest.mark.asyncio
async def test_convert_same_currency(rate_service: RateService):
    with patch.object(rate_service, "_ensure_currency", new_callable=AsyncMock):
        result = await rate_service.convert(50, "USD", "USD")
    assert result.result == 50
    assert result.rate == 1.0


@pytest.mark.asyncio
async def test_nbrb_quote_display_values(rate_service: RateService):
    """100 RUB и 10 TRY в BYN — проверка нормализованных курсов."""
    with patch.object(rate_service, "_ensure_currency", new_callable=AsyncMock):
        rub = await rate_service.get_latest_rate("RUB")
        try_ = await rate_service.get_latest_rate("TRY")
    assert rub.rate * 100 == pytest.approx(3.872, rel=1e-3)
    assert try_.rate * 10 == pytest.approx(0.6012, rel=1e-3)
