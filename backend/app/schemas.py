from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from pydantic import BaseModel, Field


class CalculateRequest(BaseModel):
    method: str
    file_path: str
    params: dict[str, Any] = Field(default_factory=dict)


@dataclass
class PreviewTable:
    columns: list[str]
    rows: list[list[Any]]


SeriesStyle = Literal["line", "dash_line", "scatter"]


@dataclass
class SeriesSpec:
    name: str
    x: list[float]
    y: list[float]
    style: SeriesStyle
    dash: list[int] | None = None


@dataclass
class PlotSpec:
    title: str
    x_label: str
    y_label: str
    log_y: bool
    series: list[SeriesSpec]


@dataclass
class CalculationResult:
    results_path: str
    message: str
    preview: PreviewTable
    plots: list[PlotSpec]

