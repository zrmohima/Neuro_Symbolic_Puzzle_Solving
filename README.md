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

These are selected development results from **one run per size**, not held-out test results or three-run averages. The 4×4 approach was selected after inspecting development experiments. Later variants performed worse and are not included in this focused package. Do not interpret this table as showing that the hybrid approach improves accuracy. Failed parsing/translation counts as an incorrect puzzle with zero credited cells. Cell scoring excludes house-number cells.

## Three-run 2×2 results

The same 20 development puzzles were run with both methods at temperature 0.7 using seeds 11, 22 and 33. Every run completed 20 predictions per method. The mean and sample standard deviation are across these three sampled runs; the archived greedy result above is excluded.

| Seed | Qwen puzzle accuracy | Qwen cell accuracy | Qwen + Z3 puzzle accuracy | Qwen + Z3 cell accuracy | Gold-consistent clues |
|---|---:|---:|---:|---:|---:|
| 11 | 15/20 (75%) | 60/80 (75%) | 20/20 (100%) | 80/80 (100%) | 38/38 (100%) |
| 22 | 14/20 (70%) | 56/80 (70%) | 20/20 (100%) | 80/80 (100%) | 38/38 (100%) |
| 33 | 16/20 (80%) | 64/80 (80%) | 19/20 (95%) | 76/80 (95%) | 37/38 (97.4%) |
| Mean ± SD | 75.0% ± 5.0 pp | 75.0% ± 5.0 pp | 98.3% ± 2.9 pp | 98.3% ± 2.9 pp | 99.1% ± 1.5 pp |

The mean within-run puzzle-accuracy difference (Qwen + Z3 minus Qwen alone) was +23.3 percentage points, with a sample standard deviation of 7.6 points. Full per-run metrics and costs are in `results/2x2_three_run_summary.json`; `results/repeated_summary.json` combines all nine sampled runs across the three sizes.

**Format sensitivity:** All 15 incorrect Qwen-alone records failed the strict table schema because Qwen returned a bare JSON matrix with a header row. A read-only diagnostic wrapped each matrix as `{"header": first_row, "rows": remaining_rows}` without changing any predicted cell values; all 15 then matched the reference table exactly. Under this post-hoc layout interpretation, Qwen-alone puzzle and cell accuracy would be 20/20 in every run. This is a diagnostic, not a replacement for the recorded primary score. The single symbolic failure was an invalid constraint. The strict-format difference should not be described as a demonstrated reasoning gain.

## Three-run 3×4 results

The same 20 development puzzles were run with both methods at temperature 0.7 using seeds 11, 22 and 33. All three runs completed 20 predictions per method. The mean and sample standard deviation are across the three runs; the archived greedy result above is excluded.

| Seed | Qwen puzzle accuracy | Qwen cell accuracy | Qwen + Z3 puzzle accuracy | Qwen + Z3 cell accuracy | Gold-consistent clues |
|---|---:|---:|---:|---:|---:|
| 11 | 11/20 (55%) | 132/240 (55%) | 16/20 (80%) | 192/240 (80%) | 121/129 (93.8%) |
| 22 | 11/20 (55%) | 132/240 (55%) | 17/20 (85%) | 204/240 (85%) | 126/129 (97.7%) |
| 33 | 15/20 (75%) | 180/240 (75%) | 15/20 (75%) | 180/240 (75%) | 123/129 (95.3%) |
| Mean ± SD | 61.7% ± 11.5 pp | 61.7% ± 11.5 pp | 80.0% ± 5.0 pp | 80.0% ± 5.0 pp | 95.6% ± 2.0 pp |

The mean within-run puzzle-accuracy difference (Qwen + Z3 minus Qwen alone) was +18.3 percentage points, with a sample standard deviation of 16.1 points. The three runs use the same puzzle IDs, so this describes sampling variation on this development set, not performance on new puzzles. Gold consistency checks whether the reference solution satisfies each translation; it does not establish semantic equivalence to the clue. Full metrics, per-run values and generation costs are in `results/3x4_three_run_summary.json`.

