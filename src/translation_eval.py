"""Check each flat Z3 relation against the reference solution.

Gold consistency is a necessary condition for a faithful translation, not proof
of semantic equivalence to the natural-language clue.
"""
import re


def numbered_clues(puzzle):
    return [int(n) for n in re.findall(r'^(\d+)\.\s+.+', puzzle, re.M)]


def evaluate_translation(row, gold, constraints, domain_values):
    """Return per-clue parse/validation/gold-consistency diagnostics."""
    ds = domain_values
    header = gold['solution']['header']
    houses = {str(r[0]): dict(zip(header[1:], r[1:])) for r in gold['solution']['rows']}
    positions = {(category, value): int(house) for house, values in houses.items()
                 for category, value in values.items()}
    expected = numbered_clues(row['puzzle'])
    by_clue = {}
    for item in constraints:
        if isinstance(item, dict) and type(item.get('clue')) is int:
            by_clue.setdefault(item['clue'], []).append(item.get('rule'))

    def position(term):
        if type(term) is int and 1 <= term <= len(houses):
            return term
        if (isinstance(term, list) and len(term) == 2
                and all(isinstance(x, str) for x in term)):
            category, value = term
            if category in ds and value in ds[category]:
                return positions[(category, value)]
        raise ValueError('Unknown or invalid position term')

    def satisfies(rule):
        if not isinstance(rule, dict) or not isinstance(rule.get('args'), list) or len(rule['args']) != 2:
            raise ValueError('Invalid relation shape')
        op = rule.get('op')
        a, b = map(position, rule['args'])
        if op == 'eq': return a == b
        if op == 'ne': return a != b
        if op == 'lt': return a < b
        if op == 'immediately_left': return a + 1 == b
        if op == 'adjacent': return abs(a-b) == 1
        if op == 'distance':
            k = rule.get('distance')
            if type(k) is not int or not 1 <= k < len(houses):
                raise ValueError('Invalid distance')
            return abs(a-b) == k
        raise ValueError('Unknown relation')

    details = []
    for clue in expected:
        rules = by_clue.get(clue, [])
        if len(rules) != 1:
            details.append({'clue': clue, 'status': 'missing' if not rules else 'duplicate'})
            continue
        try:
            valid = satisfies(rules[0])
            details.append({'clue': clue, 'status': 'consistent' if valid else 'contradicts_gold'})
        except (ValueError, KeyError, TypeError) as exc:
            details.append({'clue': clue, 'status': 'invalid', 'message': str(exc)})
    return {'total_clues': len(expected), 'extra_clues': sorted(set(by_clue)-set(expected)),
            'clues': details,
            'covered_clues': sum(d['status'] not in ('missing', 'duplicate') for d in details),
            'valid_clues': sum(d['status'] in ('consistent', 'contradicts_gold') for d in details),
            'gold_consistent_clues': sum(d['status'] == 'consistent' for d in details)}
