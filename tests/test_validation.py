import json
import unittest
from backend.validation import TrialBook


class ValidationTests(unittest.TestCase):
    def test_results_require_human_confirmation_and_store_only_metadata(self):
        book = TrialBook()
        book.begin('phone', 10)
        observation = {'face_count':1, 'gaze':'center', 'phones':[{'raised':False}], 'frame':b'private pixels', 'landmarks':[1,2]}
        book.observe(observation, 100, 15, [])
        book.observe(observation, 200, 16, [{'code':'phone_visible'}])
        for second in range(17, 23):
            book.observe(observation, 150, second, [])
        book.tick(23)
        self.assertIsNone(book.status(23)['current']['missed_event_types'])
        book.confirm(True, 'Held phone for the cue interval')
        result = book.report()['trials'][0]
        self.assertTrue(result['assessable'])
        self.assertEqual(result['missed_event_types'], [])
        self.assertEqual(result['processing_ms_p50'], 150)
        self.assertEqual(result['processing_ms_p95'], 200)
        self.assertEqual(result['events'][0]['cue_to_event_s'], 1)
        self.assertNotIn('frame', result['samples'][0])
        self.assertNotIn('landmarks', result['samples'][0])
        json.dumps(book.report())

    def test_wrong_direction_and_false_alerts_are_preserved(self):
        book = TrialBook()
        book.begin('left', 0)
        for second in range(5,13):
            book.observe({'face_count':1,'gaze':'right','phones':[]}, 50, second, [{'code':'look_down'}] if second == 5 else [])
        book.tick(13)
        book.confirm(True, 'Looked to my left')
        result = book.status(13)['current']
        self.assertEqual(result['gaze_counts'], {'right':8})
        self.assertEqual(result['expected_gaze_fraction'], 0)
        self.assertEqual(result['missed_event_types'], ['look_side'])
        self.assertEqual(result['unexpected_event_types'], ['look_down'])
        self.assertEqual(result['unexpected_event_count'], 1)

    def test_interrupted_and_early_trials_are_not_scored_as_success(self):
        for early in (False, True):
            with self.subTest(early=early):
                book = TrialBook()
                book.begin('absence', 0)
                if early:
                    book.observe({'face_count':0}, 50, 2, [])
                book.observe({'face_count':0}, 50, 5, [])
                if early:
                    book.tick(13)
                else:
                    book.interrupt(6)
                book.confirm(True, '')
                result = book.status(13)['current']
                self.assertFalse(result['assessable'])
                self.assertIsNone(result['missed_event_types'])

    def test_empty_or_declined_trial_is_not_a_measured_miss(self):
        book = TrialBook()
        book.begin('normal', 0)
        book.tick(65)
        book.confirm(False, 'Did not perform trial')
        self.assertFalse(book.status(65)['current']['assessable'])
        self.assertIsNone(book.status(65)['current']['processing_ms_p50'])

    def test_duplicate_trial_cannot_overwrite_pending_evidence(self):
        book = TrialBook()
        book.begin('normal', 0)
        with self.assertRaises(ValueError):
            book.begin('phone', 1)
        book.tick(65)
        with self.assertRaises(ValueError):
            book.begin('phone', 66)
        self.assertEqual(len(book.trials), 1)

    def test_stalled_or_sparse_observations_are_inconclusive(self):
        for sample_times in ([5], [5, 6, 11, 12], [8, 9, 10, 11, 12], [5, 6, 7, 8]):
            with self.subTest(sample_times=sample_times):
                book = TrialBook()
                book.begin('phone', 0)
                for timestamp in sample_times:
                    book.observe({'face_count':1,'phones':[]}, 50, timestamp, [])
                book.tick(13)
                book.confirm(True, 'Performed the whole trial')
                result = book.report()['trials'][0]
                self.assertFalse(result['coverage_ok'])
                self.assertFalse(result['assessable'])
                self.assertIsNone(result['missed_event_types'])


if __name__ == '__main__':
    unittest.main()
