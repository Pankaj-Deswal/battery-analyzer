import { useEffect, useMemo, useState } from "react"
import "./App.css"
import { calculate, fetchMethods } from "./api/client"
import type { CalculateResponse, MethodDescriptor } from "./types"
import { CalculateButton } from "./components/CalculateButton"
import { FilePathInput } from "./components/FilePathInput"
import { MethodSelector } from "./components/MethodSelector"
import { PlotPanel } from "./components/PlotPanel"
import { ResultsSummary } from "./components/ResultsSummary"

export default function App() {
  const [methods, setMethods] = useState<MethodDescriptor[]>([])
  const [method, setMethod] = useState("")
  const [filePath, setFilePath] = useState("")

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [resp, setResp] = useState<CalculateResponse | null>(null)

  useEffect(() => {
    fetchMethods()
      .then(setMethods)
      .catch((e) => setError(String(e)))
  }, [])

  const canCalculate = useMemo(
    () => method.trim().length > 0 && filePath.trim().length > 0,
    [method, filePath],
  )

  async function onCalculate() {
    if (!canCalculate) return
    setLoading(true)
    setError(null)
    try {
      const r = await calculate(method, filePath, {})
      setResp(r)
    } catch (e) {
      setResp(null)
      setError(String(e))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-shell">
      <section className="region region-inputs">
        <header className="region-header">
          <h1>Battery Analyzer</h1>
          <p className="muted">Run Dunn or GITT calculations and visualize results.</p>
        </header>

        <div className="region-body">
          <h2>Inputs</h2>
          <div className="stack gap">
            <MethodSelector methods={methods} selected={method} onChange={setMethod} />
            <FilePathInput value={filePath} onChange={setFilePath} />
            <CalculateButton disabled={!canCalculate} loading={loading} onClick={onCalculate} />
            {error ? <div className="error">{error}</div> : null}
          </div>
        </div>
      </section>

      <section className="region region-graphs">
        <div className="region-header">
          <h2>Graphs</h2>
        </div>
        <div className="region-body">
          <PlotPanel resp={resp} />
        </div>
      </section>

      <section className="region region-results">
        <div className="region-header">
          <h2>Results</h2>
        </div>
        <div className="region-body">
          <ResultsSummary resp={resp} />
        </div>
      </section>
    </div>
  )
}
