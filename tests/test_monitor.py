"""Failure-path tests use fake hardware and never activate the webcam or OS hook."""
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import Mock, patch

from fastapi import HTTPException
from backend.app import Monitor, StartInput, TrialInput, trial


class FakeGuard:
    def __init__(self, callback):
        self.enabled = False
        self.error = None
    def start(self):
        self.enabled = True
        return True
    def stop(self):
        self.enabled = False


class MonitorTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = patch('backend.app.ROOT', Path(self.folder.name))
        self.root.start()
        self.addCleanup(self.root.stop)
        self.guard = patch('backend.app.WindowsGuard', FakeGuard)
        self.guard.start()
        self.addCleanup(self.guard.stop)

    def monitor(self):
        monitor = Monitor()
        self.addCleanup(monitor.stop)
        return monitor

    def test_unwritable_report_directory_rejects_start_without_guard(self):
        monitor = self.monitor()
        monitor.run = Mock()
        with patch.object(Path, 'write_text', side_effect=PermissionError('read only')):
            with self.assertRaises(HTTPException) as error:
                monitor.start(StartInput(consent=True, native_guard=True))
        self.assertEqual(error.exception.status_code, 503)
        self.assertFalse(monitor.active)
        self.assertFalse(monitor.guard.enabled)

    def test_camera_cleanup_failure_still_releases_session(self):
        monitor = self.monitor()
        cap = Mock()
        cap.isOpened.return_value = True
        cap.read.side_effect = RuntimeError('camera disconnected')
        cap.release.side_effect = RuntimeError('camera cleanup failed')
        fake_vision = Mock()
        with patch('backend.app.model_status', return_value={'a': True}), patch('backend.app.Vision', return_value=fake_vision), patch('cv2.VideoCapture', return_value=cap):
            monitor.start(StartInput(consent=True, mode='live', native_guard=True))
            monitor.worker.join(3)
        self.assertFalse(monitor.worker.is_alive())
        self.assertFalse(monitor.active)
        self.assertFalse(monitor.guard.enabled)
        fake_vision.close.assert_called_once()

    def test_cancel_during_model_loading_does_not_open_camera(self):
        monitor = self.monitor()
        entered = threading.Event()
        release = threading.Event()
        fake_vision = Mock()
        def delayed_vision():
            entered.set()
            release.wait(5)
            return fake_vision
        with patch('backend.app.model_status', return_value={'a': True}), patch('backend.app.Vision', side_effect=delayed_vision), patch('cv2.VideoCapture') as capture:
            monitor.start(StartInput(consent=True, mode='live'))
            self.assertTrue(entered.wait(2))
            stopper = threading.Thread(target=monitor.stop)
            stopper.start()
            self.assertTrue(monitor.stop_flag.wait(1))
            release.set()
            stopper.join(3)
            monitor.worker.join(3)
            capture.assert_not_called()
        self.assertFalse(monitor.active)
        fake_vision.close.assert_called_once()

    def test_watchdog_releases_guard_without_vision_progress(self):
        monitor = self.monitor()
        entered = threading.Event()
        def stalled_worker(_index):
            entered.set()
            monitor.stop_flag.wait(5)
        monitor.run = stalled_worker
        monitor.start(StartInput(consent=True, native_guard=True))
        self.assertTrue(entered.wait(1))
        monitor.last_heartbeat = time.monotonic()-21
        self.assertTrue(monitor.stop_flag.wait(2))
        monitor.worker.join(2)
        deadline = time.monotonic()+2
        while monitor.guard.enabled and time.monotonic()<deadline:
            time.sleep(.01)
        self.assertFalse(monitor.guard.enabled)
        self.assertIn('session_watchdog_released', [event['code'] for event in monitor.events])

    def test_export_keeps_events_when_disk_write_fails(self):
        monitor = self.monitor()
        monitor.start(StartInput(consent=True))
        with patch.object(Path, 'write_text', side_effect=PermissionError('disk failed')):
            monitor.security('clipboard_blocked')
            monitor.stop()
            report = monitor.report()
        self.assertFalse(report['active'])
        self.assertTrue(report['storage_error'])
        self.assertIn('clipboard_blocked', [event['code'] for event in report['events']])

    def test_trial_rejects_simulation_and_requires_second_person_consent(self):
        monitor = self.monitor()
        monitor.active = True
        monitor.observation = {'face_count':1, 'gaze':'center', 'calibrated':True, 'phones':[]}
        with patch('backend.app.monitor', monitor):
            with self.assertRaises(HTTPException) as rejected:
                trial(TrialInput(scenario='normal'))
            self.assertEqual(rejected.exception.status_code, 409)
            monitor.mode = 'live'
            with self.assertRaises(HTTPException) as rejected:
                trial(TrialInput(scenario='second_face'))
            self.assertEqual(rejected.exception.status_code, 400)
            self.assertEqual(monitor.trials.trials, [])
            trial(TrialInput(scenario='second_face', second_person_consents=True))
            self.assertEqual(len(monitor.trials.trials), 1)


if __name__ == '__main__':
    unittest.main()
