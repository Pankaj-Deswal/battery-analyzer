export function CalculateButton({
  disabled,
  loading,
  onClick,
}: {
  disabled: boolean
  loading: boolean
  onClick: () => void
}) {
  return (
    <button className="button" disabled={disabled || loading} onClick={onClick}>
      {loading ? "Calculating..." : "Calculate"}
    </button>
  )
}

