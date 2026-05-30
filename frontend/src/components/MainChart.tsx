import React, { useMemo } from "react";
import {
  CartesianGrid,
  ComposedChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ChartData, ForecastResult } from "../types";
import { PAIR_LABELS } from "../types";

interface Props {
  chart: ChartData | null;
  forecast: ForecastResult | null;
  loading?: boolean;
  large?: boolean;
}

type Row = {
  dateKey: string;
  dateLabel: string;
  rate?: number;
  sma?: number;
  ema?: number;
  forecast?: number;
};

function parseIso(iso: string): Date {
  return new Date(iso.includes("T") ? iso : `${iso}T12:00:00`);
}

function sortRows(rows: Row[]): Row[] {
  return [...rows].sort((a, b) => a.dateKey.localeCompare(b.dateKey));
}

const MainChart: React.FC<Props> = ({ chart, forecast, loading, large }) => {
  const { data, yDomain } = useMemo(() => {
    if (!chart) return { data: [] as Row[], yDomain: [0, 1] as [number, number] };

    const rows: Row[] = chart.points.map((p) => {
      const dt = parseIso(p.date);
      return {
        dateKey: p.date.slice(0, 10),
        dateLabel: dt.toLocaleDateString("ru-RU", { day: "2-digit", month: "short" }),
        rate: p.rate,
        sma: p.sma_20 ?? undefined,
        ema: p.ema_20 ?? undefined,
      };
    });

    if (forecast?.forecast.length) {
      const last = rows[rows.length - 1];
      if (last?.rate != null) {
        last.forecast = last.rate;
      }

      for (const p of forecast.forecast) {
        const key = p.date.slice(0, 10);
        const existing = rows.find((r) => r.dateKey === key);
        const dt = parseIso(p.date);
        const label = dt.toLocaleDateString("ru-RU", { day: "2-digit", month: "short" });
        if (existing) {
          existing.forecast = p.predicted_value;
        } else {
          rows.push({
            dateKey: key,
            dateLabel: label,
            forecast: p.predicted_value,
          });
        }
      }
    }

    const sorted = sortRows(rows);

    const values: number[] = [];
    sorted.forEach((r) => {
      if (r.rate != null) values.push(r.rate);
      if (r.sma != null) values.push(r.sma);
      if (r.ema != null) values.push(r.ema);
      if (r.forecast != null) values.push(r.forecast);
    });

    let yMin = chart.y_min;
    let yMax = chart.y_max;
    if (values.length) {
      yMin = Math.min(yMin, ...values);
      yMax = Math.max(yMax, ...values);
    }
    const span = yMax - yMin || 0.1;
    const pad = Math.max(span * 0.08, 0.015);

    return { data: sorted, yDomain: [yMin - pad, yMax + pad] as [number, number] };
  }, [chart, forecast]);

  if (loading) return <div className="loading">Загрузка графика…</div>;
  if (!chart) return null;

  const height = large ? 480 : 360;

  return (
    <div className="chart-card glass-card">
      <div className="chart-header">
        <div className="chart-header__pair">{PAIR_LABELS[chart.pair]}</div>
        <span className="chart-y-hint">
          Y: {yDomain[0].toFixed(4)} — {yDomain[1].toFixed(4)}
        </span>
      </div>
      <ResponsiveContainer width="100%" height={height}>
        <ComposedChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
          <XAxis
            dataKey="dateLabel"
            tick={{ fill: "#9aa8bc", fontSize: 11 }}
            interval="preserveStartEnd"
          />
          <YAxis
            tick={{ fill: "#9aa8bc", fontSize: 11 }}
            domain={yDomain}
            width={58}
            tickFormatter={(v: number) => v.toFixed(4)}
            allowDataOverflow
          />
          <Tooltip
            labelFormatter={(_, payload) => {
              const row = payload?.[0]?.payload as Row | undefined;
              return row?.dateKey ?? "";
            }}
            contentStyle={{
              background: "rgba(20,28,40,0.95)",
              border: "1px solid rgba(255,255,255,0.15)",
              borderRadius: 8,
            }}
            formatter={(value: number, name: string) => [
              typeof value === "number" ? value.toFixed(4) : "—",
              name,
            ]}
          />
          <Line
            type="monotone"
            dataKey="rate"
            name="Курс"
            stroke="#38bdf8"
            strokeWidth={2.5}
            dot={false}
            connectNulls={false}
            isAnimationActive={false}
          />
          <Line
            type="monotone"
            dataKey="sma"
            name="SMA(20)"
            stroke="#a78bfa"
            strokeWidth={1.5}
            dot={false}
            connectNulls
            isAnimationActive={false}
          />
          <Line
            type="monotone"
            dataKey="ema"
            name="EMA(20)"
            stroke="#fbbf24"
            strokeWidth={1.5}
            dot={false}
            connectNulls
            isAnimationActive={false}
          />
          <Line
            type="monotone"
            dataKey="forecast"
            name="Прогноз"
            stroke="#fb923c"
            strokeWidth={2.5}
            strokeDasharray="8 4"
            dot={{ r: 3, fill: "#fb923c" }}
            connectNulls
            isAnimationActive={false}
          />
        </ComposedChart>
      </ResponsiveContainer>
      <div className="legend">
        <span className="rate">Курс (голубой)</span>
        <span className="sma">SMA(20)</span>
        <span className="ema">EMA(20)</span>
        <span className="forecast">Прогноз (оранж.)</span>
      </div>
    </div>
  );
};

export default MainChart;
