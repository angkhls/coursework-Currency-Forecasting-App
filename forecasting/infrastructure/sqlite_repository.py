import aiosqlite
from datetime import date
from typing import List, Optional

from domain.models import CurrencyRate, CurrencyCode
from domain.repositories import CurrencyRateRepository

SCHEMA = """
CREATE TABLE IF NOT EXISTS currency_rates (
    currency TEXT NOT NULL,
    date TEXT NOT NULL,
    rate REAL NOT NULL,
    PRIMARY KEY (currency, date)
);
CREATE INDEX IF NOT EXISTS idx_currency_date ON currency_rates(currency, date);
"""


class SqliteCurrencyRateRepository(CurrencyRateRepository):
    def __init__(self, db_path: str):
        self._db_path = db_path
        self._db: Optional[aiosqlite.Connection] = None

    async def connect(self) -> None:
        self._db = await aiosqlite.connect(self._db_path)
        self._db.row_factory = aiosqlite.Row
        await self._db.executescript(SCHEMA)
        await self._db.commit()

    async def close(self) -> None:
        if self._db:
            await self._db.close()
            self._db = None

    async def save(self, rate: CurrencyRate) -> None:
        assert self._db
        await self._db.execute(
            """
            INSERT INTO currency_rates (currency, date, rate) VALUES (?, ?, ?)
            ON CONFLICT(currency, date) DO UPDATE SET rate = excluded.rate
            """,
            (rate.currency, rate.date.isoformat(), rate.rate),
        )
        await self._db.commit()

    async def save_many(self, rates: List[CurrencyRate]) -> None:
        if not rates:
            return
        assert self._db
        await self._db.executemany(
            """
            INSERT INTO currency_rates (currency, date, rate) VALUES (?, ?, ?)
            ON CONFLICT(currency, date) DO UPDATE SET rate = excluded.rate
            """,
            [(r.currency, r.date.isoformat(), r.rate) for r in rates],
        )
        await self._db.commit()

    async def get_by_currency_and_date(
        self, currency: CurrencyCode, target_date: date
    ) -> Optional[CurrencyRate]:
        assert self._db
        async with self._db.execute(
            "SELECT currency, date, rate FROM currency_rates WHERE currency = ? AND date = ?",
            (currency, target_date.isoformat()),
        ) as cursor:
            row = await cursor.fetchone()
        if not row:
            return None
        return CurrencyRate(
            currency=row["currency"],
            date=date.fromisoformat(row["date"]),
            rate=row["rate"],
        )

    async def get_history(
        self, currency: CurrencyCode, from_date: date, to_date: date
    ) -> List[CurrencyRate]:
        assert self._db
        async with self._db.execute(
            """
            SELECT currency, date, rate FROM currency_rates
            WHERE currency = ? AND date BETWEEN ? AND ?
            ORDER BY date ASC
            """,
            (currency, from_date.isoformat(), to_date.isoformat()),
        ) as cursor:
            rows = await cursor.fetchall()
        return [
            CurrencyRate(
                currency=row["currency"],
                date=date.fromisoformat(row["date"]),
                rate=row["rate"],
            )
            for row in rows
        ]

    async def get_latest(self, currency: CurrencyCode) -> Optional[CurrencyRate]:
        assert self._db
        async with self._db.execute(
            """
            SELECT currency, date, rate FROM currency_rates
            WHERE currency = ? ORDER BY date DESC LIMIT 1
            """,
            (currency,),
        ) as cursor:
            row = await cursor.fetchone()
        if not row:
            return None
        return CurrencyRate(
            currency=row["currency"],
            date=date.fromisoformat(row["date"]),
            rate=row["rate"],
        )

    async def delete_currency(self, currency: CurrencyCode) -> None:
        assert self._db
        await self._db.execute(
            "DELETE FROM currency_rates WHERE currency = ?",
            (currency,),
        )
        await self._db.commit()
