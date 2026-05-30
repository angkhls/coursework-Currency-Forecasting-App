import React, { useEffect, useState } from "react";
import { currencyApi } from "../api/client";
import type { CurrencyPair, ModelMetrics } from "../types";
import { PAIR_LABELS } from "../types";

interface Props {
  pair: CurrencyPair;
}

const MetricsPanel: React.FC<Props> = ({ pair }) => {
  const [metrics, setMetrics] = useState<ModelMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        setLoading(true);
        const data = await currencyApi.getMetrics(pair);
        if (!cancelled) setMetrics(data);
      } catch {
        if (!cancelled) setMetrics(null);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [pair]);

  return (
    <div className="glass-card">
      <h3>Точность модели — {PAIR_LABELS[pair]}</h3>
      {loading ? (
        <p className="loading">Расчёт MAPE/RMSE…</p>
      ) : (
        <div className="metrics-grid">
          <div className="metric-box">
            <div className="metric-box__value">
              {metrics && metrics.mape >= 0 ? `${metrics.mape.toFixed(2)}%` : "—"}
            </div>
            <div className="metric-box__label">SARIMAX MAPE</div>
            {metrics && metrics.rmse >= 0 && (
              <div className="metric-box__label">RMSE: {metrics.rmse.toFixed(4)}</div>
            )}
          </div>
        </div>
      )}
      <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "0.75rem" }}>
        Holdout 30 дней: модель обучается на прошлом, прогноз сравнивается с фактом.
      </p>
    </div>
  );
};

export default MetricsPanel;
