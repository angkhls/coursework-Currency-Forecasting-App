import httpx
from datetime import date, timedelta
from typing import List
from domain.currencies import NBRB_CURRENCY_IDS, NBRB_QUOTE_SCALE
from domain.models import CurrencyRate, CurrencyCode

# ─────────────────────────────────────────────
# ПАТТЕРН: Adapter (Адаптер)
#
# NBRB отдаёт данные в своём формате.
# Наш адаптер преобразует их в наши сущности (CurrencyRate).
# Остальной код ничего не знает о формате NBRB —
# он работает только с CurrencyRate.
# ─────────────────────────────────────────────


class NbrbApiClient:
    """
    Клиент для получения курсов валют с API Национального
    банка Республики Беларусь (api.nbrb.by).

    Инкапсулирует всю логику работы с внешним API:
    - формирование URL
    - HTTP запросы
    - преобразование ответа в наши сущности
    - обработка ошибок
    """

    BASE_URL = "https://api.nbrb.by/exrates"

    def __init__(self):
        # httpx.AsyncClient — асинхронный HTTP клиент.
        # timeout=10 — ждём ответа не более 10 секунд.
        self._client = httpx.AsyncClient(timeout=10)

    async def get_rate(
        self,
        currency: CurrencyCode,
        target_date: date
    ) -> CurrencyRate:
        """
        Получить курс одной валюты на конкретную дату.

        NBRB endpoint: GET /exrates/rates/{currency_id}?ondate=YYYY-MM-DD&parammode=1
        """
        # parammode=2 — поиск по коду валюты (Cur_Abbreviation); dynamics — по Cur_ID из NBRB_CURRENCY_IDS
        url = f"{self.BASE_URL}/rates/{currency}"
        params = {
            "ondate": target_date.isoformat(),
            "parammode": 2,
        }

        response = await self._client.get(url, params=params)
        response.raise_for_status()  # бросит исключение если не 200 OK

        data = response.json()
        # Cur_Scale: для RUB курс за 100 ед., для CNY за 10 — нормализуем к 1 единице
        scale = data.get("Cur_Scale", 1) or 1
        return CurrencyRate(
            currency=currency,
            date=target_date,
            rate=data["Cur_OfficialRate"] / scale,
        )

    async def get_rates_for_period(
        self,
        currency: CurrencyCode,
        from_date: date,
        to_date: date
    ) -> List[CurrencyRate]:
        """
        Получить курсы валюты за период.

        NBRB endpoint: GET /exrates/rates/dynamics/{currency_id}
                       ?startDate=YYYY-MM-DD&endDate=YYYY-MM-DD
        """
        currency_id = NBRB_CURRENCY_IDS[currency]
        url = f"{self.BASE_URL}/rates/dynamics/{currency_id}"
        params = {
            "startDate": from_date.isoformat(),
            "endDate": to_date.isoformat(),
        }

        response = await self._client.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        # NBRB возвращает список:
        # [{"Cur_ID": 431, "Date": "2024-01-15T00:00:00", "Cur_OfficialRate": 3.2541}, ...]
        # dynamics не возвращает Cur_Scale — берём из справочника НБРБ
        default_scale = NBRB_QUOTE_SCALE.get(currency, 1)
        return [
            CurrencyRate(
                currency=currency,
                date=date.fromisoformat(item["Date"][:10]),
                rate=item["Cur_OfficialRate"]
                / (item.get("Cur_Scale") or default_scale),
            )
            for item in data
        ]

    async def get_last_n_days(
        self,
        currency: CurrencyCode,
        days: int = 365
    ) -> List[CurrencyRate]:
        """
        Получить курсы за последние N дней.
        Удобный метод для загрузки истории перед прогнозом.
        """
        to_date = date.today()
        from_date = to_date - timedelta(days=days)
        return await self.get_rates_for_period(currency, from_date, to_date)

    async def close(self):
        """Закрыть HTTP соединение. Вызывать при завершении работы."""
        await self._client.aclose()