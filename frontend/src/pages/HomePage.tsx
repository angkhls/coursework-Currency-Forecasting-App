import React, { useEffect, useState } from "react";
import { currencyApi } from "../api/client";
import BankRatesTable from "../components/BankRatesTable";
import MacroFactorsPanel from "../components/MacroFactorsPanel";
import RealtimeMonitor from "../components/RealtimeMonitor";
import type { CryptoRate, DashboardRate } from "../types";

const HomePage: React.FC = () => {
  const [rates, setRates] = useState<DashboardRate[]>([]);
  const [bitcoin, setBitcoin] = useState<CryptoRate | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    currencyApi
      .getDashboard()
      .then((d) => {
        setRates(d.rates);
        setBitcoin(d.bitcoin ?? null);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="home-page">
      <section className="glass-card hero-about">
        <h2>CurrencyForecastingApp</h2>
        <p className="hero-about__lead">
          Мониторинг и прогнозирование валютных курсов для Беларуси на данных{" "}
          <strong>НБРБ</strong> с прогнозом <strong>SARIMAX</strong> и индикаторами SMA/EMA.
        </p>
        <div className="steps">
          <div className="step">
            <span className="step__num">1</span>
            <div>
              <strong>Данные</strong> — официальные курсы и курсы банков (API НБРБ, Беларусбанк).
            </div>
          </div>
          <div className="step">
            <span className="step__num">2</span>
            <div>
              <strong>Анализ</strong> — графики, SMA/EMA, макро-факторы РБ, real-time панель.
            </div>
          </div>
          <div className="step">
            <span className="step__num">3</span>
            <div>
              <strong>Прогноз</strong> — SARIMAX на вкладках пар: горизонт, MAPE/RMSE.
            </div>
          </div>
        </div>
        <p className="hero-about__hint">
          Графики и прогноз по парам — в боковой панели слева. Котировки НБРБ: за 1 ед. (USD, EUR, GBP, CHF), за 10
          (CNY, PLN, AED, TRY), за 100 (RUB, UAH) — см. таблицу монитора.
        </p>
      </section>

      <div className="home-grid">
        <RealtimeMonitor rates={rates} bitcoin={bitcoin} loading={loading} />
        <MacroFactorsPanel />
      </div>

      <BankRatesTable />
    </div>
  );
};

export default HomePage;
