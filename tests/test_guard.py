"""Hook lifecycle regression with fake Win32 calls, never an actual keyboard hook."""
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from backend.windows_guard import WindowsGuard


class GuardTests(unittest.TestCase):
    def test_stop_during_install_never_enables_late_hook(self):
        user32, kernel32 = Mock(), Mock()
        entered, release = threading.Event(), threading.Event()
        def install(*_args):
            entered.set()
            release.wait(3)
            return 1
        user32.SetWindowsHookExW.side_effect = install
        user32.GetMessageW.return_value = 0
        kernel32.GetCurrentThreadId.return_value = 42
        guard = WindowsGuard(Mock())
        with patch('backend.windows_guard.os.name', 'nt'), \
             patch('ctypes.WinDLL', side_effect=lambda name, **_kw: user32 if name == 'user32' else kernel32, create=True), \
             patch('ctypes.WINFUNCTYPE', side_effect=lambda *_args: lambda fn: fn, create=True), \
             patch('ctypes.windll', SimpleNamespace(user32=user32), create=True):
            guard.thread = threading.Thread(target=guard._run)
            guard.thread.start()
            self.assertTrue(entered.wait(1))
            stopper = threading.Thread(target=guard.stop)
            stopper.start()
            self.assertTrue(guard.cancelled.wait(1))
            release.set()
            stopper.join(2)
            guard.thread.join(2)
        self.assertFalse(guard.enabled)
        self.assertFalse(guard.thread.is_alive())
        user32.UnhookWindowsHookEx.assert_called_once_with(1)
        user32.GetMessageW.assert_not_called()


if __name__ == '__main__':
    unittest.main()