**Format sensitivity:** All 23 incorrect Qwen-alone records across these three runs failed the strict table schema because Qwen returned a bare JSON matrix with a header row. A read-only diagnostic wrapped each matrix as `{"header": first_row, "rows": remaining_rows}` without changing any predicted cell values; all 23 then matched the reference table exactly. Thus the 61.7% direct score above measures compliance with the specified output schema as well as puzzle solving. Under this post-hoc layout interpretation, direct puzzle and cell accuracy would be 20/20 in each run. This is a diagnostic, not a replacement for the recorded primary score; the interpretation was examined after seeing failures. For the symbolic method, 16 of 17 invalid clue relations used a domain value with different capitalization, and one used `Child` instead of the puzzle category `Children`. Exact string grounding, rather than a gold-contradicting logical relation, accounts for these recorded translation failures. The current evaluation rejects such mismatches and gives those puzzles zero credit. These observations make a direct claim of reasoning improvement from the strict scores unwarranted.

## Three-run 4×4 results

The same 20 development puzzles were run with both methods at temperature 0.7 using seeds 11, 22 and 33. Every run completed 20 predictions per method. The mean and sample standard deviation are across these three sampled runs; the archived greedy result above is excluded.

| Seed | Qwen puzzle accuracy | Qwen cell accuracy | Qwen + Z3 puzzle accuracy | Qwen + Z3 cell accuracy | Gold-consistent clues |
|---|---:|---:|---:|---:|---:|
| 11 | 13/20 (65%) | 208/320 (65%) | 11/20 (55%) | 176/320 (55%) | 186/201 (92.5%) |
| 22 | 13/20 (65%) | 208/320 (65%) | 14/20 (70%) | 224/320 (70%) | 189/201 (94.0%) |
| 33 | 11/20 (55%) | 176/320 (55%) | 17/20 (85%) | 272/320 (85%) | 197/201 (98.0%) |
| Mean ± SD | 61.7% ± 5.8 pp | 61.7% ± 5.8 pp | 70.0% ± 15.0 pp | 70.0% ± 15.0 pp | 94.9% ± 2.8 pp |

The mean within-run puzzle-accuracy difference (Qwen + Z3 minus Qwen alone) was +8.3 percentage points, with a sample standard deviation of 20.2 points. Full per-run metrics and costs are in `results/4x4_three_run_summary.json`.

Evaluation Analysis: Output normalization increased the direct Qwen3 puzzle accuracy from 61.7% to 85.0% across the three 4×4 experimental runs. Constraint validation and response completeness also influenced the performance of the neuro-symbolic approach. These findings highlight the importance of structured output handling and reliable constraint translation in evaluating end-to-end reasoning systems.

## File layout

- `src/run_benchmark.py`: one runner for every puzzle size; direct and per-clue symbolic prompts.
- `src/solver.py`: domain extraction, whole-object JSON parsing, constraint validation, Z3 solving and scoring.
- `src/translation_eval.py`: per-clue coverage, validity and reference-solution consistency checks.
- `src/answer_validation.py`: accepts header/rows tables and arrays of records without changing predicted values.
- `scripts/`: pinned model download and Mac launcher.
- `tests/`: translation-evaluation regression tests.
- `req.txt`: exact dependency versions from the local experiment environment.
- `datasets/public/`: public grid-mode Parquet with hidden answers.
- `datasets/private/`: user-provided grid-mode and multiple-choice files with answers; included for local reproduction, Git-ignored.
- `datasets/metadata/`: download metadata, dataset checksum and pinned model revision.
- `prompts/<size>/inputs.jsonl`: exact rendered model inputs, including the chat template.
- `outputs/<size>/responses.jsonl`: raw model responses, token counts, timing and stop reasons. Join prompts and responses by `key`.
- `outputs/<size>/original_predictions.jsonl`: unmodified original per-puzzle records.
- `results/<size>/`: evaluated records, summaries, runtime, historical manifest and provenance.
- `results/comparison.json`: selected cross-size results.
- `scripts/repeat_experiment.py`: three independent sampled runs per size and mean/standard-deviation report.
- `scripts/evaluate_archived_translations.py`: score saved single-run translations against local reference answers without regenerating text.

## Dataset access and Git

Source: https://huggingface.co/datasets/allenai/ZebraLogicBench . Official answer dataset: https://huggingface.co/datasets/allenai/ZebraLogicBench-private . The private files require authorized access. Both public and private dataset files are excluded by `.gitignore`. The ZIP includes them for your local reproduction; do not upload the entire ZIP as a public Git asset or force-add those files unless redistribution is permitted. Clone users should obtain their own files and put them at `datasets/public/grid_mode.parquet`, `datasets/private/grid_mode.parquet` and, if needed, `datasets/private/mc_mode.parquet`.

