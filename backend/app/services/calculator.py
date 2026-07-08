from __future__ import annotations

from pathlib import Path
from typing import Any

from ..methods.dunn import run_dunn
from ..methods.gitt import run_gitt
from ..schemas import CalculationResult


METHOD_LABELS: dict[str, str] = {
    "dunn": "Dunn Method",
    "gitt": "GITT Method",
}


def calculate(method: str, file_path: Path, params: dict[str, Any]) -> CalculationResult:
    method_key = method.strip().lower()
    if method_key == "dunn":
        max_plot_points = params.get("max_plot_points", 5000)
        return run_dunn(file_path, max_plot_points=int(max_plot_points))

    if method_key == "gitt":
        return run_gitt(
            file_path,
            skip_rows=int(params.get("skip_rows", 6)),
            L=float(params.get("L", 1e-4)),
            threshold=float(params.get("threshold", 1e-4)),
            min_points=int(params.get("min_points", 5)),
            tau=float(params.get("tau", 1800)),
            max_plot_points=int(params.get("max_plot_points", 5000)),
        )

    raise ValueError(f"Unknown method: {method}")


__all__ = ["calculate", "METHOD_LABELS"]

