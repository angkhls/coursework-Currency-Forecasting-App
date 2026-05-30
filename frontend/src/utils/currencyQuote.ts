import type { CurrencyCode, CurrencyPair } from "../types";
import { CURRENCY_QUOTE_SCALE } from "../types";

/** Официальная сумма валюты в котировке НБРБ (Cur_Scale). */
export function nbrbOfficialRate(ratePerUnit: number, currency: CurrencyCode): number {
  const scale = CURRENCY_QUOTE_SCALE[currency];
  return ratePerUnit * scale;
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
