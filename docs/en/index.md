# DFTFlow User Manual (English)

DFTFlow is a local workflow tool built on PySCF and ASE. It runs optimization, single-point, frequency, IRC, and scans with consistent logging and metadata.

## Quick Start

```bash
conda create -n dftflow -c daehyupsohn -c conda-forge dftflow
conda activate dftflow

dftflow run path/to/input.xyz --config run_config.yaml
```

## What This Manual Covers

- Calculation modes and workflow flowcharts
- Queue/background execution and status transitions
- Scan execution including manifest-based distributed runs
- Configuration structure and key options
- Output files and troubleshooting

## Default Paths

- Default run directory: `~/DFTFlow/runs/YYYY-MM-DD_HHMMSS/`
- Override with the `DFTFLOW_BASE_DIR` environment variable.

## Next Reads

- [Install & Quickstart](getting-started.md)
- [Workflows](workflows.md)
- [Queue & Background](queue.md)
- [Scan](scan.md)
