"use client";
import {
  BarChart, Bar, LineChart, Line, ScatterChart, Scatter,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer
} from "recharts";

interface ChartSuggestion {
  type: string;
  x?: string;
  y?: string | string[];
  extra_y?: string[];
}

interface Props {
  data: Record<string, unknown>[];
  chart: ChartSuggestion;
}

const COLORS = ["#22c55e", "#60a5fa", "#f59e0b", "#f472b6", "#a78bfa"];

const formatValue = (val: unknown): string => {
  if (typeof val === "number") {
    return val >= 1_000_000
      ? `${(val / 1_000_000).toFixed(1)}M`
      : val >= 1_000
      ? `${(val / 1_000).toFixed(1)}K`
      : val % 1 === 0
      ? val.toString()
      : val.toFixed(2);
  }
  return String(val ?? "");
};

const tickFormatter = (v: unknown) => {
  const s = String(v ?? "");
  return s.length > 14 ? s.slice(0, 12) + "…" : s;
};

export default function ChartView({ data, chart }: Props) {
  if (chart.type === "none" || !data.length) return null;
  if (!chart.x || !chart.y) return null;

  const chartData = data.slice(0, 50);

  const commonProps = {
    width: 500,
    height: 320,
    data: chartData,
    margin: { top: 10, right: 20, left: 10, bottom: 60 },
  };

  const axisStyle = { fill: "#6b7280", fontSize: 11, fontFamily: "JetBrains Mono, monospace" };
  const gridStyle = { strokeDasharray: "3 3", stroke: "#1f2937" };
  const tooltipStyle = {
    contentStyle: { background: "#1f2937", border: "1px solid #374151", borderRadius: 8, fontSize: 12 },
    labelStyle: { color: "#d1d5db" },
    itemStyle: { color: "#86efac" },
  };

  if (chart.type === "bar" || chart.type === "bar_grouped") {
    const yKeys: string[] = chart.type === "bar_grouped" && Array.isArray(chart.y)
      ? chart.y
      : typeof chart.y === "string"
      ? [chart.y]
      : [];

    return (
      <div className="mt-6 bg-gray-900/60 rounded-xl p-4 border border-gray-800">
        <p className="text-xs text-gray-500 font-mono mb-3 uppercase tracking-wider">Chart</p>
        <ResponsiveContainer width="100%" height={320}>
          <BarChart {...commonProps}>
            <CartesianGrid {...gridStyle} />
            <XAxis dataKey={chart.x} tick={axisStyle} tickFormatter={tickFormatter} angle={-35} textAnchor="end" />
            <YAxis tick={axisStyle} tickFormatter={formatValue} />
            <Tooltip {...tooltipStyle} formatter={formatValue} />
            {yKeys.length > 1 && <Legend wrapperStyle={{ fontSize: 11 }} />}
            {yKeys.map((key, i) => (
              <Bar key={key} dataKey={key} fill={COLORS[i % COLORS.length]} radius={[3, 3, 0, 0]} maxBarSize={48} />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>
    );
  }

  if (chart.type === "line") {
    const yKey = typeof chart.y === "string" ? chart.y : "";
    const yKeys = chart.extra_y ? [yKey, ...chart.extra_y] : [yKey];
    return (
      <div className="mt-6 bg-gray-900/60 rounded-xl p-4 border border-gray-800">
        <p className="text-xs text-gray-500 font-mono mb-3 uppercase tracking-wider">Chart</p>
        <ResponsiveContainer width="100%" height={320}>
          <LineChart {...commonProps}>
            <CartesianGrid {...gridStyle} />
            <XAxis dataKey={chart.x} tick={axisStyle} tickFormatter={tickFormatter} angle={-35} textAnchor="end" />
            <YAxis tick={axisStyle} tickFormatter={formatValue} />
            <Tooltip {...tooltipStyle} formatter={formatValue} />
            {yKeys.length > 1 && <Legend wrapperStyle={{ fontSize: 11 }} />}
            {yKeys.map((key, i) => (
              <Line
                key={key}
                type="monotone"
                dataKey={key}
                stroke={COLORS[i % COLORS.length]}
                strokeWidth={2}
                dot={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    );
  }

  if (chart.type === "scatter") {
    const xKey = chart.x;
    const yKey = typeof chart.y === "string" ? chart.y : "";
    return (
      <div className="mt-6 bg-gray-900/60 rounded-xl p-4 border border-gray-800">
        <p className="text-xs text-gray-500 font-mono mb-3 uppercase tracking-wider">Chart</p>
        <ResponsiveContainer width="100%" height={320}>
          <ScatterChart {...commonProps}>
            <CartesianGrid {...gridStyle} />
            <XAxis dataKey={xKey} name={xKey} tick={axisStyle} tickFormatter={formatValue} />
            <YAxis dataKey={yKey} name={yKey} tick={axisStyle} tickFormatter={formatValue} />
            <Tooltip {...tooltipStyle} cursor={{ strokeDasharray: "3 3" }} />
            <Scatter data={chartData} fill={COLORS[0]} />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    );
  }

  return null;
}
