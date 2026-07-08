from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from ..schemas import CalculationResult, PlotSpec, PreviewTable, SeriesSpec


def _compute_downsample_indices(n: int, max_points: int) -> np.ndarray:
    if n <= max_points:
        return np.arange(n)
    return np.linspace(0, n - 1, max_points).round().astype(int)


def _find_segments(time: np.ndarray, voltage: np.ndarray, *, threshold: float, min_points: int):
    """Return continuous increasing/decreasing voltage segments."""
    dv = np.diff(voltage)
    direction = np.where(dv > threshold, 1, np.where(dv < -threshold, -1, 0))

    # Fill flat/noisy points with previous direction.
    for i in range(1, len(direction)):
        if direction[i] == 0:
            direction[i] = direction[i - 1]

    change_idx = np.where(np.diff(direction) != 0)[0] + 1
    bounds = np.r_[0, change_idx, len(voltage) - 1]

    segments = []
    for start, end in zip(bounds[:-1], bounds[1:]):
        if end - start >= min_points:
            segments.append(
                {
                    "start": int(start),
                    "end": int(end),
                    "dir": int(direction[start]),
                    "voltage_start": float(voltage[start]),
                    "voltage_end": float(voltage[end]),
                }
            )
    return segments


def _calculate_steps(
    time: np.ndarray,
    voltage: np.ndarray,
    *,
    expected_pulse_dir: int,
    mode: str,
    tau: float,
    L: float,
    threshold: float,
    min_points: int,
):
    """
    Charge: pulse increases (+1), relaxation decreases (-1)
    Discharge: pulse decreases (-1), relaxation increases (+1)
    """
    segments = _find_segments(time, voltage, threshold=threshold, min_points=min_points)
    results = []

    if tau <= 0:
        return results

    for i in range(len(segments) - 1):
        pulse = segments[i]
        relax = segments[i + 1]

        # Pulse must be followed by opposite-direction relaxation.
        if pulse["dir"] != expected_pulse_dir:
            continue
        if relax["dir"] != -expected_pulse_dir:
            continue

        # Guards for indexing on short/edge segments.
        if pulse["start"] + 3 >= len(voltage):
            continue
        if pulse["end"] >= len(voltage) or relax["end"] >= len(voltage):
            continue

        E_start = voltage[pulse["start"]]  # Before pulse
        E_After = voltage[pulse["start"] + 3]  # A few steps into the pulse
        E_pulse_end = voltage[pulse["end"]]  # End of pulse
        E_eq = voltage[relax["end"]]  # After relaxation

        delta_E_tau = float(abs(E_pulse_end - E_After))
        delta_E_s = float(abs(E_eq - E_start))

        if delta_E_tau == 0:
            continue

        # Simplified GITT diffusion coefficient.
        D = (4 * (L**2) / (np.pi * tau)) * ((delta_E_s / delta_E_tau) ** 2)

        results.append(
            {
                "mode": mode,
                "pulse_start_s": float(time[pulse["start"]]),
                "pulse_end_s": float(time[pulse["end"]]),
                "relax_end_s": float(time[relax["end"]]),
                "delta_E_tau_V": delta_E_tau,
                "delta_E_s_V": delta_E_s,
                "pulse_time_s": float(tau),
                "voltage_start_V": pulse["voltage_start"],
                "D_cm2_s": float(D),
            }
        )

    return results


def run_gitt(
    file_path: str | Path,
    *,
    skip_rows: int = 6,
    L: float = 1e-4,
    threshold: float = 1e-4,
    min_points: int = 5,
    tau: float = 1800,
    max_plot_points: int = 5000,
) -> CalculationResult:
    input_path = Path(file_path)

    # Read time and voltage columns (values start from row skip_rows+1 in Excel).
    df = pd.read_excel(
        input_path,
        skiprows=skip_rows,
        usecols=[0, 1],
        header=None,
    ).dropna()
    df.columns = ["time_s", "voltage_V"]
    df = df.reset_index(drop=True)

    t = df["time_s"].to_numpy(dtype=float)
    v = df["voltage_V"].to_numpy(dtype=float)

    # Plot voltage curve + compute diffusion coefficient.
    peak = int(np.argmax(v))

    charge_results = _calculate_steps(
        t[: peak + 1],
        v[: peak + 1],
        expected_pulse_dir=1,
        mode="charge",
        tau=tau,
        L=L,
        threshold=threshold,
        min_points=min_points,
    )
    discharge_results = _calculate_steps(
        t[peak:],
        v[peak:],
        expected_pulse_dir=-1,
        mode="discharge",
        tau=tau,
        L=L,
        threshold=threshold,
        min_points=min_points,
    )

    results_df = pd.DataFrame(charge_results + discharge_results)

    output_path = input_path.with_name(f"{input_path.stem}_gitt_results.xlsx")
    results_df.to_excel(output_path, index=False)

    # ------- Plot data (returned as JSON for Recharts) -------
    n_points = len(v)
    idx = _compute_downsample_indices(n_points, max_plot_points)

    plot1 = PlotSpec(
        title="GITT: Voltage vs Time",
        x_label="Time (s)",
        y_label="Voltage (V)",
        log_y=False,
        series=[
            SeriesSpec(
                name="Voltage",
                x=t[idx].astype(float).tolist(),
                y=v[idx].astype(float).tolist(),
                style="line",
            )
        ],
    )

    charge_df = results_df[results_df["mode"] == "charge"] if not results_df.empty else results_df
    discharge_df = results_df[results_df["mode"] == "discharge"] if not results_df.empty else results_df

    # Downsample scatter if there are many pulses.
    def scatter_series(df_in: pd.DataFrame, name: str):
        if df_in.empty:
            return SeriesSpec(name=name, x=[], y=[], style="scatter")

        xs = df_in["voltage_start_V"].to_numpy(dtype=float)
        ys = df_in["D_cm2_s"].to_numpy(dtype=float)
        ds_idx = _compute_downsample_indices(len(xs), max_plot_points)
        return SeriesSpec(
            name=name,
            x=xs[ds_idx].astype(float).tolist(),
            y=ys[ds_idx].astype(float).tolist(),
            style="scatter",
        )

    plot2 = PlotSpec(
        title="GITT: Diffusion Coefficient",
        x_label="Starting Voltage (V)",
        y_label="Diffusion Coefficient (cm²/s)",
        log_y=True,
        series=[scatter_series(charge_df, "Charge"), scatter_series(discharge_df, "Discharge")],
    )

    # Preview table.
    preview_df = results_df.head(20).copy()
    if not preview_df.empty:
        preview_df = preview_df.replace({np.nan: None})
        raw_rows = preview_df.to_numpy(dtype=object).tolist()
        rows: list[list[object]] = []
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
    else:
        rows = []

    preview = PreviewTable(
        columns=[str(c) for c in preview_df.columns],
        rows=rows,
    )

    return CalculationResult(
        results_path=str(output_path),
        message=f"Saved results to {output_path}",
        preview=preview,
        plots=[plot1, plot2],
    )

