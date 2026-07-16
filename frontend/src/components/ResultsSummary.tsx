import type { CalculateResponse } from "../types"

function PreviewTable({ preview }: { preview: CalculateResponse["preview"] }) {
  if (!preview.rows.length) {
    return <div className="empty-state">No result rows to display.</div>
  }

  return (
    <div className="table-wrap">
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
    </div>
  )
}

export function ResultsSummary({ resp }: { resp: CalculateResponse | null }) {
  if (!resp) {
    return (
      <div className="results-panel">
        <div className="empty-state">Run a calculation to view results here.</div>
      </div>
    )
  }

  return (
    <div className="results-panel">
      <div className="results-meta">
        <p className="muted">{resp.message}</p>
        <p className="muted">
          Saved to: <code>{resp.results_path}</code>
        </p>
      </div>
      <PreviewTable preview={resp.preview} />
    </div>
  )
}
