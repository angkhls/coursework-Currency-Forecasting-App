import React from "react";
import type { CurrencyRate } from "../types";

interface Props {
  rate: CurrencyRate | null;
  loading?: boolean;
}

import { CURRENCY_FLAGS } from "../types";
import { formatNbrbQuote, formatPerUnitNote } from "../utils/currencyQuote";

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
        <span className="card__flag">{CURRENCY_FLAGS[rate.currency]}</span>
        <span className="card__currency">{rate.currency} / BYN</span>
      </div>
      <div className="card__rate">{formatNbrbQuote(rate.currency, rate.rate)}</div>
      {formatPerUnitNote(rate.currency, rate.rate) && (
        <div className="card__quote-sub">{formatPerUnitNote(rate.currency, rate.rate)}</div>
      )}
      <div className="card__date">
        Обновлено: {new Date(rate.date).toLocaleDateString("ru-RU")}
      </div>
    </div>
  );
};

export default CurrencyCard;
