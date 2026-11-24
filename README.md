# Qwen3-8B and Z3: ZebraLogicBench experiments

A clean code and results package for the selected thinking-enabled experiments. Earlier exploratory variants, curated Z3 baselines, environments, caches and model weights are excluded. Existing workspace files were not deleted or renamed.

## Selected results

Twenty puzzles were evaluated per size, using identical puzzle IDs for both approaches.

| Size | Approach | Fully correct | Puzzle accuracy | Cell accuracy |
|---|---|---:|---:|---:|
| 2×2 | Qwen alone | 20/20 | 100% | 100% |
| 2×2 | Qwen + Z3 | 20/20 | 100% | 100% |
| 3×4 | Qwen alone | 16/20 | 80% | 80% |
| 3×4 | Qwen + Z3 | 14/20 | 70% | 70% |
| 4×4 | Qwen alone | 14/20 | 70% | 70% |
| 4×4 | Qwen + Z3 | 13/20 | 65% | 65% |

These are selected development results, not held-out test results. The 4×4 approach was selected after inspecting development experiments. Later variants performed worse and are not included in this focused package. Do not interpret this table as showing that the hybrid approach improves accuracy. Failed parsing/translation counts as an incorrect puzzle with zero credited cells. Cell scoring excludes house-number cells.

## File layout

- `src/run_benchmark.py`: one runner for every puzzle size; direct and per-clue symbolic prompts.
- `src/solver.py`: domain extraction, whole-object JSON parsing, constraint validation, Z3 solving and scoring.
- `src/answer_validation.py`: accepts header/rows tables and arrays of records without changing predicted values.
- `scripts/`: pinned model download and Mac launcher.
- `tests/`: solver and table-validation regression tests.
- `req.txt`: exact dependency versions from the local experiment environment.
- `datasets/public/`: public grid-mode Parquet with hidden answers.
- `datasets/private/`: user-provided grid-mode and multiple-choice files with answers; included for local reproduction, Git-ignored.
- `datasets/metadata/`: download metadata, dataset checksum and pinned model revision.
- `prompts/<size>/inputs.jsonl`: exact rendered model inputs, including the chat template.
- `outputs/<size>/responses.jsonl`: raw model responses, token counts, timing and stop reasons. Join prompts and responses by `key`.
- `outputs/<size>/original_predictions.jsonl`: unmodified original per-puzzle records.
- `results/<size>/`: evaluated records, summaries, runtime, historical manifest and provenance.
- `results/comparison.json`: selected cross-size results.

## Dataset access and Git

Source: https://huggingface.co/datasets/allenai/ZebraLogicBench . Official answer dataset: https://huggingface.co/datasets/allenai/ZebraLogicBench-private . The private files require authorized access and are intentionally excluded by `.gitignore`. The ZIP includes them for your local reproduction; do not upload the entire ZIP as a public Git asset or force-add those files unless redistribution is permitted. Clone users should obtain their own authorized files and put them at `datasets/private/grid_mode.parquet` and `datasets/private/mc_mode.parquet`.

The experiments use grid mode only. Multiple-choice mode is included as requested but was not evaluated. Raw predictions may reproduce correct puzzle solutions; review what you intend to publish under the dataset's access conditions. No credentials are included.

## Install (Apple Silicon Mac)

Run in a normal Terminal with Metal GPU access:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r req.txt
python -m unittest discover -s tests -v
python scripts/download_model.py
```

The recorded environment used Python 3.14 on Apple Silicon. MLX dependencies are platform-specific; this package does not implement a CUDA/Linux backend. Model weights are not bundled. The downloader retrieves `mlx-community/Qwen3-8B-4bit` at the recorded revision. Full model card: https://huggingface.co/mlx-community/Qwen3-8B-4bit . This is a 4-bit quantized conversion of Qwen/Qwen3-8B.

## Run a new experiment

Use a fresh output directory for each size/configuration:

```sh
bash scripts/run_mac.sh --size '2*2' --limit 20 --out runs/2x2
bash scripts/run_mac.sh --size '3*4' --limit 20 --out runs/3x4
bash scripts/run_mac.sh --size '4*4' --limit 20 --out runs/4x4
```

Defaults: thinking enabled for both methods, greedy decoding, seed 0, 8,192 generated tokens per call, 20 puzzles selected in public dataset order. The hybrid translates one clue per call into a flat relation using category/value pairs, then executes Z3. No repair retries or compact-ID variants are used in these selected experiments. Each attribute's position lies between 1 and the number of houses; values within a category are all distinct. Z3 checks satisfiability and uniqueness. Neither satisfiability nor uniqueness proves the translation matches the natural-language clue.

The prompt asks direct solving to check clues and category uniqueness. The table validator accepts harmless layout variations, sorts house rows, and rejects missing/duplicate houses and incomplete tables. No values are filled in or corrected. Scores compare values case-insensitively after trimming outer whitespace.

`--prepare-only` checks selection and answers without loading MLX. The model config must exist first. Rerun an identical command to resume from saved calls. Do not run multiple processes against the same output directory. `--max-tokens` or `--no-thinking` changes the experiment; choose a different output directory. Runtime metrics count model generation, not complete wall time or dataset/model downloads.

## Historical results and validator change

The selected 4×4 direct result was rescored from saved original responses with the updated table validator: 14/20, versus the original stricter format acceptance. The archive preserves both original records and evaluated records; no answers were regenerated to obtain that score. The hybrid result is unchanged. The 2×2 and 3×4 runs used the updated validator during execution.

Archived manifests contain original workspace-relative paths and historical source hashes, retained for provenance. The cleaned code uses new paths/names, so its source hashes differ; archived runs must not be used as resume directories. Use `runs/` for new runs. Exact original prompts and responses remain available for inspection.

## Upload the extracted project to Git

After reviewing dataset access and intended repository visibility:

```sh
git init
git add .
git status
```

Check the staged files before committing. The included `.gitignore` excludes private answer files, future run directories, weights, caches and environments. Git initialization/upload has not been performed for you.
