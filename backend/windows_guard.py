"""Reversible Windows keyboard hook. Never modifies registry or kills processes."""
import ctypes
from ctypes import wintypes
import os
import threading
import time

class WindowsGuard:
    def __init__(self, on_event):
        self.on_event = on_event
        self.thread = None
        self.thread_id = None
        self.enabled = False
        self.error = None
        self.last_event = 0
        self.ready = threading.Event()

    def start(self):
        if os.name != 'nt':
            self.error = 'Native keyboard guard is Windows-only'
            return False
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        self.ready.wait(3)
        return self.enabled

    def _run(self):
        user32 = ctypes.WinDLL('user32', use_last_error=True)
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        LRESULT = ctypes.c_ssize_t
        HOOKPROC = ctypes.WINFUNCTYPE(LRESULT, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)
        user32.SetWindowsHookExW.argtypes = [ctypes.c_int, HOOKPROC, wintypes.HINSTANCE, wintypes.DWORD]
        user32.SetWindowsHookExW.restype = wintypes.HANDLE
        user32.CallNextHookEx.argtypes = [wintypes.HANDLE, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM]
        user32.CallNextHookEx.restype = LRESULT
        user32.UnhookWindowsHookEx.argtypes = [wintypes.HANDLE]
        kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
        kernel32.GetModuleHandleW.restype = wintypes.HMODULE
        class Key(ctypes.Structure):
            _fields_ = [('vkCode', wintypes.DWORD), ('scanCode', wintypes.DWORD), ('flags', wintypes.DWORD),
                        ('time', wintypes.DWORD), ('dwExtraInfo', ctypes.c_size_t)]
        @HOOKPROC
        def callback(code, wp, lp):
            if code >= 0 and self.enabled:
                vk = ctypes.cast(lp, ctypes.POINTER(Key)).contents.vkCode
                ctrl = bool(user32.GetAsyncKeyState(0x11) & 0x8000)
                alt = bool(user32.GetAsyncKeyState(0x12) & 0x8000)
                blocked = vk in (0x5B, 0x5C, 0x2C) or (alt and vk in (0x09, 0x1B)) or (ctrl and vk in (0x43, 0x56, 0x1B))
                if blocked:
                    # Hook callback must be fast: defer recording to another thread.
                    now = time.monotonic()
                    if wp in (0x100, 0x104) and now - self.last_event > .5:
                        self.last_event = now
                        threading.Thread(target=self.on_event, args=('native_shortcut_blocked',), daemon=True).start()
                    return 1
            return user32.CallNextHookEx(None, code, wp, lp)
        self.callback = callback
        self.thread_id = kernel32.GetCurrentThreadId()
        hook = user32.SetWindowsHookExW(13, callback, kernel32.GetModuleHandleW(None), 0)
        if not hook:
            self.error = f'Keyboard hook failed: {ctypes.get_last_error()}'
            self.ready.set()
            return
        self.enabled = True
        self.ready.set()
        try:
            message = wintypes.MSG()
            while user32.GetMessageW(ctypes.byref(message), None, 0, 0) > 0:
                user32.TranslateMessage(ctypes.byref(message))
                user32.DispatchMessageW(ctypes.byref(message))
        finally:
            self.enabled = False
            user32.UnhookWindowsHookEx(hook)

    def stop(self):
        self.enabled = False
        if self.thread_id and os.name == 'nt':
            ctypes.windll.user32.PostThreadMessageW(self.thread_id, 0x12, 0, 0)
        if self.thread and self.thread is not threading.current_thread():
            self.thread.join(2)
