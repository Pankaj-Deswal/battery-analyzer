# Battery Analyzer UI

## Objective

A local React + FastAPI web UI to help battery researchers compute:
- **Dunn Method**: `K1`, `K2`, and `b` across scan rates (plus capacitive/inductive contributions).
- **GITT Method**: diffusion coefficient estimates for charging and discharging cycles.

The app runs in Docker and renders the resulting plots in the browser while saving the generated Excel results next to the input file.

## Run from scratch (Docker)

### 1) Prerequisites

1. Install **Docker Desktop** on your machine.
2. Ensure the Docker daemon is running.

### 2) Prepare input data

1. Create (or use) the mounted data folder:
   - `battery-analyzer/data/`
2. Copy your input Excel files into `battery-analyzer/data/`.

This is important because, inside the container, paths are under `/data/...`.

### 3) Start the app (one command)

From the `battery-analyzer/` directory, run:

```bash
docker compose up --build
```

### 4) Open the UI

Open:
- http://localhost:8000

### 5) Run a calculation

In the UI:
1. Select **Dunn Method** or **GITT Method**
2. Enter the file path **inside the container**, for example:
   - `/data/dunn_method_data.xlsx`
   - `/data/GITT_67.xlsx`
3. Click **Calculate**

The UI will show:
- A results preview table
- Plots for the selected method

Generated result files are saved back into the mounted `data/` folder on your host, next to the input file.

## Suggestions

What would you like to improve next?
- Add browser file upload (so users don’t type `/data/...` paths)
- Add GITT/Dunn advanced parameters controls in the UI
- Improve input-file validation and error messages per method

