import React, { useEffect, useState } from "react";
import { currencyApi } from "../api/client";
import MarketPanel from "../components/MarketPanel";
import type { DashboardRate } from "../types";

const MarketPage: React.FC = () => {
  const [rates, setRates] = useState<DashboardRate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    currencyApi
      .getDashboard()
      .then((d) => setRates(d.rates))
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="page-single">
      {error && <div className="alert alert--error">{error}</div>}
      <MarketPanel rates={rates} loading={loading} />
      <div className="glass-card" style={{ marginTop: "1rem" }}>
        <h3>Источник</h3>
        <p style={{ fontSize: "0.9rem", color: "var(--text-muted)", margin: 0 }}>
          Официальные курсы Национального банка Республики Беларусь (api.nbrb.by). Обновление при
          каждом запросе с подгрузкой недостающих дней в локальную базу.
        </p>
      </div>
    </div>
  );
};

export default MarketPage;
