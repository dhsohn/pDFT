#!/usr/bin/env bash
set -euo pipefail

export CMAKE_ARGS="${CMAKE_ARGS:-} -DENABLE_SMD=ON"

$PYTHON -m pip install . -vv --no-deps --no-build-isolation
