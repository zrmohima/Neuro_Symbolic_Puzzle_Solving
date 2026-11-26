"""Add gold-consistency diagnostics to archived symbolic predictions without model calls."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))


def main():
    import pyarrow.parquet as pq
    from solver import domains
    from translation_eval import evaluate_translation

    public = {r['id']: r for r in pq.read_table(ROOT / 'datasets/public/grid_mode.parquet').to_pylist()}
    gold = {r['id']: r for r in pq.read_table(ROOT / 'datasets/private/grid_mode.parquet').to_pylist()}
    report = {'description': 'Archived single-run per-clue gold consistency; not semantic equivalence', 'sizes': {}}
    for size in ('2x2', '3x4', '4x4'):
        path = ROOT / 'results' / size / 'evaluated_predictions.jsonl'
        records = [json.loads(line) for line in path.read_text().splitlines()]
        symbolic = [r for r in records if r['method'] == 'symbolic']
        details = []
        for record in symbolic:
            row = public[record['id']]
            truth = gold[record['id']]
            if row['puzzle'] != truth['puzzle'] or row['solution']['header'] != truth['solution']['header']:
                raise ValueError(f'Dataset mismatch: {record["id"]}')
            result = evaluate_translation(row, truth, record.get('constraints', []), domains(row))
            details.append({'id': record['id'], **result})
        total = sum(d['total_clues'] for d in details)
        report['sizes'][size] = {
            'puzzles': len(details), 'total_clues': total,
            'covered_clues': sum(d['covered_clues'] for d in details),
            'valid_clues': sum(d['valid_clues'] for d in details),
            'gold_consistent_clues': sum(d['gold_consistent_clues'] for d in details),
            'gold_consistency_rate': sum(d['gold_consistent_clues'] for d in details) / total if total else None,
            'fully_gold_consistent_puzzles': sum(d['gold_consistent_clues'] == d['total_clues'] and not d['extra_clues'] for d in details),
            'details': details,
        }
    dest = ROOT / 'results/archived_translation_eval.json'
    dest.write_text(json.dumps(report, indent=2) + '\n')
    print(f'Wrote {dest}')


if __name__ == '__main__':
    main()
