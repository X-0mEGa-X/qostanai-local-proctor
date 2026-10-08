import atexit
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import secrets
import threading
import time
import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .rules import TemporalRules
from .vision import Vision, model_status
from .windows_guard import WindowsGuard
from .validation import TrialBook

ROOT = Path(__file__).resolve().parents[1]
TOKEN = secrets.token_urlsafe(32)
PORT = int(os.environ.get('PROCTOR_PORT', '8765'))
ORIGIN = f'http://127.0.0.1:{PORT}'

class StartInput(BaseModel):
    mode: str = 'simulation'
    consent: bool = False
    native_guard: bool = False
    camera_index: int = Field(default=0, ge=0, le=9)

class SessionInput(BaseModel):
    session_id: str = Field(min_length=1, max_length=80)

class SecurityInput(SessionInput):
    code: str = Field(max_length=80)

class TrialInput(BaseModel):
    scenario: str = Field(max_length=30)
    second_person_consents: bool = False

class TrialConfirmation(BaseModel):
    completed: bool
    notes: str = Field(default='', max_length=1000)

class Monitor:
    def __init__(self):
        self.lock = threading.RLock()
        self.active = False
        self.mode = 'simulation'
        self.session_id = None
        self.events = []
        self.rules = TemporalRules()
        self.observation = {}
        self.jpeg = None
        self.started = 0
        self.ended_at = None
        self.elapsed_at_end = None
        self.worker = None
        self.error = None
        self.storage_error = None
        self.latency_ms = 0
        self.vision = None
        self.stop_flag = threading.Event()
        self.guard = WindowsGuard(self.security)
        self.last_heartbeat = 0
        self.security_last = {}
        self.calibration_requested = False
        self.trials = TrialBook()

    def record(self, event):
        with self.lock:
            if not self.active:
                return
            event = dict(event, id=len(self.events)+1, timestamp=datetime.now(timezone.utc).isoformat(),
                         elapsed_s=round(time.monotonic()-self.started, 1), source=event.get('source', self.mode))
            self.events.append(event)
            self.persist()

    def security(self, code, expected_session=None):
        with self.lock:
            if expected_session is not None and expected_session != self.session_id:
                return
            now = time.monotonic()
            if now - self.security_last.get(code, 0) < 1:
                return
            self.security_last[code] = now
            self.record({'code': code, 'severity': 'medium', 'source': 'environment',
                         'title': code.replace('_', ' ').capitalize()})

    def report(self):
        with self.lock:
            return {'session_id': self.session_id, 'mode': self.mode, 'active': self.active,
                    'started_at': self.started_at if self.session_id else None, 'ended_at': self.ended_at,
                    'elapsed_s': round(time.monotonic()-self.started) if self.active else self.elapsed_at_end or 0,
                    'error': self.error, 'storage_error': self.storage_error,
                    'validation': self.trials.report(),
                    'events': list(self.events), 'policy': 'Human review required; no automatic cheating verdict.',
                    'privacy': 'No video or images saved. Event metadata stays on this computer.',
                    'limits': ['Coarse calibrated gaze/head proxy', 'Phone raised is a position heuristic, not proof of photography',
                               'Window protection is a prototype, not a managed OS lockdown']}

    def persist(self):
        if not self.session_id:
            return True
        try:
            folder = ROOT / 'data'
            folder.mkdir(exist_ok=True)
            path = folder / f'{self.session_id}.json'
            tmp = path.with_suffix('.tmp')
            snapshot = self.report()
            snapshot['storage_error'] = None
            tmp.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding='utf-8')
            tmp.replace(path)
            self.storage_error = None
            return True
        except OSError as error:
            # Keep the in-memory report exportable; storage must not prevent release.
            self.storage_error = f'Local report could not be saved: {error}'
            return False

    def start(self, options):
        with self.lock:
            if self.active or (self.worker and self.worker.is_alive()):
                raise HTTPException(409, 'A session is active or still stopping')
            if not options.consent:
                raise HTTPException(400, 'Consent is required')
            if options.mode not in ('live', 'simulation'):
                raise HTTPException(400, 'Invalid mode')
            if options.mode == 'live' and not all(model_status().values()):
                raise HTTPException(400, 'Install models first: python scripts/download_models.py')
            self.active = True
            self.mode = options.mode
            self.session_id = str(uuid.uuid4())
            self.events, self.observation = [], {}
            self.security_last = {}
            self.calibration_requested = False
            self.rules = TemporalRules()
            self.trials = TrialBook()
            self.error, self.storage_error, self.jpeg = None, None, None
            self.latency_ms = 0
            self.started = time.monotonic()
            self.started_at = datetime.now(timezone.utc).isoformat()
            self.ended_at = None
            self.elapsed_at_end = None
            self.last_heartbeat = time.monotonic()
            self.stop_flag = threading.Event()
            self.guard = WindowsGuard(lambda code, session_id=self.session_id: self.security(code, session_id))
            # Verify report storage before activating any protection or camera.
            if not self.persist():
                self.active = False
                self.stop_flag.set()
                self.ended_at = datetime.now(timezone.utc).isoformat()
                self.elapsed_at_end = 0
                raise HTTPException(503, self.storage_error)
            if options.native_guard:
                self.guard.start()
                if not self.guard.enabled:
                    self.security('native_guard_unavailable')
            self.worker = threading.Thread(target=self.run, args=(options.camera_index,), daemon=True)
            self.worker.start()
            threading.Thread(target=self.watchdog, args=(self.session_id, self.stop_flag), daemon=True).start()

    def stop(self, expected_session=None):
        with self.lock:
            if expected_session is not None and expected_session != self.session_id:
                return
            session_id, guard, worker = self.session_id, self.guard, self.worker
            self.active = False
            self.stop_flag.set()
            self.trials.interrupt(time.monotonic())
            self.jpeg = None
            self.ended_at = self.ended_at or datetime.now(timezone.utc).isoformat()
            if self.elapsed_at_end is None:
                self.elapsed_at_end = round(time.monotonic()-self.started) if self.session_id else 0
        guard.stop()
        if worker and worker is not threading.current_thread():
            worker.join(3)
        with self.lock:
            if session_id == self.session_id:
                self.persist()

    def watchdog(self, session_id, flag):
        # Independent from vision so a stalled detector cannot keep keys blocked.
        while not flag.wait(.5):
            with self.lock:
                if session_id != self.session_id:
                    return
                now = time.monotonic()
                expired = self.active and (now-self.last_heartbeat > 20 or now-self.started > 3600)
            if expired:
                self.security('session_watchdog_released', expected_session=session_id)
                self.stop(expected_session=session_id)
                return

    def simulation(self, elapsed):
        stage = int(elapsed) % 40
        obs = {'face_count': 1, 'phones': [], 'gaze': 'center', 'calibrated': True, 'calibration_samples': 20}
        if 6 <= stage < 12:
            obs['phones'] = [{'confidence': .92, 'bbox': [.57, .25, .73, .65], 'raised': True}]
        if 14 <= stage < 20:
            obs['gaze'] = 'down'
        if 22 <= stage < 27:
            obs['face_count'] = 2
        if 29 <= stage < 35:
            obs['face_count'] = 0
            obs['gaze'] = 'unavailable'
        if 36 <= stage < 40:
            obs['gaze'] = 'left'
        return obs

    def run(self, camera_index):
        cap = None
        vision = None
        session_id, flag = self.session_id, self.stop_flag
        try:
            if self.mode == 'live':
                import cv2
                vision = Vision()
                with self.lock:
                    if flag.is_set():
                        return
                    self.vision = vision
                cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW if os.name == 'nt' else cv2.CAP_ANY)
                if not cap.isOpened():
                    raise RuntimeError('Camera unavailable. Close other camera apps or try another index.')
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            while not flag.is_set():
                now = time.monotonic()
                t0 = time.perf_counter()
                jpeg = None
                if self.mode == 'simulation':
                    obs = self.simulation(now-self.started)
                else:
                    ok, frame = cap.read()
                    if not ok:
                        raise RuntimeError('Camera disconnected or frame read failed')
                    with self.lock:
                        if self.calibration_requested:
                            vision.calibrate()
                            self.calibration_requested = False
                    obs, frame = vision.analyze(frame)
                    ok, encoded = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
                    if ok:
                        jpeg = encoded.tobytes()
                with self.lock:
                    if flag.is_set():
                        break
                    self.latency_ms = round((time.perf_counter()-t0)*1000)
                    self.observation, self.jpeg = obs, jpeg
                    observed_at = time.monotonic()
                    events = self.rules.update(obs, observed_at)
                    trial_finished = self.trials.observe(obs, self.latency_ms, observed_at, events)
                    for event in events:
                        self.record(event)
                    if trial_finished:
                        self.persist()
                flag.wait(.15 if self.mode == 'live' else .25)
        except Exception as error:
            with self.lock:
                self.error = str(error)
                self.record({'code': 'monitor_error', 'severity': 'high', 'title': self.error})
        finally:
            # Release protection before potentially slow/failing driver cleanup.
            self.stop(expected_session=session_id)
            for resource, close_method in ((cap, 'release'), (vision, 'close')):
                if resource is not None:
                    try:
                        getattr(resource, close_method)()
                    except Exception as error:
                        with self.lock:
                            self.error = f'{self.error + "; " if self.error else ""}Cleanup failed: {error}'
            with self.lock:
                self.vision = None
                self.persist()

