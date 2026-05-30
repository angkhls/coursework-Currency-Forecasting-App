import React, { useEffect, useState } from "react";
import { currencyApi } from "../api/client";
import type { MacroPanel } from "../types";

const MacroFactorsPanel: React.FC = () => {
  const [panel, setPanel] = useState<MacroPanel | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        setLoading(true);
        const data = await currencyApi.getMacroBelarus();
        if (!cancelled) setPanel(data);
      } catch {
        if (!cancelled) setPanel(null);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="glass-card macro-panel">
      <h3>Макро-факторы — Республика Беларусь</h3>
      <p className="macro-panel__intro">
        Ставка НБРБ, инфляция, нефть и золото — факторы, влияющие на BYN и кросс-курсы.
      </p>
      {loading ? (
        <p className="loading">Загрузка…</p>
      ) : !panel?.indicators.length ? (
        <p className="macro-panel__empty">Данные временно недоступны</p>
      ) : (
        <div className="macro-grid">
          {panel.indicators.map((ind) => (
            <div key={ind.id} className="macro-card">
              <div className="macro-card__name">{ind.name}</div>
              <div className="macro-card__value">
                {ind.value} <span className="macro-card__unit">{ind.unit}</span>
                {ind.change_pct != null && (
                  <span className={ind.change_pct >= 0 ? "macro-card__chg trend-up" : "macro-card__chg trend-down"}>
                    {ind.change_pct >= 0 ? " ▲" : " ▼"}
                    {Math.abs(ind.change_pct)}%
                  </span>
                )}
              </div>
              <p className="macro-card__impact">{ind.impact}</p>
              <span className="macro-card__source">{ind.source}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MacroFactorsPanel;
