"""Run three independent sampled replicates and report per-size mean and SD.

Use with the project's virtualenv and local model/datasets. Existing archived
greedy runs are not counted as independent replicates.
"""
import argparse
import json
import statistics
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIZES = {'2x2': '2*2', '3x4': '3*4', '4x4': '4*4'}
SEEDS = (11, 22, 33)


def read_json(path):
    return json.loads(path.read_text())


def summarize(base, report_path, limit, size_labels=None):
    report = {'design': {'seeds': list(SEEDS), 'temperature': 0.7,
                         'puzzles_per_size': limit, 'replicates': len(SEEDS)}, 'sizes': {}}
    for label in size_labels or SIZES:
        size = SIZES[label]
        runs = []
        ids = None
        reference = None
        for seed in SEEDS:
            folder = base / label / f'seed-{seed}'
            manifest = read_json(folder / 'manifest.json')
            summary = read_json(folder / 'summary.json')
            predictions = [json.loads(line) for line in (folder / 'predictions.jsonl').read_text().splitlines()]
            if manifest['size'] != size or manifest['seed'] != seed or manifest['temperature'] != 0.7 or len(manifest['ids']) != limit:
                raise ValueError(f'Unexpected configuration in {folder}')
            current = {k: manifest[k] for k in ('model', 'model_revision', 'thinking', 'max_tokens', 'gold_sha256', 'data_sha256', 'source_sha256', 'solver_sha256', 'translation_eval_sha256')}
            if reference is None:
                reference = current
                ids = manifest['ids']
            elif current != reference or manifest['ids'] != ids:
                raise ValueError(f'Runs are not comparable: {folder}')
            keys = [(p['id'], p['method']) for p in predictions]
            if len(keys) != 2 * limit or len(set(keys)) != len(keys) or set(keys) != {(i, m) for i in ids for m in ('direct', 'symbolic')}:
                raise ValueError(f'Incomplete or duplicate predictions: {folder}')
            if any(p['score'] is None for p in predictions):
                raise ValueError(f'Unscored predictions: {folder}')
            t = summary['symbolic'].get('translation')
            if not t or t['total_clues'] <= 0:
                raise ValueError(f'Missing translation evaluation: {folder}')
            by_method = {m: [p for p in predictions if p['method'] == m] for m in ('direct', 'symbolic')}
            metrics = {}
            for method, items in by_method.items():
                metrics[method] = {
                    'puzzle_accuracy': sum(p['score']['exact'] for p in items) / limit,
                    'cell_accuracy': sum(p['score']['correct_cells'] for p in items) / sum(p['score']['total_cells'] for p in items),
                    'error_rate': sum('error' in p for p in items) / limit,
                    'mean_generation_seconds_per_puzzle': sum(p['generation_seconds'] for p in items) / limit,
                    'mean_generation_tokens_per_puzzle': sum(p['generation_tokens'] for p in items) / limit,
                }
            metrics['symbolic']['clue_coverage_rate'] = t['covered_clues'] / t['total_clues']
            metrics['symbolic']['clue_validity_rate'] = t['valid_clues'] / t['total_clues']
            metrics['symbolic']['gold_consistency_rate'] = t['gold_consistency_rate']
            metrics['symbolic']['fully_gold_consistent_puzzle_rate'] = t['fully_gold_consistent_puzzles'] / limit
            metrics['paired_puzzle_accuracy_delta'] = metrics['symbolic']['puzzle_accuracy'] - metrics['direct']['puzzle_accuracy']
            runs.append({'seed': seed, 'metrics': metrics})

        def aggregate(path):
            values = []
            for run in runs:
                value = run['metrics']
                for key in path:
                    value = value[key]
                values.append(value)
            return {'mean': statistics.mean(values), 'sd': statistics.stdev(values), 'per_run': values}

        report['sizes'][label] = {
            'ids': ids, 'runs': runs,
            'direct': {key: aggregate(('direct', key)) for key in runs[0]['metrics']['direct']},
            'symbolic': {key: aggregate(('symbolic', key)) for key in runs[0]['metrics']['symbolic']},
            'paired_puzzle_accuracy_delta': aggregate(('paired_puzzle_accuracy_delta',)),
        }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    print(f'Wrote {report_path}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('run', 'summarize'))
    parser.add_argument('--base', type=Path, default=ROOT / 'runs' / 'repeated')
    parser.add_argument('--report', type=Path, default=ROOT / 'results' / 'repeated_summary.json')
    parser.add_argument('--limit', type=int, default=20)
    parser.add_argument('--size', choices=('all', *SIZES), default='all')
    args = parser.parse_args()
    if args.limit < 1:
        parser.error('--limit must be positive')
    selected = tuple(SIZES) if args.size == 'all' else (args.size,)
    if args.action == 'run':
        for label in selected:
            size = SIZES[label]
            for seed in SEEDS:
                out = args.base / label / f'seed-{seed}'
                command = [sys.executable, str(ROOT / 'src' / 'run_benchmark.py'), '--size', size,
                           '--limit', str(args.limit), '--out', str(out), '--seed', str(seed),
                           '--temperature', '0.7']
                print('Running', label, 'seed', seed, flush=True)
                subprocess.run(command, cwd=ROOT, check=True)
    summarize(args.base, args.report, args.limit, selected)


if __name__ == '__main__':
    main()
