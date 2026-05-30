import React from "react";
import type { DashboardRate } from "../types";
import { CURRENCY_FLAGS } from "../types";

interface Props {
  rates: DashboardRate[];
  loading?: boolean;
}

const MarketPanel: React.FC<Props> = ({ rates, loading }) => (
  <div className="glass-card">
    <h3>Real-time Monitor</h3>
    {loading ? (
      <p className="loading">Загрузка…</p>
    ) : (
      <table className="market-table">
        <thead>
          <tr>
            <th>Market</th>
            <th>Price (BYN)</th>
            <th>Trend</th>
          </tr>
        </thead>
        <tbody>
          {rates.map((r) => (
            <tr key={r.currency}>
              <td>
                {CURRENCY_FLAGS[r.currency]} {r.currency}/BYN
              </td>
              <td>{r.rate.toFixed(4)}</td>
              <td className={r.change_pct != null && r.change_pct >= 0 ? "trend-up" : "trend-down"}>
                {r.change_pct != null ? `${r.change_pct > 0 ? "▲" : "▼"} ${Math.abs(r.change_pct).toFixed(2)}%` : "—"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    )}
  </div>
);

export default MarketPanel;
