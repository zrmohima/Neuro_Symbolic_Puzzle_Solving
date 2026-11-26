import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from translation_eval import evaluate_translation


class TranslationEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.row = {'puzzle': '1. Ada is in house 1.\n2. The cat lives next to Ada.\n3. The cat is in house 1.',
                    'size': '2*2'}
        self.gold = {'solution': {'header': ['House', 'Name', 'Pet'],
                                  'rows': [['1', 'Ada', 'dog'], ['2', 'Bob', 'cat']]}}
        self.domains = {'Name': ['Ada', 'Bob'], 'Pet': ['dog', 'cat']}

    def test_coverage_validity_and_gold_consistency_are_distinct(self):
        rules = [
            {'clue': 1, 'rule': {'op': 'eq', 'args': [['Name', 'Ada'], 1]}},
            {'clue': 2, 'rule': {'op': 'adjacent', 'args': [['Pet', 'cat'], ['Name', 'Ada']]}},
            {'clue': 3, 'rule': {'op': 'eq', 'args': [['Pet', 'cat'], 1]}},
        ]
        result = evaluate_translation(self.row, self.gold, rules, self.domains)
        self.assertEqual((result['covered_clues'], result['valid_clues'], result['gold_consistent_clues']), (3, 3, 2))
        self.assertEqual(result['clues'][2]['status'], 'contradicts_gold')

    def test_missing_and_invalid_clues_do_not_pass(self):
        rules = [{'clue': 1, 'rule': {'op': 'eq', 'args': [['Name', 'Nobody'], 1]}},
                 {'clue': 4, 'rule': {'op': 'eq', 'args': [['Name', 'Ada'], 1]}}]
        result = evaluate_translation(self.row, self.gold, rules, self.domains)
        self.assertEqual((result['covered_clues'], result['valid_clues'], result['gold_consistent_clues']), (1, 0, 0))
        self.assertEqual(result['extra_clues'], [4])


if __name__ == '__main__':
    unittest.main()
