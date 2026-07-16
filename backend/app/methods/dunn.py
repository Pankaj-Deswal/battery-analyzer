from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import linregress

from ..schemas import CalculationResult, PlotSpec, PreviewTable, SeriesSpec


def _compute_downsample_indices(n: int, max_points: int) -> np.ndarray:
    if n <= max_points:
        return np.arange(n)
    # Evenly spaced indices to keep the plot shape while reducing JSON size.
    return np.linspace(0, n - 1, max_points).round().astype(int)


def _find_peak_voltage_indices(voltage: np.ndarray) -> list[int]:
    """Return indices where voltage is greater than both neighbors."""
    if len(voltage) < 3:
        return []

    peaks: list[int] = []
    for i in range(1, len(voltage) - 1):
        if voltage[i] > voltage[i - 1] and voltage[i] > voltage[i + 1]:
            peaks.append(i)
    return peaks


def _calculate_b_value(
    currents: np.ndarray,
    scan_rates: np.ndarray,
) -> float:
    """b from log(scan_rate) vs log(current) regression slope."""
    valid = currents > 0
    if int(valid.sum()) < 2:
        return float("nan")

    log_scan = np.log(scan_rates[valid])
    log_i = np.log(currents[valid])
    b_slope, _, _, _, _ = linregress(log_scan, log_i)
    return float(b_slope)


def run_dunn(file_path: str | Path, *, max_plot_points: int = 5000) -> CalculationResult:
    input_path = Path(file_path)

    raw = pd.read_excel(input_path, header=None)

    # Find last non-empty column in first row (skip voltage column).
    last_col = 0
    for col in range(1, raw.shape[1]):
        value = raw.iat[0, col]
        if pd.isna(value) or str(value).strip() == "":
            break
        last_col = col

    raw = raw.iloc[:, : last_col + 1]

    # Voltage starts at row index 2, column 0.
    voltage = raw.iloc[2:, 0].astype(float).to_numpy()

    # Scan rates are in row 0, columns 1..end.
    scan_rates = raw.iloc[0, 1:].astype(float).to_numpy()

    # Current matrix: rows are voltages, columns are scan rates.
    current_matrix = raw.iloc[2:, 1:].astype(float).to_numpy()

    sqrt_scan = np.sqrt(scan_rates)

    results = pd.DataFrame()
    results["Voltage_V"] = voltage

    k1_list: list[float] = []
    k2_list: list[float] = []

    for i in range(len(voltage)):
        currents = current_matrix[i, :]

        # Step 1-2: regression of i/sqrt(v) against sqrt(v).
        new_current = currents / sqrt_scan
        slope, intercept, _, _, _ = linregress(sqrt_scan, new_current)

        k1_list.append(float(slope))
        k2_list.append(float(intercept))

    results["K1_slope"] = k1_list
    results["K2_intercept"] = k2_list

    for scan_rate in scan_rates:
        results[f"Capacitive_{scan_rate}"] = results["K1_slope"] * scan_rate
        results[f"Inductive_{scan_rate}"] = results["K2_intercept"] * (scan_rate**0.5)

    # b value: only at peak voltages (local maxima in the voltage column).
    peak_indices = _find_peak_voltage_indices(voltage)
    peak_b_rows: list[dict[str, float]] = []
    for peak_idx in peak_indices:
        peak_b_rows.append(
            {
                "Peak_Voltage_V": float(voltage[peak_idx]),
                "b_value": _calculate_b_value(current_matrix[peak_idx, :], scan_rates),
            }
        )

    peak_b_results = pd.DataFrame(peak_b_rows)

    output_path = input_path.with_name(f"{input_path.stem}_dunn_results.xlsx")
    with pd.ExcelWriter(output_path) as writer:
        results.to_excel(writer, sheet_name="Results", index=False)
        peak_b_results.to_excel(writer, sheet_name="Peak_b_values", index=False)

    # -------- Plot data (Plotly-style JSON, rendered by Recharts) --------
    n_points = len(voltage)
    idx = _compute_downsample_indices(n_points, max_plot_points)

    voltage_ds = voltage[idx]

    series: list[SeriesSpec] = []
    for col_idx, scan_rate in enumerate(scan_rates):
        original_y = current_matrix[:, col_idx][idx]
        capacitive_y = results[f"Capacitive_{scan_rate}"].to_numpy()[idx]

        series.append(
            SeriesSpec(
                name=f"Original {scan_rate}",
                x=voltage_ds.astype(float).tolist(),
                y=np.asarray(original_y, dtype=float).tolist(),
                style="line",
            )
        )
        series.append(
            SeriesSpec(
                name=f"K1*scan_rate {scan_rate}",
                x=voltage_ds.astype(float).tolist(),
                y=np.asarray(capacitive_y, dtype=float).tolist(),
                style="dash_line",
                dash=[6, 4],
            )
        )

    plot1 = PlotSpec(
        title="Dunn Method: Original Current and Capacitive Contribution",
        x_label="Voltage (V)",
        y_label="Current (A)",
        log_y=False,
        series=series,
    )

    # Preview table for UI.
    preview_df = (
        peak_b_results.copy()
        if not peak_b_results.empty
        else results.head(20).copy()
    )
    preview_df = preview_df.replace({np.nan: None})
    raw_rows = preview_df.to_numpy(dtype=object).tolist()
    rows: list[list[Any]] = []
    for row in raw_rows:
        converted = []
        for cell in row:
            if cell is None:
                converted.append(None)
            elif hasattr(cell, "item"):
                converted.append(cell.item())
            else:
                converted.append(cell)
        rows.append(converted)
    preview = PreviewTable(
        columns=[str(c) for c in preview_df.columns],
        rows=rows,
    )

    return CalculationResult(
        results_path=str(output_path),
        message=f"Saved results to {output_path}",
        preview=preview,
        plots=[plot1],
    )

