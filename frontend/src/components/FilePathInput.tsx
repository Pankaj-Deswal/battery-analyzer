export function FilePathInput({
  value,
  onChange,
}: {
  value: string
  onChange: (v: string) => void
}) {
  return (
    <label className="field">
      <span className="label">File path (inside container)</span>
      <input
        className="input"
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="/data/dunn_method_data.xlsx"
        spellCheck={false}
      />
      <span className="help">
        Put your Excel files on the mounted volume and enter their path, e.g.
        <code> /data/dunn_method_data.xlsx</code>.
      </span>
    </label>
  )
}

