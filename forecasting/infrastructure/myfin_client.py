import re
from typing import List, Optional

import httpx
from bs4 import BeautifulSoup

from domain.models import BankCurrencyQuotes, BankRow

# Банки для отображения (как на myfin)
MYFIN_BANK_MAP = {
    "belarusbank": ("Беларусбанк", re.compile(r"^Беларусбанк$", re.I)),
    "prior": ("Приорбанк", re.compile(r"^Приорбанк$", re.I)),
    "alfa": ("Альфа Банк", re.compile(r"^Альфа\s*Банк$", re.I)),
    "bsb": ("БСБ Банк", re.compile(r"^БСБ\s*Банк$", re.I)),
    "sber": ("Сбер Банк", re.compile(r"^Сбер\s*Банк$", re.I)),
}


class MyfinClient:
    """Курсы банков Минска с myfin.by (публичная таблица «В банках»)."""

    URL = "https://myfin.by/currency/minsk"

    async def fetch_bank_rows(self) -> List[BankRow]:
        async with httpx.AsyncClient(
            timeout=20,
            headers={"User-Agent": "Mozilla/5.0 (compatible; CurrencyForecastingApp/1.0)"},
            follow_redirects=True,
        ) as client:
            r = await client.get(self.URL)
            r.raise_for_status()
            return self._parse_html(r.text)

    def _parse_html(self, html: str) -> List[BankRow]:
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table")
        if not table:
            return []

        found: dict[str, BankRow] = {}
        for tr in table.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) < 7:
                continue
            name = tds[0].get_text(strip=True)
            if not name or len(name) > 60:
                continue

            for bank_id, (display_name, pattern) in MYFIN_BANK_MAP.items():
                if not pattern.match(name):
                    continue
                quotes = self._parse_quotes(tds)
                if quotes:
                    found[bank_id] = BankRow(
                        bank_id=bank_id,
                        bank_name=display_name,
                        usd=quotes[0],
                        eur=quotes[1],
                        rub100=quotes[2],
                    )
                break

        return list(found.values())

    @staticmethod
    def _parse_quotes(tds) -> Optional[tuple[BankCurrencyQuotes, BankCurrencyQuotes, BankCurrencyQuotes]]:
        def cell(i: int) -> float:
            raw = tds[i].get_text(strip=True).replace(",", ".")
            try:
                v = float(raw)
                return v if v > 0 else 0.0
            except ValueError:
                return 0.0

        usd = BankCurrencyQuotes(sell=cell(1), buy=cell(2))
        eur = BankCurrencyQuotes(sell=cell(3), buy=cell(4))
        rub = BankCurrencyQuotes(sell=cell(5), buy=cell(6))
        if not any([usd.sell, usd.buy, eur.sell, eur.buy, rub.sell, rub.buy]):
            return None
        return usd, eur, rub
