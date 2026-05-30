from datetime import date
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

CurrencyCode = Literal["USD", "EUR", "RUB", "CNY"]
CurrencyPair = Literal["USD_BYN", "EUR_BYN", "EUR_USD"]
ForecastMethod = Literal["sarimax"]
PeriodPreset = Literal["day", "week", "month", "year"]


class CurrencyRate(BaseModel):
    currency: CurrencyCode
    date: date
    rate: float


class ForecastPoint(BaseModel):
    date: date
    predicted_value: float
    lower: Optional[float] = None
    upper: Optional[float] = None


class ForecastResult(BaseModel):
    pair: CurrencyPair
    method: ForecastMethod
    forecast: List[ForecastPoint]
    mape: Optional[float] = Field(None, description="MAPE на holdout, %")
    rmse: Optional[float] = Field(None, description="RMSE на holdout")


class ChartPoint(BaseModel):
    date: date
    rate: float
    sma_20: Optional[float] = None
    ema_20: Optional[float] = None
    is_weekend: bool = False


class MacroIndicator(BaseModel):
    id: str
    name: str
    value: float
    unit: str
    change_pct: Optional[float] = None
    impact: str
    source: str = ""


class MacroPanel(BaseModel):
    pair: CurrencyPair
    indicators: List["MacroIndicator"]


class TechnicalLevels(BaseModel):
    support: float
    resistance: float


class ChartData(BaseModel):
    pair: CurrencyPair
    period: PeriodPreset
    points: List[ChartPoint]
    levels: TechnicalLevels
    y_min: float
    y_max: float


class ModelMetrics(BaseModel):
    pair: CurrencyPair
    method: ForecastMethod
    mape: float
    rmse: float
    holdout_days: int


class ConvertRequest(BaseModel):
    amount: float = Field(gt=0)
    from_currency: CurrencyCode
    to_currency: CurrencyCode


class ConvertResult(BaseModel):
    amount: float
    from_currency: CurrencyCode
    to_currency: CurrencyCode
    rate: float
    result: float
    date: date


class DashboardRate(BaseModel):
    currency: CurrencyCode
    rate: float
    date: date
    change_pct: Optional[float] = None


class CryptoRate(BaseModel):
    symbol: str
    price_usd: float
    price_byn: Optional[float] = None
    change_pct: Optional[float] = None


class BankCurrencyQuotes(BaseModel):
    """sell — банк покупает (клиент сдаёт), buy — банк продаёт (клиент покупает)."""
    sell: float
    buy: float


class BankRow(BaseModel):
    bank_id: str
    bank_name: str
    usd: BankCurrencyQuotes
    eur: BankCurrencyQuotes
    rub100: BankCurrencyQuotes


class BankRatesTable(BaseModel):
    city: str
    rows: List[BankRow]
    source_note: str = ""


class GoldCalcResult(BaseModel):
    amount: float
    currency: str
    amount_byn: float
    gold_grams: float
    price_per_gram_byn: float
    product_name: str


class DashboardResponse(BaseModel):
    rates: List[DashboardRate]
    bitcoin: Optional[CryptoRate] = None


class NewsArticle(BaseModel):
    id: int
    headline: str
    summary: str
    source: str
    url: str
    image: Optional[str] = None
    category: str
    datetime: int  # Unix timestamp


class NewsFeed(BaseModel):
    category: str
    articles: List[NewsArticle]
    source_note: str = "Данные: Finnhub Market News API"
