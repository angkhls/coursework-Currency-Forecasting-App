import React, { useEffect, useMemo, useState } from "react";
import { currencyApi } from "../api/client";
import type { BankRatesTable as BankTable } from "../types";

const BankRatesTable: React.FC = () => {
  const [table, setTable] = useState<BankTable | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    currencyApi
      .getBankRates()
      .then(setTable)
      .catch(() => setTable(null))
      .finally(() => setLoading(false));
  }, []);

  const best = useMemo(() => {
    if (!table?.rows.length) return null;
    const rows = table.rows;
    return {
      usdSell: Math.max(...rows.map((r) => r.usd.sell)),
      usdBuy: Math.min(...rows.filter((r) => r.usd.buy > 0).map((r) => r.usd.buy)),
      eurSell: Math.max(...rows.map((r) => r.eur.sell)),
      eurBuy: Math.min(...rows.filter((r) => r.eur.buy > 0).map((r) => r.eur.buy)),
      rubSell: Math.max(...rows.map((r) => r.rub100.sell)),
      rubBuy: Math.min(...rows.filter((r) => r.rub100.buy > 0).map((r) => r.rub100.buy)),
    };
  }, [table]);

  const cell = (value: number, isBest: boolean) => (
    <td className={isBest ? "bank-cell bank-cell--best" : "bank-cell"}>{value > 0 ? value.toFixed(4) : "—"}</td>
  );

  return (
    <div className="glass-card bank-table-wrap">
      <h3>Курсы в банках — {table?.city ?? "Минск"}</h3>
      {loading ? (
        <p className="loading">Загрузка…</p>
      ) : !table?.rows.length ? (
        <p className="macro-panel__empty">Не удалось загрузить курсы банков</p>
      ) : (
        <>
          <div className="bank-table-scroll">
            <table className="bank-table">
              <thead>
                <tr>
                  <th rowSpan={2}>Банк</th>
                  <th colSpan={2}>USD</th>
                  <th colSpan={2}>EUR</th>
                  <th colSpan={2}>RUB 100</th>
                </tr>
                <tr>
                  <th>Сдать</th>
                  <th>Купить</th>
                  <th>Сдать</th>
                  <th>Купить</th>
                  <th>Сдать</th>
                  <th>Купить</th>
                </tr>
              </thead>
              <tbody>
                {table.rows.map((row) => (
                  <tr key={row.bank_id}>
                    <td className="bank-name">{row.bank_name}</td>
                    {cell(row.usd.sell, best != null && row.usd.sell === best.usdSell)}
                    {cell(row.usd.buy, best != null && row.usd.buy === best.usdBuy)}
                    {cell(row.eur.sell, best != null && row.eur.sell === best.eurSell)}
                    {cell(row.eur.buy, best != null && row.eur.buy === best.eurBuy)}
                    {cell(row.rub100.sell, best != null && row.rub100.sell === best.rubSell)}
                    {cell(row.rub100.buy, best != null && row.rub100.buy === best.rubBuy)}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
};

export default BankRatesTable;
