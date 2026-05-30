from datetime import date
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from api.routes import get_rate_service
from domain.models import CurrencyRate
from main import app
from tests.test_rate_service import InMemoryRateRepository
from service.rate_service import RateService
from infrastructure.nbrb_client import NbrbApiClient


@pytest.fixture
def api_client():
    today = date(2026, 5, 30)
    repo = InMemoryRateRepository(
        {
            "USD": CurrencyRate(currency="USD", date=today, rate=2.7596),
            "RUB": CurrencyRate(currency="RUB", date=today, rate=0.03872),
        }
    )
    service = RateService(repository=repo, nbrb_client=NbrbApiClient())
    app.dependency_overrides[get_rate_service] = lambda: service
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_health(api_client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_convert_endpoint(api_client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        with patch.object(RateService, "_ensure_currency", new_callable=AsyncMock):
            response = await client.get(
                "/api/v1/convert",
                params={"amount": 100, "from": "RUB", "to": "USD"},
            )
    assert response.status_code == 200
    data = response.json()
    assert data["from_currency"] == "RUB"
    assert data["to_currency"] == "USD"
    assert data["result"] == pytest.approx(round(100 * 0.03872 / 2.7596, 4))
