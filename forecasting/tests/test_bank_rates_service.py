from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from service.bank_rates_service import BankRatesService


def _row(bank_id: str):
    return SimpleNamespace(bank_id=bank_id)


@pytest.fixture(autouse=True)
def plain_table():
    """BankRatesTable заменяем простым контейнером, чтобы не зависеть от полей BankRow."""
    with patch(
        "service.bank_rates_service.BankRatesTable",
        side_effect=lambda **kw: SimpleNamespace(**kw),
    ):
        yield


def _service(myfin_rows=None, myfin_error=None, bb_row=None, bb_error=None):
    myfin = MagicMock()
    myfin.fetch_bank_rows = AsyncMock(
        return_value=myfin_rows or [], side_effect=myfin_error
    )
    bb = MagicMock()
    bb.fetch_city = AsyncMock(return_value={"raw": 1}, side_effect=bb_error)
    bb.aggregate_best = MagicMock(return_value=bb_row)
    return BankRatesService(belarusbank=bb, myfin=myfin, nbrb=AsyncMock()), bb


@pytest.mark.asyncio
async def test_rows_are_sorted_in_fixed_order():
    service, _ = _service(
        myfin_rows=[_row("sber"), _row("prior"), _row("alfa")],
        bb_row=_row("belarusbank"),
    )
    table = await service.get_minsk_table()

    assert table.city == "Минск"
    assert [r.bank_id for r in table.rows] == ["belarusbank", "prior", "alfa", "sber"]


@pytest.mark.asyncio
async def test_unknown_banks_are_dropped():
    service, _ = _service(myfin_rows=[_row("prior"), _row("some-other-bank")])
    table = await service.get_minsk_table()
    assert [r.bank_id for r in table.rows] == ["prior"]


@pytest.mark.asyncio
async def test_belarusbank_failure_keeps_myfin_rows():
    service, _ = _service(myfin_rows=[_row("prior")], bb_error=RuntimeError("down"))
    table = await service.get_minsk_table()
    assert [r.bank_id for r in table.rows] == ["prior"]


@pytest.mark.asyncio
async def test_myfin_failure_keeps_belarusbank_row():
    service, _ = _service(myfin_error=RuntimeError("down"), bb_row=_row("belarusbank"))
    table = await service.get_minsk_table()
    assert [r.bank_id for r in table.rows] == ["belarusbank"]


@pytest.mark.asyncio
async def test_belarusbank_without_best_row_is_skipped():
    service, bb = _service(myfin_rows=[_row("alfa")], bb_row=None)
    table = await service.get_minsk_table()

    bb.aggregate_best.assert_called_once()
    assert [r.bank_id for r in table.rows] == ["alfa"]


@pytest.mark.asyncio
async def test_all_sources_failing_gives_empty_table():
    service, _ = _service(myfin_error=RuntimeError("x"), bb_error=RuntimeError("y"))
    table = await service.get_minsk_table()
    assert table.rows == []