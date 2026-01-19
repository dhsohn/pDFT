# Troubleshooting

## SMD Errors

- You need an SMD-enabled PySCF build.
- Example message: "Install the SMD-enabled PySCF package..."

```bash
conda install -c daehyupsohn -c conda-forge pyscf
```

## SCF Convergence Failures

- DFTFlow retries with level shift/damping by default.
- Disable retries with `DFTFLOW_SCF_RETRY=0`.

## Queue Appears Stuck

- Check status: `dftflow queue status`
- Check runner log: `~/DFTFlow/log/queue_runner.log`
- Requeue failed: `dftflow queue requeue-failed`

## Memory/Threads

- `memory_gb` is passed to PySCF `max_memory`.
- Threading depends on OpenMP availability.

## Diagnostics

```bash
dftflow doctor
```
