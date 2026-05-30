import React from "react";
import {
  LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import type { CurrencyRate, CurrencyCode } from "../types";
import { chartRate, chartYAxisLabel } from "../utils/currencyQuote";

interface Props {
  data: CurrencyRate[];
  currency: CurrencyCode;
}

const HistoryChart: React.FC<Props> = ({ data, currency }) => {
  const chartData = data.map((r) => ({
    date: new Date(r.date).toLocaleDateString("ru-RU", {
      day: "2-digit",
      month: "2-digit",
    }),
    rate: chartRate(r.rate, currency),
  }));

  return (
    <div className="chart">
      <h3 className="chart__title">История курса {currency} / BYN</h3>
      <p className="chart__subtitle">{chartYAxisLabel(currency)}</p>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12 }}
            interval={Math.floor(chartData.length / 7)}
          />
          <YAxis tick={{ fontSize: 12 }} domain={["auto", "auto"]} />
          <Tooltip
            formatter={(value: number) => [value.toFixed(4), "Курс"]}
            labelFormatter={(label) => `Дата: ${label}`}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="rate"
            name={`${currency}/BYN`}
            stroke="#2563eb"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default HistoryChart;
