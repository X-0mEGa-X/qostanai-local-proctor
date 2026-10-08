import unittest
from backend.rules import TemporalRules

class RuleTests(unittest.TestCase):
    def test_sustained_signal_emits_once_until_clear(self):
        rules = TemporalRules()
        obs = {'face_count': 1, 'gaze': 'down'}
        self.assertEqual(rules.update(obs, 0), [])
        self.assertEqual(rules.update(obs, 1.5), [])
        self.assertEqual(len(rules.update(obs, 3)), 1)
        self.assertEqual(rules.update(obs, 4), [])
        rules.update({'face_count': 1, 'gaze': 'center'}, 5)
        rules.update(obs, 6)
        rules.update(obs, 7.5)
        self.assertEqual(len(rules.update(obs, 9)), 1)

    def test_stall_does_not_create_violation(self):
        rules = TemporalRules()
        obs = {'face_count': 0}
        rules.update(obs, 0)
        self.assertEqual(rules.update(obs, 10), [])

    def test_unknown_face_count_is_not_absence(self):
        rules = TemporalRules()
        self.assertEqual(rules.update({}, 0), [])
        self.assertEqual(rules.update({}, 1), [])

    def test_phone_and_multiple_face_signals(self):
        rules = TemporalRules()
        obs = {'face_count': 2, 'phones': [{'raised': True}]}
        rules.update(obs, 0)
        self.assertEqual({e['code'] for e in rules.update(obs, 1.5)}, {'phone_visible', 'phone_raised', 'multiple_faces'})

    def test_absence_and_side_require_sustained_observation(self):
        for obs, expected in (({'face_count': 0}, 'no_face'), ({'face_count': 1, 'gaze': 'left'}, 'look_side')):
            with self.subTest(expected=expected):
                rules = TemporalRules()
                for timestamp in (0, 1, 2):
                    self.assertEqual(rules.update(obs, timestamp), [])
                self.assertEqual([e['code'] for e in rules.update(obs, 3)], [expected])
                self.assertEqual(rules.update(obs, 4), [])

    def test_brief_glance_clears_without_event(self):
        rules = TemporalRules()
        for timestamp, gaze in ((0,'center'), (.1,'down'), (.6,'down'), (.7,'center'), (1.7,'center'), (2.7,'center'), (3.7,'center')):
            self.assertEqual(rules.update({'face_count':1, 'gaze':gaze}, timestamp), [])

if __name__ == '__main__':
    unittest.main()
