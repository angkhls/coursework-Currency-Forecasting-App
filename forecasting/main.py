import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Корень пакета forecasting в PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent))

import asyncpg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import get_bank_rates_service, get_rate_service, router
from config import CORS_ORIGINS, POSTGRES_DSN, SQLITE_PATH, STORAGE
from infrastructure.db_repository import PostgresCurrencyRateRepository
from infrastructure.belarusbank_client import BelarusbankClient
from infrastructure.myfin_client import MyfinClient
from infrastructure.nbrb_client import NbrbApiClient
from infrastructure.sqlite_repository import SqliteCurrencyRateRepository
from service.bank_rates_service import BankRatesService
from service.rate_service import RateService

INIT_SQL = """
CREATE TABLE IF NOT EXISTS currency_rates (
    currency VARCHAR(8) NOT NULL,
    date DATE NOT NULL,
    rate DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (currency, date)
);
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    nbrb = NbrbApiClient()
    pool = None
    sqlite_repo = None

    if STORAGE == "postgres":
        pool = await asyncpg.create_pool(POSTGRES_DSN, min_size=1, max_size=5)
        async with pool.acquire() as conn:
            await conn.execute(INIT_SQL)
        repository = PostgresCurrencyRateRepository(pool)
    else:
        sqlite_repo = SqliteCurrencyRateRepository(SQLITE_PATH)
        await sqlite_repo.connect()
        repository = sqlite_repo

    service = RateService(repository=repository, nbrb_client=nbrb)

    bank_rates = BankRatesService(BelarusbankClient(), MyfinClient(), nbrb)
    app.state.rate_service = service
    app.state.bank_rates_service = bank_rates

    def _get_service() -> RateService:
        return app.state.rate_service

    def _get_banks() -> BankRatesService:
        return app.state.bank_rates_service

    app.dependency_overrides[get_rate_service] = _get_service
    app.dependency_overrides[get_bank_rates_service] = _get_banks

    # Первичная загрузка курсов при старте
    for currency in ("USD", "EUR", "RUB", "CNY"):
        try:
            await service.sync_rates(currency)  # type: ignore
        except Exception:
            pass

    yield

    await nbrb.close()
    if sqlite_repo:
        await sqlite_repo.close()
    if pool:
        await pool.close()


app = FastAPI(
    title="Currency Forecasting API",
    description="Мониторинг и прогнозирование валютных курсов (НБРБ, SARIMAX)",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok"}
