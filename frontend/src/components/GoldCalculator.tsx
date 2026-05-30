import React, { useState } from "react";
import { currencyApi } from "../api/client";
import type { CurrencyCode } from "../types";
import { CURRENCY_FLAGS } from "../types";

const GoldCalculator: React.FC = () => {
  const [amount, setAmount] = useState("1000");
  const [currency, setCurrency] = useState<CurrencyCode | "BYN">("BYN");
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const calc = async () => {
    try {
      setError(null);
      const data = await currencyApi.calcGold(parseFloat(amount), currency);
      setResult(
        `На ${data.amount_byn.toFixed(2)} BYN можно купить ~${data.gold_grams} г золота (${data.product_name}, ${data.price_per_gram_byn} BYN/г)`
      );
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Ошибка");
      setResult(null);
    }
  };

  return (
    <div className="glass-card">
      <h3>Сколько золота купить?</h3>
      <p style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginTop: 0 }}>
        По учётным ценам НБРБ на драгметаллы — для ориентира, не оферта банка.
      </p>
      <div className="converter-form">
        <input className="input" type="number" min="0" value={amount} onChange={(e) => setAmount(e.target.value)} />
        <select className="select" value={currency} onChange={(e) => setCurrency(e.target.value as CurrencyCode | "BYN")}>
          {(["USD", "EUR", "RUB"] as CurrencyCode[]).map((c) => (
            <option key={c} value={c}>
              {CURRENCY_FLAGS[c]} {c}
            </option>
          ))}
          <option value="BYN">🇧🇾 BYN</option>
        </select>
        <button type="button" className="pill pill--active" onClick={calc}>
          Рассчитать
        </button>
        {result && <div className="history-result">{result}</div>}
        {error && <div className="alert alert--error">{error}</div>}
      </div>
    </div>
  );
};

export default GoldCalculator;
