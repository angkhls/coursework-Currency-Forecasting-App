from datetime import date
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from api.routes import get_rate_service
from domain.models import CurrencyRate
from main import app
from service.rate_service import RateService
from tests.test_rate_service import InMemoryRateRepository


@pytest.fixture
def scenario_service() -> RateService:
    today = date.today()
    repo = InMemoryRateRepository(
        {
            "USD": CurrencyRate(currency="USD", date=today, rate=2.7596),
            "RUB": CurrencyRate(currency="RUB", date=today, rate=0.03872),
            "TRY": CurrencyRate(currency="TRY", date=today, rate=0.06012),
            "EUR": CurrencyRate(currency="EUR", date=today, rate=3.0112),
        }
    )
    return RateService(repository=repo, nbrb_client=AsyncMock())


@pytest.fixture
def override_api_service():
    today = date.today()
    repo = InMemoryRateRepository(
        {
            "USD": CurrencyRate(currency="USD", date=today, rate=2.7596),
            "RUB": CurrencyRate(currency="RUB", date=today, rate=0.03872),
            "TRY": CurrencyRate(currency="TRY", date=today, rate=0.06012),
            "EUR": CurrencyRate(currency="EUR", date=today, rate=3.0112),
        }
    )
    service = RateService(repository=repo, nbrb_client=AsyncMock())
    app.dependency_overrides[get_rate_service] = lambda: service
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "amount, from_currency, to_currency, expected",
    [
        (100, "RUB", "USD", 100 * (0.03872 / 2.7596)),
        (50, "TRY", "USD", 50 * (0.06012 / 2.7596)),
        (10, "USD", "RUB", 10 * (2.7596 / 0.03872)),
    ],
)
async def test_convert_multiple_currency_pairs(amount, from_currency, to_currency, expected, scenario_service):
    # Arrange
    service = scenario_service

    # Act
    with patch.object(service, "_ensure_currency", new_callable=AsyncMock):
        result = await service.convert(amount, from_currency, to_currency)

    # Assert
    assert result.result == pytest.approx(round(expected, 4), rel=1e-4)
    assert result.from_currency == from_currency
    assert result.to_currency == to_currency


@pytest.mark.asyncio
async def test_get_latest_rate_then_convert_then_get_history_scenario(scenario_service):
    # Arrange
    service = scenario_service

    # Act
    with patch.object(service, "_ensure_currency", new_callable=AsyncMock):
        latest = await service.get_latest_rate("USD")
        converted = await service.convert(100, "RUB", "USD")
        history = await service.get_history("USD", 30)

    # Assert
    assert latest.currency == "USD"
    assert latest.rate == pytest.approx(2.7596)
    assert converted.result == pytest.approx(100 * (0.03872 / 2.7596), rel=1e-4)
    assert len(history) >= 1
    assert all(item.currency == "USD" for item in history)


@pytest.mark.asyncio
async def test_api_currency_flow_sequence(override_api_service):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        latest = await client.get("/api/v1/rates/USD/latest")
        converted = await client.get(
            "/api/v1/convert",
            params={"amount": 100, "from": "RUB", "to": "USD"},
        )
        history = await client.get("/api/v1/rates/USD/history", params={"days": 30})

    assert latest.status_code == 200
    assert converted.status_code == 200
    assert history.status_code == 200

    assert latest.json()["currency"] == "USD"
    assert converted.json()["result"] == pytest.approx(round(100 * (0.03872 / 2.7596), 4), rel=1e-4)
    assert len(history.json()) >= 1


@pytest.mark.asyncio
async def test_api_history_endpoint_rejects_invalid_days(override_api_service):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/rates/USD/history", params={"days": 0})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_api_convert_rejects_invalid_amount(override_api_service):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            "/api/v1/convert",
            params={"amount": 0, "from": "USD", "to": "RUB"},
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_latest_rate_raises_when_currency_missing(scenario_service):
    # Arrange
    service = scenario_service

    # Act / Assert
    with patch.object(service, "_ensure_currency", new_callable=AsyncMock):
        with pytest.raises(ValueError):
            await service.get_latest_rate("XYZ")
