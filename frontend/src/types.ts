export type SeriesStyle = "line" | "dash_line" | "scatter"

export type SeriesSpec = {
  name: string
  x: number[]
  y: number[]
  style: SeriesStyle
  dash?: number[]
}

export type PlotSpec = {
  title: string
  x_label: string
  y_label: string
  log_y: boolean
  series: SeriesSpec[]
}

export type PreviewTable = {
  columns: string[]
  rows: any[][]
}

export type CalculateResponse = {
  method: string
  input_path: string
  results_path: string
  message: string
  preview: PreviewTable
  plots: PlotSpec[]
}

export type MethodDescriptor = {
  key: string
  label: string
}

