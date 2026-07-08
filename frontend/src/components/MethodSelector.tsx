import type { MethodDescriptor } from "../types"

export function MethodSelector({
  methods,
  selected,
  onChange,
}: {
  methods: MethodDescriptor[]
  selected: string
  onChange: (key: string) => void
}) {
  return (
    <label className="field">
      <span className="label">Method</span>
      <select
        className="input"
        value={selected}
        onChange={(e) => onChange(e.target.value)}
      >
        <option value="" disabled>
          Select a method
        </option>
        {methods.map((m) => (
          <option key={m.key} value={m.key}>
            {m.label}
          </option>
        ))}
      </select>
    </label>
  )
}

