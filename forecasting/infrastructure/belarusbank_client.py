import httpx
from typing import Any, List, Optional

from domain.models import BankCurrencyQuotes, BankRatesTable, BankRow


class BelarusbankClient:
    """
    Курсы обмена в отделениях Беларусбанка (официальный API).
    USD_in — банк покупает (клиент «сдаёт» валюту), USD_out — банк продаёт.
    """

    BASE = "https://belarusbank.by/api/kursExchange"

    async def fetch_city(self, city: str = "Минск") -> List[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(self.BASE, params={"city": city})
            r.raise_for_status()
            data = r.json()
        if isinstance(data, dict):
            data = data.get("kurs_exchange") or data.get("data") or []
        return data if isinstance(data, list) else []

    def aggregate_best(self, rows: List[dict[str, Any]], bank_name: str, bank_id: str) -> Optional[BankRow]:
        if not rows:
            return None

        def best_pair(in_key: str, out_key: str) -> BankCurrencyQuotes:
            ins = [float(x[in_key]) for x in rows if x.get(in_key) not in (None, "", "0", 0)]
            outs = [float(x[out_key]) for x in rows if x.get(out_key) not in (None, "", "0", 0)]
            return BankCurrencyQuotes(
                sell=max(ins) if ins else 0.0,
                buy=min(outs) if outs else 0.0,
            )

        return BankRow(
            bank_id=bank_id,
            bank_name=bank_name,
            usd=best_pair("USD_in", "USD_out"),
            eur=best_pair("EUR_in", "EUR_out"),
            rub100=best_pair("RUB_in", "RUB_out"),
        )
