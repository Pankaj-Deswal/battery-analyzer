import type { CalculateResponse, MethodDescriptor } from "../types"

export async function fetchMethods(): Promise<MethodDescriptor[]> {
  const res = await fetch("/api/methods")
  if (!res.ok) {
    const text = await res.text().catch(() => "")
    throw new Error(`Failed to load methods (${res.status}): ${text}`)
  }
  return (await res.json()) as MethodDescriptor[]
}

export async function calculate(method: string, file_path: string, params: Record<string, any> = {}) {
  const res = await fetch("/api/calculate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ method, file_path, params }),
  })

  if (!res.ok) {
    const text = await res.text().catch(() => "")
    throw new Error(`Calculation failed (${res.status}): ${text}`)
  }

  return (await res.json()) as CalculateResponse
}