monitor = Monitor()
atexit.register(monitor.stop)

@asynccontextmanager
async def lifespan(app):
    yield
    monitor.stop()

app = FastAPI(title='Qostanai Local Proctor', lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)

@app.middleware('http')
async def boundary(request: Request, call_next):
    if request.headers.get('host') not in (f'127.0.0.1:{PORT}', f'localhost:{PORT}', 'testserver'):
        return JSONResponse({'detail': 'Invalid host'}, status_code=403)
    if request.url.path.startswith('/api/'):
        if request.cookies.get('proctor_session') != TOKEN:
            return JSONResponse({'detail': 'Open the application first'}, status_code=401)
        if request.method != 'GET' and request.headers.get('origin') != f'http://{request.headers.get("host")}':
            return JSONResponse({'detail': 'Invalid origin'}, status_code=403)
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self'; img-src 'self' blob: data:; connect-src 'self'; frame-ancestors 'none'"
    return response

@app.get('/')
def index():
    response = FileResponse(ROOT / 'frontend/index.html')
    response.set_cookie('proctor_session', TOKEN, httponly=True, samesite='strict')
    return response

@app.get('/health')
def health():
    return {'ok': True, 'application': 'qostanai-local-proctor'}

@app.get('/api/status')
def status(heartbeat: bool = True):
    with monitor.lock:
        now = time.monotonic()
        if heartbeat:
            monitor.last_heartbeat = now
        if monitor.trials.tick(now):
            monitor.persist()
        return {'active': monitor.active, 'mode': monitor.mode, 'session_id': monitor.session_id,
                'validation': monitor.trials.status(now),
                'observation': monitor.observation, 'events': list(monitor.events), 'error': monitor.error,
                'elapsed_s': (round(time.monotonic()-monitor.started) if monitor.active else monitor.elapsed_at_end or 0),
                'latency_ms': monitor.latency_ms, 'models': model_status(),
                'native_guard': monitor.guard.enabled, 'guard_error': monitor.guard.error,
                'storage_error': monitor.storage_error, 'vision_ready': monitor.active and monitor.vision is not None,
                'stopping': not monitor.active and bool(monitor.worker and monitor.worker.is_alive())}

