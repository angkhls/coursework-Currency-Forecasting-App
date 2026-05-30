export type CurrencyCode = "USD" | "EUR" | "RUB" | "CNY";
export type CurrencyPair = "USD_BYN" | "EUR_BYN" | "EUR_USD";
export type ForecastMethod = "sarimax";
export type PeriodPreset = "day" | "week" | "month" | "year";

export interface CurrencyRate {
  currency: CurrencyCode;
  date: string;
  rate: number;
}

export interface ForecastPoint {
  date: string;
  predicted_value: number;
  lower?: number | null;
  upper?: number | null;
}

export interface ForecastResult {
  pair: CurrencyPair;
  method: ForecastMethod;
  forecast: ForecastPoint[];
  mape?: number | null;
  rmse?: number | null;
}

export interface ChartPoint {
  date: string;
  rate: number;
  sma_20?: number | null;
  ema_20?: number | null;
  is_weekend?: boolean;
}

export interface ChartData {
  pair: CurrencyPair;
  period: PeriodPreset;
  points: ChartPoint[];
  levels: { support: number; resistance: number };
  y_min: number;
  y_max: number;
}

export interface MacroIndicator {
  id: string;
  name: string;
  value: number;
  unit: string;
  change_pct?: number | null;
  impact: string;
  source: string;
}

export interface MacroPanel {
  pair: CurrencyPair;
  indicators: MacroIndicator[];
}

export interface ModelMetrics {
  pair: CurrencyPair;
  method: ForecastMethod;
  mape: number;
  rmse: number;
  holdout_days: number;
}

export interface DashboardRate {
  currency: CurrencyCode;
  rate: number;
  date: string;
  change_pct?: number | null;
}

export interface CryptoRate {
  symbol: string;
  price_usd: number;
  price_byn?: number | null;
  change_pct?: number | null;
}

export interface DashboardResponse {
  rates: DashboardRate[];
  bitcoin?: CryptoRate | null;
}

export interface BankCurrencyQuotes {
  sell: number;
  buy: number;
}

export interface BankRow {
  bank_id: string;
  bank_name: string;
  usd: BankCurrencyQuotes;
  eur: BankCurrencyQuotes;
  rub100: BankCurrencyQuotes;
}

export interface BankRatesTable {
  city: string;
  rows: BankRow[];
  source_note: string;
}

export interface GoldCalcResult {
  amount: number;
  currency: CurrencyCode;
  amount_byn: number;
  gold_grams: number;
  price_per_gram_byn: number;
  product_name: string;
}

export interface ConvertResult {
  amount: number;
  from_currency: CurrencyCode;
  to_currency: CurrencyCode;
  rate: number;
  result: number;
  date: string;
}

export type AllLatestRates = Record<CurrencyCode, CurrencyRate | null>;

export type NewsCategory = "forex" | "general" | "crypto" | "merger";

export interface NewsArticle {
  id: number;
  headline: string;
  summary: string;
  source: string;
  url: string;
  image?: string | null;
  category: string;
  datetime: number;
}

export interface NewsFeed {
  category: string;
  articles: NewsArticle[];
  source_note: string;
}

export const PAIR_LABELS: Record<CurrencyPair, string> = {
  USD_BYN: "USD / BYN",
  EUR_BYN: "EUR / BYN",
  EUR_USD: "EUR / USD",
};

export const CURRENCY_FLAGS: Record<CurrencyCode, string> = {
  USD: "🇺🇸",
  EUR: "🇪🇺",
  RUB: "🇷🇺",
  CNY: "🇨🇳",
};

export const PERIOD_LABELS: Record<PeriodPreset, string> = {
  day: "День",
  week: "Неделя",
  month: "Месяц",
  year: "Год",
};
