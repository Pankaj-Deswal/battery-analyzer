import type { CalculateResponse } from "../types"

function PreviewTable({ preview }: { preview: CalculateResponse["preview"] }) {
  if (!preview.rows.length) return null
  return (
    <table className="table">
      <thead>
        <tr>
          {preview.columns.map((c) => (
            <th key={c}>{c}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {preview.rows.map((row, idx) => (
          <tr key={idx}>
            {row.map((v, j) => (
              <td key={j}>{v === null ? "" : String(v)}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export function ResultsSummary({ resp }: { resp: CalculateResponse | null }) {
  if (!resp) return null
  return (
    <section className="panel">
      <h2>Results</h2>
      <p className="muted">{resp.message}</p>
      <p className="muted">
        Saved to: <code>{resp.results_path}</code>
      </p>
      <PreviewTable preview={resp.preview} />
    </section>
  )
}

