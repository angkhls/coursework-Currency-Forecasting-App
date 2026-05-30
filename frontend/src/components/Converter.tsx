import React, { useState } from "react";
import { currencyApi } from "../api/client";
import type { CurrencyCode } from "../types";
import { CURRENCY_FLAGS } from "../types";

const CURRENCIES: CurrencyCode[] = ["USD", "EUR", "RUB", "CNY"];

const Converter: React.FC = () => {
  const [amount, setAmount] = useState("100");
  const [from, setFrom] = useState<CurrencyCode>("USD");
  const [to, setTo] = useState<CurrencyCode>("EUR");
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleConvert = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await currencyApi.convert(parseFloat(amount), from, to);
      setResult(`${data.result.toFixed(4)} ${to} (курс: ${data.rate.toFixed(6)})`);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Ошибка");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-card">
      <h3>Конвертер валют</h3>
      <div className="converter-form">
        <input
          className="input"
          type="number"
          min="0"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
        />
        <div className="converter-row">
          <select className="select" value={from} onChange={(e) => setFrom(e.target.value as CurrencyCode)}>
            {CURRENCIES.map((c) => (
              <option key={c} value={c}>
                {CURRENCY_FLAGS[c]} {c}
              </option>
            ))}
          </select>
          <span>→</span>
          <select className="select" value={to} onChange={(e) => setTo(e.target.value as CurrencyCode)}>
            {CURRENCIES.map((c) => (
              <option key={c} value={c}>
                {CURRENCY_FLAGS[c]} {c}
              </option>
            ))}
          </select>
        </div>
        <button type="button" className="pill pill--active" onClick={handleConvert} disabled={loading}>
          {loading ? "Считаем…" : "Конвертировать"}
        </button>
        {result && <div className="converter-result">{result}</div>}
        {error && <div className="alert alert--error">{error}</div>}
      </div>
    </div>
  );
};

export default Converter;
