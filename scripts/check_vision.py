"""Smoke check: model loading and inference, not an accuracy benchmark."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import json
import numpy as np
from backend.vision import Vision

vision = Vision()
try:
    observation, frame = vision.analyze(np.zeros((480, 640, 3), dtype=np.uint8))
    assert observation['face_count'] == 0
    assert observation['phones'] == []
    print(json.dumps({'model_inference': 'passed', 'blank_frame_observation': observation, 'accuracy_validated': False}))
finally:
    vision.close()
