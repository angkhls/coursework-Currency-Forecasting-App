import React, { useCallback, useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { currencyApi } from "../api/client";
import MainChart from "../components/MainChart";
import MetricsPanel from "../components/MetricsPanel";
import type { ChartData, CurrencyPair, ForecastResult, PeriodPreset } from "../types";
import { PAIR_LABELS, PERIOD_LABELS } from "../types";

const PERIODS: PeriodPreset[] = ["week", "month", "year"];
const PAIRS: CurrencyPair[] = ["USD_BYN", "EUR_BYN", "EUR_USD"];

const ForecastPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const pair = (searchParams.get("pair") as CurrencyPair) || "USD_BYN";
  const [period, setPeriod] = useState<PeriodPreset>("month");
  const [days, setDays] = useState(14);
  const [chart, setChart] = useState<ChartData | null>(null);
  const [forecast, setForecast] = useState<ForecastResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const setPair = (p: CurrencyPair) => {
    setSearchParams({ pair: p });
  };

  const load = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [chartData, forecastData] = await Promise.all([
        currencyApi.getChart(pair, period),
        currencyApi.getForecast(pair, days),
      ]);
      setChart(chartData);
      setForecast(forecastData);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Ошибка");
    } finally {
      setLoading(false);
    }
  }, [pair, period, days]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="dashboard-grid">
      <div>
        {error && <div className="alert alert--error">{error}</div>}
        <div className="glass-card" style={{ marginBottom: "1rem" }}>
          <div className="forecast-controls">
            <select className="select" value={pair} onChange={(e) => setPair(e.target.value as CurrencyPair)}>
              {PAIRS.map((p) => (
                <option key={p} value={p}>
                  {PAIR_LABELS[p]}
                </option>
              ))}
            </select>
            <div className="pill-group">
              {PERIODS.map((p) => (
                <button
                  key={p}
                  type="button"
                  className={period === p ? "pill pill--active" : "pill"}
                  onClick={() => setPeriod(p)}
                >
                  {PERIOD_LABELS[p]}
                </button>
              ))}
            </div>
            <label style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>
              Прогноз SARIMAX: {days} календ. дн.
              <input
                type="range"
                min={3}
                max={30}
                value={days}
                onChange={(e) => setDays(Number(e.target.value))}
                style={{ display: "block", width: "140px" }}
              />
            </label>
          </div>
          {forecast?.mape != null && forecast.mape >= 0 && (
            <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", margin: "0.5rem 0 0" }}>
              Backtest SARIMAX: MAPE {forecast.mape.toFixed(2)}%, RMSE {forecast.rmse?.toFixed(4) ?? "—"}
            </p>
          )}
        </div>
        <MainChart chart={chart} forecast={forecast} loading={loading} />
      </div>
      <div className="widgets-column">
        <MetricsPanel pair={pair} />
        <div className="glass-card">
          <h3>О прогнозе</h3>
          <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", margin: 0 }}>
            Модель SARIMAX считает только рабочие дни НБРБ. На субботу и воскресенье на графике
            показывается значение последнего рабочего дня.
          </p>
        </div>
      </div>
    </div>
  );
};

export default ForecastPage;
