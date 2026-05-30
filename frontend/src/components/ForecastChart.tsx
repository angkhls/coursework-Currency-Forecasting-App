import React from "react";
import {
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import type { CurrencyRate, ForecastResult } from "../types";

interface Props {
  history: CurrencyRate[];
  forecast: ForecastResult | null;
  currency: string;
}

const ForecastChart: React.FC<Props> = ({ history, forecast, currency }) => {
  const recent = history.slice(-30);
  const historyPoints = recent.map((r) => ({
    date: new Date(r.date).toLocaleDateString("ru-RU", {
      day: "2-digit",
      month: "2-digit",
    }),
    rate: r.rate,
    predicted: undefined as number | undefined,
  }));

  const last = recent[recent.length - 1];
  const forecastPoints = (forecast?.forecast ?? []).map((p, index) => ({
    date: new Date(p.date).toLocaleDateString("ru-RU", {
      day: "2-digit",
      month: "2-digit",
    }),
    rate: index === 0 && last ? last.rate : undefined,
    predicted: p.predicted_value,
  }));

  const chartData = [...historyPoints, ...forecastPoints];

  return (
    <div className="chart">
      <h3 className="chart__title">Прогноз курса {currency} / BYN</h3>
      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12 }}
            interval={Math.floor(chartData.length / 8)}
          />
          <YAxis tick={{ fontSize: 12 }} domain={["auto", "auto"]} />
          <Tooltip
            formatter={(value: number, name: string) => [
              value?.toFixed(4),
              name === "rate" ? "Факт" : "Прогноз",
            ]}
          />
          <Legend formatter={(value) => (value === "rate" ? "Факт" : "Прогноз")} />
          <Line
            type="monotone"
            dataKey="rate"
            stroke="#2563eb"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
            connectNulls={false}
          />
          <Line
            type="monotone"
            dataKey="predicted"
            stroke="#f97316"
            strokeWidth={2}
            strokeDasharray="6 3"
            dot={{ r: 3, fill: "#f97316" }}
            connectNulls
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ForecastChart;