@app.post('/api/start')
def start(options: StartInput):
    monitor.start(options)
    return {'session_id': monitor.session_id}

@app.post('/api/stop')
def stop(options: SessionInput):
    monitor.stop(expected_session=options.session_id)
    return monitor.report()

@app.post('/api/calibrate')
def calibrate():
    with monitor.lock:
        if not monitor.active or not monitor.vision:
            raise HTTPException(409, 'Live vision is not ready')
        if monitor.trials.trials and monitor.trials.trials[-1]['state'] in ('countdown', 'measuring'):
            raise HTTPException(409, 'Finish the current trial before recalibrating')
        monitor.calibration_requested = True
    return {'ok': True}

@app.post('/api/trial')
def trial(options: TrialInput):
    with monitor.lock:
        if not monitor.active or monitor.mode != 'live' or not monitor.observation.get('calibrated'):
            raise HTTPException(409, 'Start LIVE mode and complete calibration first')
        obs = monitor.observation
        if obs.get('face_count') != 1 or obs.get('gaze') != 'center' or obs.get('phones'):
            raise HTTPException(409, 'Return to one face, centered gaze, and no phone before starting a trial')
        if options.scenario == 'second_face' and not options.second_person_consents:
            raise HTTPException(400, 'Confirm that the second person consents before this trial')
        try:
            monitor.trials.begin(options.scenario, time.monotonic())
        except ValueError as error:
            raise HTTPException(400, str(error)) from error
        monitor.persist()
        return monitor.trials.status(time.monotonic())

@app.post('/api/trial/confirm')
def confirm_trial(options: TrialConfirmation):
    with monitor.lock:
        try:
            monitor.trials.confirm(options.completed, options.notes)
        except ValueError as error:
            raise HTTPException(409, str(error)) from error
        monitor.persist()
        return monitor.trials.status(time.monotonic())

@app.post('/api/security')
def security(event: SecurityInput):
    if event.code not in {'focus_lost', 'tab_hidden', 'fullscreen_left', 'clipboard_blocked', 'shortcut_blocked', 'navigation_blocked', 'window_blocked', 'emergency_exit', 'desktop_guard_started', 'desktop_guard_stopped'}:
        raise HTTPException(400, 'Unknown event')
    monitor.security(event.code, expected_session=event.session_id)
    return {'ok': True}

@app.get('/api/frame')
def frame():
    with monitor.lock:
        if not monitor.active or not monitor.jpeg:
            return Response(status_code=204)
        return Response(monitor.jpeg, media_type='image/jpeg')

@app.get('/api/report')
def report():
    return JSONResponse(monitor.report(), headers={'Content-Disposition': f'attachment; filename="proctor-{monitor.session_id or "empty"}.json"'})

app.mount('/assets', StaticFiles(directory=ROOT / 'frontend'), name='assets')
