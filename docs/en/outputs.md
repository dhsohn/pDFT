# Outputs

## Directory Layout (Example)

```text
runs/2026-01-03_100104/0147_optimization/
  metadata.json
  config_used.json
  log/run.log
  log/run_events.jsonl
  optimized.xyz
  frequency_result.json
  irc_result.json
  irc_profile.csv
  qcschema_result.json
  scan_result.json
  scan_result.csv
  scan/
  snapshots/
```

## Key Files

- `metadata.json`: run metadata (status, settings, versions, summary)
- `config_used.json`: config snapshot used for the run
- `log/run.log`: runtime log
- `log/run_events.jsonl`: status transition events
- `optimized.xyz`: optimized geometry
- `frequency_result.json`: frequency results
- `irc_result.json`, `irc_profile.csv`: IRC results/profile
- `qcschema_result.json`: QCSchema output
- `scan_result.json`, `scan_result.csv`: scan results
- `snapshots/`: intermediate snapshots (optional)

Not all files are created for every calculation mode.
