#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/.hf-cache"
export HF_HUB_DISABLE_XET=1
if [[ ! -x .venv/bin/python ]]; then
  echo "Missing .venv/bin/python. Create the environment and install dependencies first:" >&2
  echo "  python3.14 -m venv .venv" >&2
  echo "  .venv/bin/python -m pip install -r req.txt" >&2
  exit 1
fi
if ! .venv/bin/python -c 'import importlib.util; assert all(importlib.util.find_spec(name) for name in ("pyarrow", "z3", "mlx_lm"))' 2>/dev/null; then
  echo "Required Python packages are missing from .venv. Run:" >&2
  echo "  .venv/bin/python -m pip install -r req.txt" >&2
  exit 1
fi
if ! .venv/bin/python -c 'import mlx.core' 2>/dev/null; then
  echo "MLX cannot access a Metal GPU in this session. Run the benchmark in a normal macOS Terminal with GPU access." >&2
  exit 1
fi
if [[ ! -f models/Qwen3-8B-4bit/config.json ]]; then
  echo "Missing models/Qwen3-8B-4bit/config.json. Download the model first:" >&2
  echo "  .venv/bin/python scripts/download_model.py" >&2
  exit 1
fi
.venv/bin/python src/run_benchmark.py "$@"
