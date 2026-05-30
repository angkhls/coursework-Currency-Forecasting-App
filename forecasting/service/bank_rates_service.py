from domain.models import BankRatesTable, BankRow
from infrastructure.belarusbank_client import BelarusbankClient
from infrastructure.myfin_client import MyfinClient
from infrastructure.nbrb_client import NbrbApiClient


class BankRatesService:
    def __init__(
        self,
        belarusbank: BelarusbankClient,
        myfin: MyfinClient,
        nbrb: NbrbApiClient,
    ):
        self._bb = belarusbank
        self._myfin = myfin
        self._nbrb = nbrb

    async def get_minsk_table(self) -> BankRatesTable:
        rows_by_id: dict[str, BankRow] = {}

        try:
            for row in await self._myfin.fetch_bank_rows():
                rows_by_id[row.bank_id] = row
        except Exception:
            pass

        try:
            bb_data = await self._bb.fetch_city("Минск")
            bb_row = self._bb.aggregate_best(bb_data, "Беларусбанк", "belarusbank")
            if bb_row:
                rows_by_id["belarusbank"] = bb_row
        except Exception:
            pass

        order = ["belarusbank", "prior", "alfa", "bsb", "sber"]
        rows = [rows_by_id[bid] for bid in order if bid in rows_by_id]

        return BankRatesTable(
            city="Минск",
            rows=rows,
            source_note=(
                "Курсы «Сдать/Купить» в банках Минска: myfin.by (таблица банков) "
                "и API Беларусбанка. Для курсовой: полный агрегатор как myfin требует "
                "API каждого банка; мы подключаем основные банки через публичные источники."
            ),
        )
