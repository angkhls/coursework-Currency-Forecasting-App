import React, { useState } from "react";
import { currencyApi } from "../api/client";
import type { CurrencyCode } from "../types";
import { CURRENCY_FLAGS } from "../types";

const CURRENCIES: CurrencyCode[] = ["USD", "EUR", "RUB", "CNY"];

const HistoryWidget: React.FC = () => {
  const [currency, setCurrency] = useState<CurrencyCode>("USD");
  const [date, setDate] = useState("");
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const lookup = async () => {
    if (!date) return;
    try {
      setError(null);
      const rate = await currencyApi.getRateOnDate(currency, date);
      setResult(
        `${CURRENCY_FLAGS[currency]} ${currency}/BYN на ${new Date(rate.date).toLocaleDateString("ru-RU")}: ${rate.rate.toFixed(4)} BYN`
      );
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Не найдено");
      setResult(null);
    }
  };

  return (
    <div className="glass-card">
      <h3>Исторические данные</h3>
      <div className="history-form">
        <select className="select" value={currency} onChange={(e) => setCurrency(e.target.value as CurrencyCode)}>
          {CURRENCIES.map((c) => (
            <option key={c} value={c}>
              {CURRENCY_FLAGS[c]} {c}
            </option>
          ))}
        </select>
        <input className="input" type="date" value={date} onChange={(e) => setDate(e.target.value)} />
        <button type="button" className="pill pill--active" onClick={lookup}>
          Показать курс
        </button>
        {result && <div className="history-result">{result}</div>}
        {error && <div className="alert alert--error">{error}</div>}
      </div>
    </div>
  );
};

export default HistoryWidget;
