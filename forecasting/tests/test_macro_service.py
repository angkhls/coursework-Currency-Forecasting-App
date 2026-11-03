from unittest.mock import AsyncMock, patch

import pytest

from domain.models import MacroIndicator
from service.macro_service import MacroService


class FakeResponse:
    def __init__(self, data=None, status_code=200):
        self._data = data
        self.status_code = status_code

    def json(self):
        return self._data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeClient:
    def __init__(self, outcome):
        self._outcome = outcome

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def get(self, url, **kwargs):
        if isinstance(self._outcome, Exception):
            raise self._outcome
        return self._outcome


def fake_http(outcome):
    return patch(
        "service.macro_service.httpx.AsyncClient",
        lambda *a, **k: FakeClient(outcome),
    )


def _indicator(id_: str = "x") -> MacroIndicator:
    return MacroIndicator(
        id=id_,
        name="n",
        value=1.0,
        unit="u",
        change_pct=None,
        impact="i",
        source="s",
    )


# ---------- refinance ----------

@pytest.mark.asyncio
async def test_refinance_computes_change():
    with fake_http(FakeResponse([{"Value": 9.5}, {"Value": 10}])):
        ind = await MacroService()._fetch_nbrb_refinance()
    assert ind.id == "nbrb_rate"
    assert ind.value == 10
    assert ind.change_pct == pytest.approx(5.26)


@pytest.mark.asyncio
async def test_refinance_single_point_has_zero_change():
    with fake_http(FakeResponse([{"Value": 9.5}])):
        ind = await MacroService()._fetch_nbrb_refinance()
    assert ind.change_pct == 0


@pytest.mark.asyncio
async def test_refinance_empty_returns_none():
    with fake_http(FakeResponse([])):
        assert await MacroService()._fetch_nbrb_refinance() is None


@pytest.mark.asyncio
async def test_refinance_http_error_propagates():
    with fake_http(FakeResponse([], status_code=500)):
        with pytest.raises(RuntimeError):
            await MacroService()._fetch_nbrb_refinance()


# ---------- inflation ----------

@pytest.mark.asyncio
async def test_inflation_from_api():
    with fake_http(FakeResponse([{"Value": 4.2}])):
        ind = await MacroService()._fetch_nbrb_inflation()
    assert ind.value == 4.2
    assert ind.name == "Инфляция (РБ)"


@pytest.mark.asyncio
async def test_inflation_uses_inflation_key():
    with fake_http(FakeResponse([{"Inflation": 6.1}])):
        ind = await MacroService()._fetch_nbrb_inflation()
    assert ind.value == 6.1


@pytest.mark.asyncio
async def test_inflation_fallback_on_bad_status():
    with fake_http(FakeResponse([], status_code=404)):
        ind = await MacroService()._fetch_nbrb_inflation()
    assert ind.value == 5.5
    assert "ориентир" in ind.name


@pytest.mark.asyncio
async def test_inflation_fallback_on_empty_list():
    with fake_http(FakeResponse([])):
        ind = await MacroService()._fetch_nbrb_inflation()
    assert ind.value == 5.5


@pytest.mark.asyncio
async def test_inflation_fallback_on_exception():
    with fake_http(ConnectionError("down")):
        ind = await MacroService()._fetch_nbrb_inflation()
    assert ind.value == 5.5


# ---------- gold ----------

@pytest.mark.asyncio
async def test_gold_uses_value():
    with fake_http(FakeResponse([{"Name": "Слиток 999", "Value": 123.456}])):
        ind = await MacroService()._fetch_nbrb_gold()
    assert ind.id == "gold_nbrb"
    assert ind.value == 123.46
    assert ind.name == "Слиток 999"


@pytest.mark.asyncio
async def test_gold_falls_back_to_price_and_default_name():
    with fake_http(FakeResponse([{"Price": 99.0}])):
        ind = await MacroService()._fetch_nbrb_gold()
    assert ind.value == 99.0
    assert ind.name == "Золото (НБРБ)"


