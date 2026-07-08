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
    <div className="page">
      <header className="header">
        <h1>Battery Analyzer</h1>
        <p className="muted">Run Dunn or GITT calculations and visualize results.</p>
      </header>

      <main className="grid">
        <section className="card">
          <h2>Inputs</h2>
          <div className="stack gap">
            <MethodSelector methods={methods} selected={method} onChange={setMethod} />
            <FilePathInput value={filePath} onChange={setFilePath} />
            <CalculateButton disabled={!canCalculate} loading={loading} onClick={onCalculate} />
            {error ? <div className="error">{error}</div> : null}
          </div>
        </section>

        <section className="stack gap">
          <ResultsSummary resp={resp} />
          <PlotPanel resp={resp} />
        </section>
      </main>
    </div>
  )
}
