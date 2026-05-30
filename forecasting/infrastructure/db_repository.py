import asyncpg
from datetime import date
from typing import List, Optional
from domain.models import CurrencyRate, CurrencyCode
from domain.repositories import CurrencyRateRepository

# ─────────────────────────────────────────────
# ПАТТЕРН: Repository — конкретная реализация
#
# Реализует абстрактный CurrencyRateRepository
# для PostgreSQL через библиотеку asyncpg.
#
# Весь SQL спрятан здесь. Сервисы и роуты
# работают только с абстракцией — они не знают
# что данные хранятся в PostgreSQL.
# ─────────────────────────────────────────────


class PostgresCurrencyRateRepository(CurrencyRateRepository):
    """
    Реализация репозитория курсов через PostgreSQL.
    asyncpg — самая быстрая async библиотека для PostgreSQL.
    """

    def __init__(self, pool: asyncpg.Pool):
        # pool — пул соединений с БД.
        # Пул переиспользует соединения вместо создания нового
        # на каждый запрос — это намного эффективнее.
        self._pool = pool

    async def save(self, rate: CurrencyRate) -> None:
        """
        Сохранить курс. Если запись на эту дату уже есть —
        обновить (INSERT ... ON CONFLICT DO UPDATE).
        Это называется UPSERT.
        """
        async with self._pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO currency_rates (currency, date, rate)
                VALUES ($1, $2, $3)
                ON CONFLICT (currency, date)
                DO UPDATE SET rate = EXCLUDED.rate
            """, rate.currency, rate.date, rate.rate)

    async def save_many(self, rates: List[CurrencyRate]) -> None:
        """
        Сохранить много курсов за один запрос (bulk upsert).
        Используем executemany — это быстрее чем N отдельных запросов.
        """
        async with self._pool.acquire() as conn:
            await conn.executemany("""
                INSERT INTO currency_rates (currency, date, rate)
                VALUES ($1, $2, $3)
                ON CONFLICT (currency, date)
                DO UPDATE SET rate = EXCLUDED.rate
            """, [(r.currency, r.date, r.rate) for r in rates])

    async def get_by_currency_and_date(
        self,
        currency: CurrencyCode,
        target_date: date
    ) -> Optional[CurrencyRate]:
        """
        Найти курс по валюте и дате.
        Возвращает None если не найдено.
        """
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT currency, date, rate
                FROM currency_rates
                WHERE currency = $1 AND date = $2
            """, currency, target_date)

        if row is None:
            return None

        # asyncpg возвращает Record — преобразуем в нашу сущность
        return CurrencyRate(
            currency=row["currency"],
            date=row["date"],
            rate=row["rate"]
        )

    async def get_history(
        self,
        currency: CurrencyCode,
        from_date: date,
        to_date: date
    ) -> List[CurrencyRate]:
        """
        Получить историю курсов за период.
        ORDER BY date ASC — нужен для SARIMAX (временной ряд).
        """
        async with self._pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT currency, date, rate
                FROM currency_rates
                WHERE currency = $1
                  AND date BETWEEN $2 AND $3
                ORDER BY date ASC
            """, currency, from_date, to_date)

        return [
            CurrencyRate(
                currency=row["currency"],
                date=row["date"],
                rate=row["rate"]
            )
            for row in rows
        ]

    async def get_latest(
        self,
        currency: CurrencyCode
    ) -> Optional[CurrencyRate]:
        """
        Получить самый свежий курс валюты.
        Используется чтобы понять — нужно ли обновлять данные.
        """
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT currency, date, rate
                FROM currency_rates
                WHERE currency = $1
                ORDER BY date DESC
                LIMIT 1
            """, currency)

        if row is None:
            return None

        return CurrencyRate(
            currency=row["currency"],
            date=row["date"],
            rate=row["rate"]
        )

    async def delete_currency(self, currency: CurrencyCode) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM currency_rates WHERE currency = $1",
                currency,
            )