import React, { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { currencyApi } from "../api/client";
import MainChart from "../components/MainChart";
import MacroFactorsPanel from "../components/MacroFactorsPanel";
import MarketPanel from "../components/MarketPanel";
import type { ChartData, CurrencyPair, DashboardRate, ForecastResult, PeriodPreset } from "../types";
import { CURRENCY_PAIRS, PAIR_LABELS, PERIOD_LABELS } from "../types";

const PERIODS: PeriodPreset[] = ["day", "week", "month", "year"];

const Dashboard: React.FC = () => {
  const [pair, setPair] = useState<CurrencyPair>("USD_BYN");
  const [period, setPeriod] = useState<PeriodPreset>("month");
  const [forecastDays, setForecastDays] = useState(7);
  const [rates, setRates] = useState<DashboardRate[]>([]);
  const [chart, setChart] = useState<ChartData | null>(null);
  const [forecast, setForecast] = useState<ForecastResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [dashboard, chartData, forecastData] = await Promise.all([
        currencyApi.getDashboard(),
        currencyApi.getChart(pair, period),
        currencyApi.getForecast(pair, forecastDays),
      ]);
      setRates(dashboard.rates);
      setChart(chartData);
      setForecast(forecastData);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Ошибка загрузки");
    } finally {
      setLoading(false);
    }
  }, [pair, period, forecastDays]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <>
      <div className="dashboard-grid">
        <div>
          {error && <div className="alert alert--error">{error}</div>}
          <div className="glass-card" style={{ marginBottom: "1rem" }}>
            <div className="forecast-controls">
              <select className="select" value={pair} onChange={(e) => setPair(e.target.value as CurrencyPair)}>
                {CURRENCY_PAIRS.map((p) => (
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
                Прогноз SARIMAX: {forecastDays} дн.
                <input
                  type="range"
                  min={3}
                  max={21}
                  value={forecastDays}
                  onChange={(e) => setForecastDays(Number(e.target.value))}
                  style={{ display: "block", width: "120px" }}
                />
              </label>
            </div>
            {forecast?.mape != null && forecast.mape >= 0 && (
              <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", margin: "0.5rem 0 0" }}>
                Точность SARIMAX: MAPE {forecast.mape.toFixed(2)}%
                <Link to={`/pair/${pair}`} className="link-muted">
                  {" "}
                  → подробнее
                </Link>
              </p>
            )}
          </div>
          <MainChart chart={chart} forecast={forecast} loading={loading} />
          <div style={{ marginTop: "1rem" }}>
            <MacroFactorsPanel pair={pair} />
          </div>
        </div>
        <div className="widgets-column">
          <MarketPanel rates={rates} loading={loading} />
          <div className="glass-card">
            <h3>Быстрые ссылки</h3>
            <nav className="quick-links">
              <Link to="/pair/USD_BYN">График и прогноз →</Link>
              <Link to="/converter">Конвертер →</Link>
            </nav>
          </div>
        </div>
      </div>
    </>
  );
};

export default Dashboard;
