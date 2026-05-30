import type { CurrencyCode, CurrencyPair } from "../types";
import { CURRENCY_QUOTE_SCALE } from "../types";

/** Официальная сумма валюты в котировке НБРБ (Cur_Scale). */
export function nbrbOfficialRate(ratePerUnit: number, currency: CurrencyCode): number {
  const scale = CURRENCY_QUOTE_SCALE[currency];
  return ratePerUnit * scale;
}

/** Курс для графика — в официальном масштабе НБРБ (100 RUB, 10 TRY и т.д.). */
export function chartRate(ratePerUnit: number, currency: CurrencyCode): number {
  return nbrbOfficialRate(ratePerUnit, currency);
}

/** Подпись оси Y на графике. */
export function chartYAxisLabel(currency: CurrencyCode): string {
  const scale = CURRENCY_QUOTE_SCALE[currency];
  if (scale === 1) return `BYN за 1 ${currency}`;
  return `BYN за ${scale} ${currency}`;
}

/** Как публикует НБРБ: «100 RUB = 3.8720 BYN». */
export function formatNbrbQuote(currency: CurrencyCode, ratePerUnit: number): string {
  const scale = CURRENCY_QUOTE_SCALE[currency];
  const official = nbrbOfficialRate(ratePerUnit, currency);
  if (scale === 1) {
    return `1 ${currency} = ${official.toFixed(4)} BYN`;
  }
  return `${scale} ${currency} = ${official.toFixed(4)} BYN`;
}

/** Для валют с масштабом > 1 — пересчёт за одну единицу (внутренний курс приложения). */
export function formatPerUnitNote(currency: CurrencyCode, ratePerUnit: number): string | null {
  const scale = CURRENCY_QUOTE_SCALE[currency];
  if (scale === 1) return null;
  return `1 ${currency} ≈ ${ratePerUnit.toFixed(6)} BYN`;
}

export function baseCurrencyFromPair(pair: CurrencyPair): CurrencyCode {
  return pair.split("_")[0] as CurrencyCode;
}
