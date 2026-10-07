"""One-time downloads. All inference is offline after setup."""
from pathlib import Path
import hashlib
import json
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
MODELS = {
    'yolov8n.pt': 'https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8n.pt',
    'face_landmarker.task': 'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task',
}

def main():
    folder = ROOT / 'models'
    folder.mkdir(exist_ok=True)
    manifest = {}
    for name, url in MODELS.items():
        path = folder / name
        if not path.exists():
            print('Downloading', name, flush=True)
            part = path.with_suffix(path.suffix + '.part')
            urllib.request.urlretrieve(url, part)
            part.replace(path)
        manifest[name] = {'source': url, 'size': path.stat().st_size, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        print(name, manifest[name]['size'], 'bytes', flush=True)
    (folder / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')

if __name__ == '__main__':
    main()
