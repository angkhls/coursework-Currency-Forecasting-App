import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

STORAGE = os.getenv("STORAGE", "sqlite")  # sqlite | postgres
SQLITE_PATH = os.getenv("SQLITE_PATH", str(DATA_DIR / "currency.db"))

POSTGRES_DSN = os.getenv(
    "DATABASE_URL",
    "postgresql://currency_user:currency_pass@localhost:5432/currencydb",
)

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")

CORS_ORIGINS = [
    o.strip()
    for o in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    if o.strip()
]
