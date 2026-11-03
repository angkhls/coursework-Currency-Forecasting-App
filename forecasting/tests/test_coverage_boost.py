from datetime import date, timedelta
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from api.routes import get_rate_service
from domain.models import CurrencyRate
from main import app
from service.rate_service import RateService
from tests.test_rate_service import InMemoryRateRepository


@pytest.fixture
def client_service():
    today = date.today()
    repo = InMemoryRateRepository(
        {
            "USD": CurrencyRate(currency="USD", date=today, rate=2.7596),
            "RUB": CurrencyRate(currency="RUB", date=today, rate=0.03872),
        }
    )
    service = RateService(repository=repo, nbrb_client=AsyncMock())
    service._ensure_currency = AsyncMock()  # без сетевых вызовов
    app.dependency_overrides[get_rate_service] = lambda: service
    yield service
    app.dependency_overrides.clear()


async def _get(url, **params):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        return await client.get(url, params=params)


@pytest.mark.asyncio
async def test_latest_rate_ok(client_service):
    res = await _get("/api/v1/rates/USD/latest")
    assert res.status_code == 200
    assert res.json()["currency"] == "USD"


@pytest.mark.asyncio
async def test_history_ok(client_service):
    res = await _get("/api/v1/rates/USD/history", days=7)
    assert res.status_code == 200
    assert len(res.json()) >= 1


@pytest.mark.asyncio
async def test_convert_ok(client_service):
    res = await _get("/api/v1/convert", amount=100, **{"from": "RUB", "to": "USD"})
    assert res.status_code == 200
    assert res.json()["to_currency"] == "USD"


@pytest.mark.asyncio
async def test_history_invalid_days(client_service):
    res = await _get("/api/v1/rates/USD/history", days=0)
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_convert_invalid_amount(client_service):
    res = await _get("/api/v1/convert", amount=0, **{"from": "USD", "to": "RUB"})
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_bank_rates_service_constructs():
    from service.bank_rates_service import BankRatesService

    service = BankRatesService(
        belarusbank=AsyncMock(), myfin=AsyncMock(), nbrb=AsyncMock()
    )
    assert service is not None