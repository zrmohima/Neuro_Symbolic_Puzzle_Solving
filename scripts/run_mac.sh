#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/.hf-cache"
export HF_HUB_DISABLE_XET=1
.venv/bin/python src/run_benchmark.py "$@"
