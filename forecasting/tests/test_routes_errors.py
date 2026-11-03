"""Тесты веток API с моками сервисов (в т.ч. обработка ошибок 400/404/502)."""
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from api import routes
from api.routes import (
    get_bank_rates_service,
    get_finnhub_client,
    get_rate_service,
)
from domain.models import BankRatesTable
from main import app


@pytest.fixture
def svc():
    service = AsyncMock()
    app.dependency_overrides[get_rate_service] = lambda: service
    yield service
    app.dependency_overrides.clear()


@pytest.fixture
def banks():
    service = AsyncMock()
    app.dependency_overrides[get_bank_rates_service] = lambda: service
    yield service
    app.dependency_overrides.clear()


@pytest.fixture
def finnhub():
    client = AsyncMock()
    app.dependency_overrides[get_finnhub_client] = lambda: client
    yield client
    app.dependency_overrides.clear()


async def _get(url: str, **params):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        return await client.get(url, params=params or None)


async def _post(url: str):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        return await client.post(url)


# ---------- заглушки зависимостей ----------

@pytest.mark.parametrize(
    "factory",
    [routes.get_rate_service, routes.get_bank_rates_service, routes.get_finnhub_client],
)
def test_unconfigured_dependencies_raise(factory):
    with pytest.raises(NotImplementedError):
        factory()


# ---------- rates ----------

@pytest.mark.asyncio
async def test_latest_rate_missing_currency_is_404(svc):
    svc.get_latest_rate.side_effect = ValueError("нет курса")
    res = await _get("/api/v1/rates/USD/latest")
    assert res.status_code == 404
    assert "нет курса" in res.json()["detail"]


@pytest.mark.asyncio
async def test_history_value_error_is_400(svc):
    svc.get_history.side_effect = ValueError("bad")
    res = await _get("/api/v1/rates/USD/history", days=7)
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_rate_on_date_error_is_404(svc):
    svc.get_rate_on_date.side_effect = RuntimeError("нет данных")
    res = await _get("/api/v1/rates/USD/on/2026-05-30")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_rate_on_date_invalid_date_is_422(svc):
    res = await _get("/api/v1/rates/USD/on/not-a-date")
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_sync_success(svc):
    svc.sync_rates.return_value = 3
    res = await _post("/api/v1/rates/USD/sync")
    assert res.status_code == 200
    assert res.json() == {"synced": 3, "currency": "USD"}


@pytest.mark.asyncio
async def test_sync_failure_is_502(svc):
    svc.sync_rates.side_effect = RuntimeError("timeout")
    res = await _post("/api/v1/rates/USD/sync")
    assert res.status_code == 502
    assert "NBRB" in res.json()["detail"]


@pytest.mark.asyncio
async def test_convert_value_error_is_400(svc):
    svc.convert.side_effect = ValueError("unsupported")
    res = await _get("/api/v1/convert", amount=10, **{"from": "USD", "to": "RUB"})
    assert res.status_code == 400


# ---------- macro ----------

@pytest.mark.asyncio
async def test_macro_belarus_error_is_502(svc):
    svc.get_macro.side_effect = RuntimeError("upstream")
    res = await _get("/api/v1/macro/belarus")
    assert res.status_code == 502


@pytest.mark.asyncio
async def test_pair_macro_error_is_502(svc):
    svc.get_macro.side_effect = RuntimeError("upstream")
    res = await _get("/api/v1/pairs/USD_BYN/macro")
    assert res.status_code == 502


# ---------- banks ----------

@pytest.mark.asyncio
async def test_bank_rates_success(banks):
    banks.get_minsk_table.return_value = BankRatesTable(
        city="Минск", rows=[], source_note=""
    )
    res = await _get("/api/v1/banks/minsk")
    assert res.status_code == 200
    assert res.json()["city"] == "Минск"


@pytest.mark.asyncio
async def test_bank_rates_error_is_502(banks):
    banks.get_minsk_table.side_effect = RuntimeError("down")
    res = await _get("/api/v1/banks/minsk")
    assert res.status_code == 502


