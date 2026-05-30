import React from "react";
import type { CurrencyRate } from "../types";

interface Props {
  rate: CurrencyRate | null;
  loading?: boolean;
}

const FLAGS: Record<string, string> = {
  USD: "🇺🇸",
  EUR: "🇪🇺",
  RUB: "🇷🇺",
};

const CurrencyCard: React.FC<Props> = ({ rate, loading }) => {
  if (loading) {
    return (
      <div className="card card--loading">
        <div className="skeleton skeleton--title" />
        <div className="skeleton skeleton--value" />
      </div>
    );
  }

  if (!rate) {
    return (
      <div className="card card--error">
        <span>Нет данных</span>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card__header">
        <span className="card__flag">{FLAGS[rate.currency]}</span>
        <span className="card__currency">{rate.currency} / BYN</span>
      </div>
      <div className="card__rate">{rate.rate.toFixed(4)}</div>
      <div className="card__date">
        Обновлено: {new Date(rate.date).toLocaleDateString("ru-RU")}
      </div>
    </div>
  );
};

export default CurrencyCard;
