from __future__ import annotations

import os
from dataclasses import asdict
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .schemas import CalculateRequest
from .services.calculator import METHOD_LABELS, calculate


DATA_DIR = Path(os.getenv("DATA_DIR", "/data")).resolve()

ALLOWED_EXTENSIONS = {".xlsx", ".xls"}


app = FastAPI(title="Battery Analyzer UI")

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/methods")
def get_methods() -> list[dict[str, str]]:
    return [{"key": k, "label": v} for k, v in METHOD_LABELS.items()]


def resolve_guarded_path(file_path: str) -> Path:
    try:
        p = Path(file_path).expanduser()
        resolved = p.resolve()
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=400, detail=f"Invalid file_path: {e}")

    if resolved.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Only {sorted(ALLOWED_EXTENSIONS)} files are supported in v1.",
        )

    # For this Docker build, Excel IO is based on openpyxl -> best-effort support for .xlsx.
    if resolved.suffix.lower() != ".xlsx":
        raise HTTPException(status_code=400, detail="Only .xlsx inputs are supported in this build.")

    try:
        if not resolved.is_relative_to(DATA_DIR):
            raise HTTPException(
                status_code=400,
                detail="file_path must be under the mounted DATA_DIR.",
            )
    except AttributeError:  # pragma: no cover (older Python)
        # Fallback for Python versions without is_relative_to().
        if str(resolved).startswith(str(DATA_DIR) + os.sep) is False:
            raise HTTPException(status_code=400, detail="file_path must be under the mounted DATA_DIR.")

    if not resolved.exists():
        raise HTTPException(status_code=400, detail="file_path does not exist.")
    if not resolved.is_file():
        raise HTTPException(status_code=400, detail="file_path must be a file.")

    return resolved


@app.post("/api/calculate")
def post_calculate(req: CalculateRequest) -> dict[str, Any]:
    method_key = req.method.strip().lower()
    if method_key not in METHOD_LABELS:
        raise HTTPException(status_code=422, detail=f"Unknown method: {req.method}")

    input_path = resolve_guarded_path(req.file_path)

    try:
        result = calculate(method_key, input_path, req.params)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate ({method_key}): {type(e).__name__}: {e}",
        )

    return {
        "method": method_key,
        "input_path": str(input_path),
        **asdict(result),
    }


# Serve built React UI in Docker/production.
static_dir = Path(__file__).resolve().parent.parent / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