# ---------- gold ----------

@pytest.mark.asyncio
async def test_gold_value_error_is_400(svc):
    svc.calc_gold.side_effect = ValueError("bad currency")
    res = await _get("/api/v1/tools/gold", amount=10, currency="XXX")
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_gold_rejects_non_positive_amount(svc):
    res = await _get("/api/v1/tools/gold", amount=0)
    assert res.status_code == 422


# ---------- chart / forecast / metrics ----------

@pytest.mark.asyncio
async def test_chart_value_error_is_400(svc):
    svc.get_chart.side_effect = ValueError("bad")
    res = await _get("/api/v1/pairs/USD_BYN/chart")
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_forecast_value_error_is_400(svc):
    svc.get_forecast.side_effect = ValueError("not enough data")
    res = await _get("/api/v1/pairs/USD_BYN/forecast", days=7)
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_forecast_unexpected_error_is_502(svc):
    svc.get_forecast.side_effect = RuntimeError("model crashed")
    res = await _get("/api/v1/pairs/USD_BYN/forecast", days=7)
    assert res.status_code == 502


@pytest.mark.asyncio
async def test_forecast_days_out_of_range_is_422(svc):
    res = await _get("/api/v1/pairs/USD_BYN/forecast", days=31)
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_metrics_error_is_502(svc):
    svc.get_metrics.side_effect = RuntimeError("fail")
    res = await _get("/api/v1/pairs/USD_BYN/metrics")
    assert res.status_code == 502


@pytest.mark.asyncio
async def test_metrics_holdout_out_of_range_is_422(svc):
    res = await _get("/api/v1/pairs/USD_BYN/metrics", holdout_days=3)
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_compare_metrics_success(svc):
    svc.compare_methods.return_value = {"sarimax": {"mape": 1.0}}
    res = await _get("/api/v1/pairs/USD_BYN/metrics/compare")
    assert res.status_code == 200
    assert res.json() == {"sarimax": {"mape": 1.0}}


@pytest.mark.asyncio
async def test_compare_metrics_error_is_502(svc):
    svc.compare_methods.side_effect = RuntimeError("fail")
    res = await _get("/api/v1/pairs/USD_BYN/metrics/compare")
    assert res.status_code == 502


# ---------- news ----------

@pytest.mark.asyncio
async def test_news_success(finnhub):
    finnhub.get_market_news.return_value = []
    res = await _get("/api/v1/news")
    assert res.status_code == 200
    body = res.json()
    assert body["category"] == "general"
    assert body["articles"] == []


@pytest.mark.asyncio
async def test_news_value_error_is_400(finnhub):
    finnhub.get_market_news.side_effect = ValueError("no api key")
    res = await _get("/api/v1/news")
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_news_unexpected_error_is_502(finnhub):
    finnhub.get_market_news.side_effect = RuntimeError("down")
    res = await _get("/api/v1/news")
    assert res.status_code == 502
    assert "Finnhub" in res.json()["detail"]


# ---------- функции, вызываемые напрямую ----------

@pytest.mark.asyncio
async def test_dashboard_returns_service_result():
    service = AsyncMock()
    service.get_dashboard.return_value = "dash"
    assert await routes.dashboard(service=service) == "dash"


@pytest.mark.asyncio
async def test_get_all_latest_marks_missing_as_none():
    service = MagicMock()

    async def fake_latest(currency):
        if currency == routes.CURRENCY_CODES[0]:
            raise ValueError("нет")
        return f"rate-{currency}"

    service.get_latest_rate = fake_latest
    result = await routes.get_all_latest(service=service)

    assert set(result) == set(routes.CURRENCY_CODES)
    assert result[routes.CURRENCY_CODES[0]] is None
    assert result[routes.CURRENCY_CODES[1]] == f"rate-{routes.CURRENCY_CODES[1]}"