# Qwen3-8B and Z3: ZebraLogicBench experiments

This project investigates the effectiveness of neuro-symbolic reasoning for solving logic grid puzzles using Qwen3-8B and Z3. Using ZebraLogicBench, we compare direct LLM-based reasoning with a neuro-symbolic framework that translates natural-language clues into formal logical constraints. The evaluation examines puzzle accuracy, constraint translation consistency, computational efficiency, and system reliability.
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

These preliminary results represent individual development runs using identical puzzle instances for both approaches. The 4×4 configuration was selected through exploratory experimentation, and subsequent variants with lower performance are not included in this comparison. These findings are reported separately from the multi-seed evaluation and do not establish an accuracy improvement from integrating Z3. Unsuccessful predictions receive zero credit, and house-number cells are excluded from cell accuracy calculations.

## Three-run 2×2 results

The same 20 development puzzles were run with both methods at temperature 0.7 using seeds 11, 22 and 33. Every run completed 20 predictions per method. The mean and sample standard deviation are across these three sampled runs; the archived greedy result above is excluded.

| Seed | Qwen puzzle accuracy | Qwen cell accuracy | Qwen + Z3 puzzle accuracy | Qwen + Z3 cell accuracy | Gold-consistent clues |
|---|---:|---:|---:|---:|---:|
| 11 | 15/20 (75%) | 60/80 (75%) | 20/20 (100%) | 80/80 (100%) | 38/38 (100%) |
| 22 | 14/20 (70%) | 56/80 (70%) | 20/20 (100%) | 80/80 (100%) | 38/38 (100%) |
| 33 | 16/20 (80%) | 64/80 (80%) | 19/20 (95%) | 76/80 (95%) | 37/38 (97.4%) |
| Mean ± SD | 75.0% ± 5.0 pp | 75.0% ± 5.0 pp | 98.3% ± 2.9 pp | 98.3% ± 2.9 pp | 99.1% ± 1.5 pp |

The neuro-symbolic approach achieved a mean puzzle accuracy of 98.3%, compared with 75.0% for direct Qwen3 under the strict evaluation protocol, representing a difference of 23.3 percentage points. The approach also demonstrated strong constraint translation consistency across all three runs. Detailed experimental metrics and computational costs are available in `results/2x2_three_run_summary.json`, while `results/repeated_summary.json` provides consolidated results across all three puzzle sizes.

**Evaluation Analysis:** Post-hoc output normalization increased the direct Qwen3 puzzle accuracy from 75.0% to 100% across the three 2×2 experimental runs without modifying the predicted attribute values. The neuro-symbolic approach achieved 99.1% gold consistency, with only one constraint validation failure across all three runs. These findings highlight the importance of structured output handling and reliable constraint translation in evaluating end-to-end reasoning systems. The reported primary accuracy reflects pipeline reliability rather than reasoning capability alone.

**Three-run 3×4 results**

The same 20 development puzzles were run with both methods at temperature 0.7 using seeds 11, 22 and 33. All three runs completed 20 predictions per method. The mean and sample standard deviation are across the three runs; the archived greedy result above is excluded.

| Seed | Qwen puzzle accuracy | Qwen cell accuracy | Qwen + Z3 puzzle accuracy | Qwen + Z3 cell accuracy | Gold-consistent clues |
|---|---:|---:|---:|---:|---:|
| 11 | 11/20 (55%) | 132/240 (55%) | 16/20 (80%) | 192/240 (80%) | 121/129 (93.8%) |
| 22 | 11/20 (55%) | 132/240 (55%) | 17/20 (85%) | 204/240 (85%) | 126/129 (97.7%) |
| 33 | 15/20 (75%) | 180/240 (75%) | 15/20 (75%) | 180/240 (75%) | 123/129 (95.3%) |
| Mean ± SD | 61.7% ± 11.5 pp | 61.7% ± 11.5 pp | 80.0% ± 5.0 pp | 80.0% ± 5.0 pp | 95.6% ± 2.0 pp |

The neuro-symbolic approach achieved a mean puzzle accuracy of 80.0%, compared with 61.7% for direct Qwen3 under the strict evaluation protocol, representing a difference of 18.3 percentage points. The experiments also demonstrate strong constraint translation consistency across all three runs. Detailed experimental metrics and computational costs are available in `results/3x4_three_run_summary.json`.

