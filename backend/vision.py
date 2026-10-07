"""Local YOLOv8n + MediaPipe Face Landmarker (478-point face mesh)."""
from pathlib import Path
import math
import time

ROOT = Path(__file__).resolve().parents[1]

def model_status():
    return {name: (ROOT / 'models' / name).is_file()
            for name in ('yolov8n.pt', 'face_landmarker.task')}

class Vision:
    def __init__(self):
        import cv2
        import mediapipe as mp
        import numpy as np
        from ultralytics import YOLO
        self.cv2, self.mp, self.np = cv2, mp, np
        self.yolo = YOLO(str(ROOT / 'models/yolov8n.pt'))
        options = mp.tasks.vision.FaceLandmarkerOptions(
            # MediaPipe native file loading can fail on Windows Cyrillic paths.
            base_options=mp.tasks.BaseOptions(model_asset_buffer=(ROOT / 'models/face_landmarker.task').read_bytes()),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_faces=3, output_facial_transformation_matrixes=True,
            min_face_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.face = mp.tasks.vision.FaceLandmarker.create_from_options(options)
        self.baseline = None
        self.samples = []
        self.last_ms = 0

    def calibrate(self):
        self.baseline = None
        self.samples = []

    @staticmethod
    def eye_ratio(points, iris, left, right, top, bottom):
        x0, x1 = sorted([points[left].x, points[right].x])
        y0, y1 = sorted([points[top].y, points[bottom].y])
        return ((points[iris].x - x0) / max(x1 - x0, 0.0001),
                (points[iris].y - y0) / max(y1 - y0, 0.0001))

    def analyze(self, frame):
        cv2, mp, np = self.cv2, self.mp, self.np
        h, w = frame.shape[:2]
        result = self.yolo.predict(frame, imgsz=640, conf=0.35, classes=[67], device='cpu', verbose=False)[0]
        phones = []
        for box in result.boxes:
            x1, y1, x2, y2 = [float(x) for x in box.xyxy[0]]
            # Position heuristic only; camera orientation / shutter are not observable.
            raised = (y1 + y2) / (2 * h) < 0.65 and (x2 - x1) * (y2 - y1) / (w * h) > 0.008
            phones.append({'bbox': [round(x1/w, 3), round(y1/h, 3), round(x2/w, 3), round(y2/h, 3)],
                           'confidence': round(float(box.conf[0]), 3), 'raised': raised})
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (74, 171, 255), 2)
            cv2.putText(frame, 'PHONE', (int(x1), max(20, int(y1)-8)), cv2.FONT_HERSHEY_SIMPLEX, .6, (74, 171, 255), 2)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        timestamp = max(self.last_ms + 1, int(time.monotonic() * 1000))
        self.last_ms = timestamp
        faces = self.face.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), timestamp)
        observation = {'face_count': len(faces.face_landmarks), 'phones': phones, 'gaze': 'unavailable',
                       'calibrated': self.baseline is not None, 'calibration_samples': len(self.samples)}
        for points in faces.face_landmarks:
            for index in (1, 33, 133, 362, 263, 468, 473):
                point = points[index]
                cv2.circle(frame, (int(point.x * w), int(point.y * h)), 2, (180, 226, 62), -1)
        if len(faces.face_landmarks) != 1:
            if self.baseline is None:
                self.samples.clear()
            return observation, frame
        points = faces.face_landmarks[0]
        rotation = np.asarray(faces.facial_transformation_matrixes[0])[:3, :3]
        yaw = math.degrees(math.atan2(float(rotation[0, 2]), float(rotation[2, 2])))
        pitch = math.degrees(math.atan2(-float(rotation[1, 2]), math.hypot(float(rotation[0, 2]), float(rotation[2, 2]))))
        ex1, ey1 = self.eye_ratio(points, 468, 33, 133, 159, 145)
        ex2, ey2 = self.eye_ratio(points, 473, 362, 263, 386, 374)
        sample = [yaw, pitch, (ex1+ex2)/2, (ey1+ey2)/2]
        if self.baseline is None:
            self.samples.append(sample)
            if len(self.samples) >= 20:
                self.baseline = np.median(self.samples, axis=0)
            observation['calibration_samples'] = len(self.samples)
            observation['calibrated'] = self.baseline is not None
            observation['gaze'] = 'calibrating'
            return observation, frame
        dyaw, dpitch, dex, dey = np.asarray(sample) - self.baseline
        # Coarse proxy combining head rotation and iris location, not eye-tracker accuracy.
        gaze = 'center'
        if dpitch > 15 or dey > .25:
            gaze = 'down'
        elif abs(dyaw) > 20 or abs(dex) > .18:
            gaze = 'left' if dyaw < -20 or dex < -.18 else 'right'
        observation.update(gaze=gaze, yaw_deg=round(float(dyaw), 1), pitch_deg=round(float(dpitch), 1))
        return observation, frame

    def close(self):
        self.face.close()