The experiments use grid mode only. Multiple-choice mode is included as requested but was not evaluated. Raw predictions may reproduce correct puzzle solutions; review what you intend to publish under the dataset's access conditions. No credentials are included.

## Install (Apple Silicon Mac)

Run in a normal Terminal with Metal GPU access:

```sh
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r req.txt
python -m unittest discover -s tests -v
python scripts/download_model.py
```

The recorded environment used Python 3.14 on Apple Silicon. MLX dependencies are platform-specific; this package does not implement a CUDA/Linux backend. Model weights are not bundled. The downloader retrieves `mlx-community/Qwen3-8B-4bit` at the revision in `datasets/metadata/model.json`. If that file is absent, it resolves the current revision and saves its SHA there before downloading. This may differ from the archived model revision, so treat a new run as a separate experiment. Full model card: https://huggingface.co/mlx-community/Qwen3-8B-4bit . This is a 4-bit quantized conversion of Qwen/Qwen3-8B.

## Run a new experiment

Use a fresh output directory for each size/configuration:

```sh
bash scripts/run_mac.sh --size '2*2' --limit 20 --out runs/2x2
bash scripts/run_mac.sh --size '3*4' --limit 20 --out runs/3x4
bash scripts/run_mac.sh --size '4*4' --limit 20 --out runs/4x4
```

Defaults: thinking enabled for both methods, greedy decoding, seed 0, 8,192 generated tokens per call, 20 puzzles selected in public dataset order. The hybrid translates one clue per call into a flat relation using category/value pairs, then executes Z3. No repair retries or compact-ID variants are used in these selected experiments. Each attribute's position lies between 1 and the number of houses; values within a category are all distinct. Z3 checks satisfiability and uniqueness.

## Translation evaluation

For every symbolic puzzle, the runner records `translation_eval` in `predictions.jsonl`. It checks each numbered clue for one generated relation, validates its operation and position terms against the puzzle domains, and evaluates that relation on the authorized reference solution. The summary reports clue coverage, valid clues, gold-consistent clues, and puzzles for which every clue is gold-consistent. Missing, duplicate, malformed and gold-contradicting clues receive no gold-consistency credit. This is a **necessary-condition metric**: a wrong or overly weak relation can still be true of the reference solution. To measure semantic fidelity directly, have an annotator independently label each clue with the intended relation and compare the generated relations with those labels, or have annotators judge equivalence blind to the model output. Z3 satisfiability and uniqueness also do not prove translation fidelity.

To evaluate the existing saved translations after installation, run `.venv/bin/python scripts/evaluate_archived_translations.py`. It writes `results/archived_translation_eval.json` and does not regenerate predictions. That report still describes one run per size.

## Three-run experiment

After installing the dependencies, downloading the model, and placing both grid-mode datasets at the paths above, run:

```sh
.venv/bin/python scripts/repeat_experiment.py run
```

This runs three separate seeds (11, 22, 33) at temperature 0.7 for each size, with the same 20 puzzle IDs, prompt, model, token budget, and scoring in both methods. Each run has its own directory under `runs/repeated/` and can resume after interruption. After all nine size/seed runs finish, the script writes `results/repeated_summary.json` with each run's puzzle accuracy, cell accuracy, failure rate, generation cost, clue coverage, clue validity, gold consistency, and per-size means and sample standard deviations. It also reports the within-run difference in puzzle accuracy between symbolic and direct. Recompute the summary without generating model calls with `.venv/bin/python scripts/repeat_experiment.py summarize`. Do not average across puzzle sizes; they have different difficulty. The existing archived greedy runs cannot substitute for independent sampled replicates.

For a 3×4-only experiment, run the three seeds under `runs/repeated/3x4/`, then summarize with `.venv/bin/python scripts/repeat_experiment.py summarize --size 3x4 --report results/3x4_three_run_summary.json`. The summarizer requires all three completed runs with identical puzzle IDs and settings.

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

Check the staged files before committing. The included `.gitignore` excludes public and private dataset files, future run directories, weights, caches and environments.
