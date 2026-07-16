import type { CalculateResponse, PlotSpec, SeriesSpec } from "../types"
import {
  CartesianGrid,
  Line,
  LineChart,
  Legend,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"

const COLORS = [
  "#2563eb",
  "#16a34a",
  "#d97706",
  "#dc2626",
  "#7c3aed",
  "#0891b2",
  "#db2777",
]

function makeLineChartData(plot: PlotSpec) {
  if (!plot.series.length) return []
  const baseX = plot.series[0].x
  const seriesByIndex = plot.series

  return baseX.map((x, i) => {
    const row: Record<string, number> = { x }
    for (let s = 0; s < seriesByIndex.length; s++) {
      row[`s${s}`] = seriesByIndex[s].y[i] ?? NaN
    }
    return row
  })
}

function PlotCard({ plot }: { plot: PlotSpec }) {
  const usesScatter = plot.series.some((s) => s.style === "scatter")

  if (usesScatter) {
    return (
      <div className="plot-card">
        <h3>{plot.title}</h3>
        <div className="chart-wrap">
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart>
              <CartesianGrid />
              <XAxis dataKey="x" name={plot.x_label} tick={{ fontSize: 10 }} />
              <YAxis
                scale={plot.log_y ? "log" : "linear"}
                dataKey="y"
                name={plot.y_label}
                domain={plot.log_y ? ["auto", "auto"] : undefined}
                tick={{ fontSize: 10 }}
              />
              <Tooltip />
              {plot.series.map((s: SeriesSpec, idx: number) => {
                const data = s.x.map((x, i) => ({ x, y: s.y[i] }))
                return (
                  <Scatter
                    key={s.name}
                    name={s.name}
                    data={data}
                    fill={COLORS[idx % COLORS.length]}
                  />
                )
              })}
              <Legend wrapperStyle={{ fontSize: 10 }} />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      </div>
    )
  }

  const data = makeLineChartData(plot)
  return (
    <div className="plot-card">
      <h3>{plot.title}</h3>
      <div className="chart-wrap">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid />
            <XAxis dataKey="x" name={plot.x_label} tick={{ fontSize: 10 }} />
            <YAxis
              scale={plot.log_y ? "log" : "linear"}
              domain={plot.log_y ? ["auto", "auto"] : undefined}
              tick={{ fontSize: 10 }}
            />
            <Tooltip />
            <Legend wrapperStyle={{ fontSize: 10 }} />
            {plot.series.map((s, idx) => {
              const dash = s.style === "dash_line" ? s.dash ?? [6, 4] : undefined
              return (
                <Line
                  key={s.name}
                  name={s.name}
                  type="monotone"
                  dataKey={`s${idx}`}
                  stroke={COLORS[idx % COLORS.length]}
                  strokeDasharray={dash ? dash.join(" ") : undefined}
                  dot={false}
                  connectNulls
                />
              )
            })}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export function PlotPanel({ resp }: { resp: CalculateResponse | null }) {
  if (!resp || !resp.plots.length) {
    return (
      <div className="plot-panel">
        <div className="empty-state">Run a calculation to view graphs here.</div>
      </div>
    )
  }

  return (
    <div className="plot-panel">
      {resp.plots.map((p) => (
        <PlotCard key={p.title} plot={p} />
      ))}
    </div>
  )
}