@pytest.mark.asyncio
async def test_gold_truncates_long_name():
    with fake_http(FakeResponse([{"Name": "x" * 100, "Value": 1}])):
        ind = await MacroService()._fetch_nbrb_gold()
    assert len(ind.name) == 40


@pytest.mark.asyncio
async def test_gold_empty_returns_none():
    with fake_http(FakeResponse([])):
        assert await MacroService()._fetch_nbrb_gold() is None


# ---------- reserves ----------

@pytest.mark.asyncio
async def test_reserves_converted_to_billions():
    with fake_http(FakeResponse([{"Value": 8_000_000_000}])):
        ind = await MacroService()._fetch_nbrb_reserves()
    assert ind.id == "reserves"
    assert ind.value == 8.0


@pytest.mark.asyncio
async def test_reserves_bad_status_returns_none():
    with fake_http(FakeResponse([], status_code=500)):
        assert await MacroService()._fetch_nbrb_reserves() is None


@pytest.mark.asyncio
async def test_reserves_empty_returns_none():
    with fake_http(FakeResponse([])):
        assert await MacroService()._fetch_nbrb_reserves() is None


@pytest.mark.asyncio
async def test_reserves_exception_returns_none():
    with fake_http(ConnectionError("down")):
        assert await MacroService()._fetch_nbrb_reserves() is None


# ---------- yahoo / btc ----------

def _yahoo_payload(closes):
    return {"chart": {"result": [{"indicators": {"quote": [{"close": closes}]}}]}}


@pytest.mark.asyncio
async def test_yahoo_value_and_change():
    with fake_http(FakeResponse(_yahoo_payload([None, 100.0, 110.0]))):
        ind = await MacroService()._fetch_yahoo("BZ=F", "brent", "Нефть Brent")
    assert ind.value == 110.0
    assert ind.change_pct == 10.0
    assert ind.source == "Yahoo Finance"


@pytest.mark.asyncio
async def test_yahoo_single_close_has_no_change():
    with fake_http(FakeResponse(_yahoo_payload([100.0]))):
        ind = await MacroService()._fetch_yahoo("BZ=F", "brent", "Brent")
    assert ind.change_pct is None


@pytest.mark.asyncio
async def test_yahoo_all_none_returns_none():
    with fake_http(FakeResponse(_yahoo_payload([None, None]))):
        assert await MacroService()._fetch_yahoo("BZ=F", "brent", "Brent") is None


@pytest.mark.asyncio
async def test_btc_uses_yahoo():
    with fake_http(FakeResponse(_yahoo_payload([50000.0, 51000.0]))):
        ind = await MacroService()._fetch_btc()
    assert ind.id == "btc"
    assert ind.value == 51000.0


# ---------- panel ----------

@pytest.mark.asyncio
async def test_panel_keeps_only_indicators_and_ignores_failures():
    service = MacroService()
    with (
        patch.object(service, "_fetch_nbrb_refinance", AsyncMock(return_value=_indicator("a"))),
        patch.object(service, "_fetch_nbrb_inflation", AsyncMock(return_value=_indicator("b"))),
        patch.object(service, "_fetch_yahoo", AsyncMock(side_effect=RuntimeError("x"))),
        patch.object(service, "_fetch_nbrb_gold", AsyncMock(return_value=None)),
        patch.object(service, "_fetch_btc", AsyncMock(return_value=_indicator("c"))),
        patch.object(service, "_fetch_nbrb_reserves", AsyncMock(return_value=None)),
    ):
        panel = await service.get_belarus_panel()

    assert panel.pair == "USD_BYN"
    assert [i.id for i in panel.indicators] == ["a", "b", "c"]


@pytest.mark.asyncio
async def test_get_panel_delegates_to_belarus_panel():
    service = MacroService()
    sentinel = object()
    with patch.object(service, "get_belarus_panel", AsyncMock(return_value=sentinel)):
        assert await service.get_panel("USD_BYN") is sentinel