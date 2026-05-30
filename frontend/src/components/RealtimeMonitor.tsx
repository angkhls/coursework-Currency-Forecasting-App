import React from "react";
import type { CryptoRate, DashboardRate } from "../types";
import { CURRENCY_FLAGS } from "../types";
import { formatNbrbQuote, formatPerUnitNote } from "../utils/currencyQuote";

interface Props {
  rates: DashboardRate[];
  bitcoin: CryptoRate | null | undefined;
  loading?: boolean;
}

const RealtimeMonitor: React.FC<Props> = ({ rates, bitcoin, loading }) => (
  <div className="glass-card">
    <h3>Real-time Monitor</h3>
    {loading ? (
      <p className="loading">Загрузка…</p>
    ) : (
      <table className="market-table">
        <thead>
          <tr>
            <th>Актив</th>
            <th>Курс НБРБ</th>
            <th>Изм. 7д</th>
          </tr>
        </thead>
        <tbody>
          {rates.map((r) => {
            const perUnit = formatPerUnitNote(r.currency, r.rate);
            return (
            <tr key={r.currency}>
              <td>
                {CURRENCY_FLAGS[r.currency]} {r.currency}/BYN
              </td>
              <td className="quote-cell">
                <div>{formatNbrbQuote(r.currency, r.rate)}</div>
                {perUnit && <div className="quote-cell__sub">{perUnit}</div>}
              </td>
              <td className={r.change_pct != null && r.change_pct >= 0 ? "trend-up" : "trend-down"}>
                {r.change_pct != null ? `${r.change_pct > 0 ? "▲" : "▼"} ${Math.abs(r.change_pct).toFixed(2)}%` : "—"}
              </td>
            </tr>
          );
          })}
          {bitcoin && (
            <tr>
              <td>₿ Bitcoin</td>
              <td>
                {bitcoin.price_byn?.toLocaleString("ru-RU")} BYN
                <span className="btc-usd"> (${bitcoin.price_usd.toLocaleString("ru-RU")})</span>
              </td>
              <td className={bitcoin.change_pct != null && bitcoin.change_pct >= 0 ? "trend-up" : "trend-down"}>
                {bitcoin.change_pct != null ? `${bitcoin.change_pct > 0 ? "▲" : "▼"} ${Math.abs(bitcoin.change_pct)}%` : "—"}
              </td>
            </tr>
          )}
        </tbody>
      </table>
    )}
    <p className="monitor-foot">Курсы валют — НБРБ; BTC — Yahoo Finance × USD/BYN НБРБ</p>
  </div>
);

export default RealtimeMonitor;
