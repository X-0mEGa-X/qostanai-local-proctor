"""End-to-end local API check using a separate process and scripted observations."""
import http.cookiejar
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'http://127.0.0.1:8766'
env = dict(os.environ, PROCTOR_PORT='8766', PYTHONIOENCODING='utf-8')
process = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'backend.app:app', '--host', '127.0.0.1', '--port', '8766'],
    cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

def request(path, body=None, origin=ORIGIN):
    headers = {'Origin': origin}
    data = None
    if body is not None:
        headers['Content-Type'] = 'application/json'
        data = json.dumps(body).encode()
    return opener.open(urllib.request.Request(ORIGIN+path, data=data, headers=headers), timeout=10)

def fails(path, body, expected, origin=ORIGIN):
    try:
        request(path, body, origin)
        raise AssertionError('Expected rejection')
    except urllib.error.HTTPError as error:
        assert error.code == expected, (error.code, expected)

try:
    for _ in range(100):
        if process.poll() is not None:
            raise RuntimeError('API subprocess did not start')
        try:
            urllib.request.urlopen(ORIGIN+'/health', timeout=1)
            break
        except urllib.error.URLError:
            time.sleep(.1)
    fails('/api/start', {'consent': True}, 401)
    request('/')
    fails('/api/start', {'consent': True}, 403, 'https://example.com')
    fails('/api/start', {'consent': False}, 400)
    fails('/api/start', {'consent': True, 'mode': 'invented'}, 400)
    result = json.load(request('/api/start', {'consent': True, 'mode': 'simulation'}))
    fails('/api/start', {'consent': True}, 409)
    fails('/api/security', {'code': 'invented'}, 400)
    request('/api/security', {'code': 'clipboard_blocked'})
    for _ in range(11):
        time.sleep(1)
        status = json.load(request('/api/status'))
    codes = {event['code'] for event in status['events']}
    assert {'phone_visible', 'phone_raised', 'clipboard_blocked'} <= codes, codes
    assert all(event['source'] == 'simulation' for event in status['events'])
    report = json.load(request('/api/stop', {}))
    assert report['active'] is False
    assert report['session_id'] == result['session_id']
    saved = json.loads((ROOT/'data'/f"{result['session_id']}.json").read_text(encoding='utf-8'))
    assert saved['active'] is False and saved['ended_at']
    assert json.load(request('/api/report'))['session_id'] == result['session_id']
    assert request('/api/frame').status == 204
    print(json.dumps({'api_check': 'passed', 'signal_codes': sorted(codes), 'auth_origin_consent_conflict_checks': 'passed', 'saved_report': 'passed'}))
finally:
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
