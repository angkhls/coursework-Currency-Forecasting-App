import asyncio
import xml.etree.ElementTree as ET
from datetime import date
from typing import List, Optional

import httpx

from domain.models import MacroIndicator, MacroPanel

IMPACT_RB = {
    "nbrb_rate": "Ставка НБРБ влияет на стоимость BYN: рост ставки обычно поддерживает белорусский рубль.",
    "nbrb_inflation": "Инфляция в РБ снижает покупательную способность BYN и давит на курс через ожидания.",
    "brent": "Беларусь — экспортёр нефтепродуктов; рост Brent может поддерживать поступление валюты в экономику.",
    "gold_nbrb": "Цены НБРБ на золото отражают внутренний «защитный» спрос и ориентир для инвесторов.",
    "btc": "Bitcoin — глобальный риск-актив; рост BTC часто совпадает с аппетитом к риску на FX-рынках.",
    "reserves": "Золотовалютные резервы НБРБ — запас прочности для поддержки курса BYN.",
}


class MacroService:
    """Макро-факторы для Республики Беларусь (НБРБ и мировые сырьевые индикаторы)."""

    async def get_belarus_panel(self) -> MacroPanel:
        tasks = await asyncio.gather(
            self._fetch_nbrb_refinance(),
            self._fetch_nbrb_inflation(),
            self._fetch_yahoo("BZ=F", "brent", "Нефть Brent"),
            self._fetch_nbrb_gold(),
            self._fetch_btc(),
            self._fetch_nbrb_reserves(),
            return_exceptions=True,
        )
        indicators: List[MacroIndicator] = []
        for item in tasks:
            if isinstance(item, MacroIndicator):
                indicators.append(item)
        return MacroPanel(pair="USD_BYN", indicators=indicators)

    async def get_panel(self, pair: str = "USD_BYN") -> MacroPanel:
        return await self.get_belarus_panel()

    async def _fetch_nbrb_refinance(self) -> Optional[MacroIndicator]:
        url = "https://api.nbrb.by/refinancingrate"
        async with httpx.AsyncClient(timeout=12) as client:
            r = await client.get(url)
            r.raise_for_status()
            data = r.json()
        if not data:
            return None
        last, prev = data[-1], data[-2] if len(data) > 1 else data[-1]
        value = float(last["Value"])
        change = None
        pv = float(prev["Value"])
        if pv:
            change = round((value - pv) / pv * 100, 2)
        return MacroIndicator(
            id="nbrb_rate",
            name="Ставка рефинансирования НБРБ",
            value=value,
            unit="% годовых",
            change_pct=change,
            impact=IMPACT_RB["nbrb_rate"],
            source="api.nbrb.by",
        )

    async def _fetch_nbrb_inflation(self) -> MacroIndicator:
        """ИПЦ: публичный XML Белстат через НБРБ (если недоступен — справочный ориентир)."""
        try:
            url = "https://www.nbrb.by/api/ExInflationRates"
            async with httpx.AsyncClient(timeout=12) as client:
                r = await client.get(url)
                if r.status_code == 200:
                    data = r.json()
                    if isinstance(data, list) and data:
                        value = float(data[-1].get("Value", data[-1].get("Inflation", 5)))
                        return MacroIndicator(
                            id="nbrb_inflation",
                            name="Инфляция (РБ)",
                            value=value,
                            unit="%",
                            change_pct=None,
                            impact=IMPACT_RB["nbrb_inflation"],
                            source="НБРБ / Белстат",
                        )
        except Exception:
            pass
        return MacroIndicator(
            id="nbrb_inflation",
            name="Инфляция (РБ, ориентир)",
            value=5.5,
            unit="% г/г",
            change_pct=None,
            impact=IMPACT_RB["nbrb_inflation"],
            source="Белстат (ориентир)",
        )

    async def _fetch_nbrb_gold(self) -> Optional[MacroIndicator]:
        url = "https://api.nbrb.by/bankingots/prices"
        async with httpx.AsyncClient(timeout=12) as client:
            r = await client.get(url)
            r.raise_for_status()
            data = r.json()
        if not data:
            return None
        # Берём слиток 999 или первую позицию (цена за 1 г в BYN)
        item = data[0]
        value = float(item.get("Value") or item.get("Price") or 0)
        name = item.get("Name", "Золото (НБРБ)")
        return MacroIndicator(
            id="gold_nbrb",
            name=name[:40],
            value=round(value, 2),
            unit="BYN/г",
            change_pct=None,
            impact=IMPACT_RB["gold_nbrb"],
            source="api.nbrb.by/bankingots",
        )

    async def _fetch_nbrb_reserves(self) -> Optional[MacroIndicator]:
        try:
            url = "https://api.nbrb.by/goldreserves"
            async with httpx.AsyncClient(timeout=12) as client:
                r = await client.get(url)
                if r.status_code != 200:
                    return None
                data = r.json()
            if not data:
                return None
            last = data[-1]
            value = float(last.get("Value", 0)) / 1e9
            return MacroIndicator(
                id="reserves",
                name="Золотовалютные резервы НБРБ",
                value=round(value, 2),
                unit="млрд USD",
                change_pct=None,
                impact=IMPACT_RB["reserves"],
                source="api.nbrb.by",
            )
        except Exception:
            return None

    async def _fetch_btc(self) -> Optional[MacroIndicator]:
        return await self._fetch_yahoo("BTC-USD", "btc", "Bitcoin")

    async def _fetch_yahoo(self, symbol: str, id_key: str, name: str) -> Optional[MacroIndicator]:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        async with httpx.AsyncClient(timeout=12) as client:
            r = await client.get(
                url,
                params={"interval": "1d", "range": "5d"},
                headers={"User-Agent": "Mozilla/5.0"},
            )
            r.raise_for_status()
            closes = r.json()["chart"]["result"][0]["indicators"]["quote"][0]["close"]
        closes = [c for c in closes if c is not None]
        if not closes:
            return None
        value = float(closes[-1])
        change = None
        if len(closes) > 1 and closes[-2]:
            change = round((value - closes[-2]) / closes[-2] * 100, 2)
        unit = "USD" if id_key != "btc" else "USD"
        return MacroIndicator(
            id=id_key,
            name=name,
            value=round(value, 2),
            unit=unit,
            change_pct=change,
            impact=IMPACT_RB.get(id_key, IMPACT_RB["brent"]),
            source="Yahoo Finance",
        )
