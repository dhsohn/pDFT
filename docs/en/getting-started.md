# Install & Quickstart

## Installation

DFTFlow is distributed via conda.

```bash
conda create -n dftflow -c daehyupsohn -c conda-forge dftflow
conda activate dftflow
```

- `pip install dftflow` is not supported.
- The GUI is a separate app (`dftflow_gui`).

## Environment Check

```bash
dftflow doctor
```

## Configuration File

- Supported formats: `.json`, `.yaml/.yml`, `.toml`
- Default name: `run_config.json`

Example (`run_config.yaml`):

```yaml
calculation_mode: optimization
basis: def2-svp
xc: b3lyp
solvent: vacuum
optimizer:
  mode: minimum
scf:
  max_cycle: 200
single_point_enabled: true
frequency_enabled: true
```

## First Run

```bash
dftflow run path/to/input.xyz --config run_config.yaml
```

## Check Results

```bash
dftflow status --recent 5
```

Logs are written to `log/run.log` inside the run directory by default.
