import React, { useCallback, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { currencyApi } from "../api/client";
import MainChart from "../components/MainChart";
import MetricsPanel from "../components/MetricsPanel";
import type { ChartData, CurrencyPair, ForecastResult, PeriodPreset } from "../types";
import { PAIR_LABELS, PERIOD_LABELS } from "../types";

const PERIODS: PeriodPreset[] = ["week", "month", "year"];

const PairPage: React.FC = () => {
  const { pair: pairParam } = useParams<{ pair: string }>();
  const pair = (pairParam ?? "USD_BYN") as CurrencyPair;
  const [period, setPeriod] = useState<PeriodPreset>("month");
  const [days, setDays] = useState(14);
  const [chart, setChart] = useState<ChartData | null>(null);
  const [forecast, setForecast] = useState<ForecastResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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
    <div className="pair-page">
      {error && <div className="alert alert--error">{error}</div>}
      <div className="glass-card pair-controls">
        <h2 className="pair-title">{PAIR_LABELS[pair]}</h2>
        <div className="forecast-controls">
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
          <label className="range-label">
            Прогноз SARIMAX: {days} календ. дн.
            <input type="range" min={3} max={30} value={days} onChange={(e) => setDays(Number(e.target.value))} />
          </label>
        </div>
        {forecast && forecast.mape != null && forecast.mape >= 0 && (
          <div className="accuracy-banner">
            Точность SARIMAX на тестовом периоде (последние 30 дней): MAPE{" "}
            <span className="accuracy-value">{forecast.mape.toFixed(2)}%</span>, RMSE{" "}
            <span className="accuracy-value">{forecast.rmse?.toFixed(4) ?? "—"}</span>
          </div>
        )}
      </div>
      <MainChart chart={chart} forecast={forecast} loading={loading} large />
      <div className="pair-metrics-row">
        <MetricsPanel pair={pair} />
      </div>
    </div>
  );
};

export default PairPage;
