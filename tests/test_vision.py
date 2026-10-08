"""Deterministic pipeline/calibration checks with fake model output, not accuracy trials."""
from types import SimpleNamespace as NS
import unittest
from unittest.mock import Mock
import numpy as np
import cv2
from backend.vision import Vision


def face_points():
    points = [NS(x=.5, y=.5) for _ in range(478)]
    for left, right, top, bottom, iris in ((33,133,159,145,468),(362,263,386,374,473)):
        points[left] = NS(x=.4,y=.5)
        points[right] = NS(x=.6,y=.5)
        points[top] = NS(x=.5,y=.45)
        points[bottom] = NS(x=.5,y=.55)
        points[iris] = NS(x=.5,y=.5)
    return points


class VisionTests(unittest.TestCase):
    def vision(self, faces=None, boxes=None):
        vision = Vision.__new__(Vision)
        vision.cv2, vision.np = cv2, np
        vision.mp = NS(Image=lambda **args: args['data'], ImageFormat=NS(SRGB=1))
        vision.yolo = Mock()
        vision.yolo.predict.return_value = [NS(boxes=boxes or [])]
        vision.face = Mock()
        vision.face.detect_for_video.return_value = NS(face_landmarks=faces or [], facial_transformation_matrixes=[np.eye(4)])
        vision.baseline, vision.samples, vision.last_ms = None, [], 0
        return vision

    def test_phone_overlay_never_enters_face_model_or_mutates_input(self):
        box = NS(xyxy=[np.array([10,10,100,100])], conf=[.9])
        vision = self.vision(boxes=[box])
        raw = np.zeros((480,640,3), dtype=np.uint8)
        obs, annotated = vision.analyze(raw)
        face_input = vision.face.detect_for_video.call_args.args[0]
        self.assertFalse(np.any(face_input), 'Face inference must receive clean camera pixels')
        self.assertFalse(np.any(raw), 'Caller owns the raw frame')
        self.assertTrue(np.any(annotated))
        self.assertEqual(len(obs['phones']), 1)
        for key in ('save', 'save_txt', 'save_crop', 'show'):
            self.assertIs(vision.yolo.predict.call_args.kwargs[key], False)

    def test_face_loss_resets_reported_calibration_progress(self):
        vision = self.vision()
        vision.samples = [[0,0,.5,.5]] * 19
        obs, _ = vision.analyze(np.zeros((480,640,3), dtype=np.uint8))
        self.assertEqual(obs['calibration_samples'], 0)
        self.assertFalse(obs['calibrated'])

    def test_twenty_valid_frames_then_recalibration(self):
        vision = self.vision(faces=[face_points()])
        for _ in range(20):
            obs, _ = vision.analyze(np.zeros((480,640,3), dtype=np.uint8))
        self.assertTrue(obs['calibrated'])
        obs, _ = vision.analyze(np.zeros((480,640,3), dtype=np.uint8))
        self.assertEqual(obs['gaze'], 'center')
        vision.calibrate()
        obs, _ = vision.analyze(np.zeros((480,640,3), dtype=np.uint8))
        self.assertFalse(obs['calibrated'])
        self.assertEqual(obs['calibration_samples'], 1)

    def test_relative_iris_directions_and_multiple_faces(self):
        vision = self.vision(faces=[face_points()])
        vision.baseline = np.array([0,0,.5,.5])
        for x,y,expected in ((.5,.54,'down'), (.55,.5,'right'), (.45,.5,'left'), (.5,.5,'center')):
            points = face_points()
            points[468] = points[473] = NS(x=x,y=y)
            vision.face.detect_for_video.return_value.face_landmarks = [points]
            obs, _ = vision.analyze(np.zeros((480,640,3), dtype=np.uint8))
            self.assertEqual(obs['gaze'], expected)
        vision.face.detect_for_video.return_value.face_landmarks = [face_points(), face_points()]
        obs, _ = vision.analyze(np.zeros((480,640,3), dtype=np.uint8))
        self.assertEqual(obs['face_count'], 2)
        self.assertEqual(obs['gaze'], 'unavailable')


if __name__ == '__main__':
    unittest.main()