**Evaluation Analysis:** Post-hoc output normalization increased the direct Qwen3 puzzle accuracy from 61.7% to 100% across the three 3×4 experimental runs without modifying the predicted attribute values. The neuro-symbolic approach achieved 95.6% gold consistency, with domain validation requirements influencing its overall performance. These findings highlight the importance of structured output handling and accurate constraint translation in evaluating end-to-end reasoning systems. The reported primary accuracy reflects pipeline reliability rather than reasoning capability alone.
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
- `datasets/private/`: Authorized reference datasets used for evaluation; excluded from version control.- `datasets/metadata/`: download metadata, dataset checksum and pinned model revision.
- `prompts/<size>/inputs.jsonl`: exact rendered model inputs, including the chat template.
- `outputs/<size>/responses.jsonl`: raw model responses, token counts, timing and stop reasons. Join prompts and responses by `key`.
- `outputs/<size>/original_predictions.jsonl`: unmodified original per-puzzle records.
- `results/<size>/`: evaluated records, summaries, runtime, historical manifest and provenance.
- `results/comparison.json`: selected cross-size results.
- `scripts/repeat_experiment.py`: three independent sampled runs per size and mean/standard-deviation report.
- `scripts/evaluate_archived_translations.py`: score saved single-run translations against local reference answers without regenerating text.

## Dataset

This project uses ZebraLogicBench to evaluate logical reasoning through structured logic grid puzzles.

- Public benchmark: [ZebraLogicBench](https://huggingface.co/datasets/allenai/ZebraLogicBench)
- Reference solutions: [ZebraLogicBench-private](https://huggingface.co/datasets/allenai/ZebraLogicBench-private)

All reported experiments use the grid-mode dataset. Reference solutions are used exclusively for evaluation.

Dataset files are excluded from version control and must be obtained independently. Place the required files in the following directories:

- `datasets/public/grid_mode.parquet`
- `datasets/private/grid_mode.parquet`

Access to the private reference dataset requires authorization. Dataset and prediction redistribution must comply with the original dataset's access conditions.

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

The framework evaluates individual clue translations based on coverage, structural validity, and consistency with the reference solution. Each generated relation is validated against the corresponding puzzle domains before symbolic solving. Missing, duplicate, invalid, and reference-inconsistent relations receive no gold-consistency credit.

Gold consistency measures whether a translated relation is satisfied by the reference solution but does not establish semantic equivalence with the original natural-language clue. Similarly, Z3 satisfiability and uniqueness checks establish properties of the encoded constraints rather than the semantic correctness of their translations.
To evaluate the existing saved translations after installation, run `.venv/bin/python scripts/evaluate_archived_translations.py`. It writes `results/archived_translation_eval.json` and does not regenerate predictions. That report still describes one run per size.

## Three-run experiment

After installing the dependencies, downloading the model, and placing both grid-mode datasets at the paths above, run:

```sh
.venv/bin/python scripts/repeat_experiment.py run
```

This runs three separate seeds (11, 22, 33) at temperature 0.7 for each size, with the same 20 puzzle IDs, prompt, model, token budget, and scoring in both methods. Each run has its own directory under `runs/repeated/` and can resume after interruption. After all nine size/seed runs finish, the script writes `results/repeated_summary.json` with each run's puzzle accuracy, cell accuracy, failure rate, generation cost, clue coverage, clue validity, gold consistency, and per-size means and sample standard deviations. It also reports the within-run difference in puzzle accuracy between symbolic and direct. Recompute the summary without generating model calls with `.venv/bin/python scripts/repeat_experiment.py summarize`. Results are reported separately for each puzzle size to account for differences in puzzle complexity. Preliminary greedy-decoding experiments are excluded from the multi-seed statistical analysis.

For a 3×4-only experiment, run the three seeds under `runs/repeated/3x4/`, then summarize with `.venv/bin/python scripts/repeat_experiment.py summarize --size 3x4 --report results/3x4_three_run_summary.json`. The summarizer requires all three completed runs with identical puzzle IDs and settings.

The direct reasoning prompt requires satisfaction of all clues and category uniqueness constraints. The table validator supports permitted output formats, orders house rows, and checks for missing or duplicate houses and incomplete solutions. Predicted attribute values are preserved without correction, and evaluation uses case-insensitive comparisons after removing surrounding whitespace.

`--prepare-only` checks selection and answers without loading MLX. The model config must exist first. Rerun an identical command to resume from saved calls. Do not run multiple processes against the same output directory. `--max-tokens` or `--no-thinking` changes the experiment; choose a different output directory. Runtime metrics count model generation, not complete wall time or dataset/model downloads.

## Evaluation Protocol and Reproducibility

The preliminary 4×4 direct reasoning results were reevaluated using an updated output validator, yielding a puzzle accuracy of 70.0% without regenerating model responses or modifying predicted attribute values. The corresponding neuro-symbolic result remained unchanged.

Original predictions, evaluated outputs, experimental configurations, and provenance metadata are preserved to support reproducibility and transparency. Preliminary single-run results and subsequent multi-seed experiments are reported separately.

New experiments should use dedicated output directories rather than archived result directories.


