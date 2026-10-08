"""Read local measurement metadata only. Never requests /api/frame or saves pixels."""
import http.cookiejar
import json
import urllib.request

origin = 'http://127.0.0.1:8765'
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
with opener.open(origin+'/', timeout=5) as response:
    response.read()
with opener.open(origin+'/api/status?heartbeat=false', timeout=5) as response:
    status = json.load(response)
summary = {key: status[key] for key in ('active','mode','session_id','error','storage_error','latency_ms','native_guard','stopping','observation','validation')}
summary['event_counts'] = {}
for event in status['events']:
    summary['event_counts'][event['code']] = summary['event_counts'].get(event['code'], 0)+1
print(json.dumps(summary, ensure_ascii=False))
