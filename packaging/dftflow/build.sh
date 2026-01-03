#!/usr/bin/env bash
set -euo pipefail

$PYTHON -m pip install . -vv --no-deps --no-build-isolation
$PYTHON -m pip install sella basis-set-exchange -vv --no-deps
