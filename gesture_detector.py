import math
import os
import time
import urllib.request

import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hand_landmarker.task")

WRIST = 0
THUMB_TIP, THUMB_IP, THUMB_MCP = 4, 3, 2
INDEX_TIP, INDEX_PIP, INDEX_MCP = 8, 6, 5
MIDDLE_TIP, MIDDLE_PIP, MIDDLE_MCP = 12, 10, 9
RING_TIP, RING_PIP, RING_MCP = 16, 14, 13
PINKY_TIP, PINKY_PIP, PINKY_MCP = 20, 18, 17

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17),
]


def _ensure_model():
    if not os.path.exists(MODEL_PATH):
        print("Downloading hand landmark model (one-time, ~10 MB)...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("Model downloaded.")


class HandGestureDetector:
    def __init__(self, max_hands=1, detection_confidence=0.5, tracking_confidence=0.5):
        _ensure_model()
        base_options = mp_python.BaseOptions(model_asset_path=MODEL_PATH)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=max_hands,
            min_hand_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)
        self._start_time = time.time()

    def process(self, frame_rgb):
        """frame_rgb: HxWx3 uint8 numpy array in RGB order."""
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        timestamp_ms = int((time.time() - self._start_time) * 1000)
        return self.landmarker.detect_for_video(mp_image, timestamp_ms)

    def draw_landmarks(self, frame_bgr, landmarks):
        """landmarks: list of NormalizedLandmark for one hand."""
        h, w, _ = frame_bgr.shape
        pts = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
        for a, b in HAND_CONNECTIONS:
            cv2_line_color = (255, 255, 255)
            import cv2
            cv2.line(frame_bgr, pts[a], pts[b], cv2_line_color, 2)
        import cv2
        for x, y in pts:
            cv2.circle(frame_bgr, (x, y), 4, (0, 255, 0), -1)

    @staticmethod
    def _finger_is_up(landmarks, tip_idx, pip_idx):
        return landmarks[tip_idx].y < landmarks[pip_idx].y

    @staticmethod
    def _thumb_is_up(landmarks, handedness_label):
        tip = landmarks[THUMB_TIP]
        ip = landmarks[THUMB_IP]
        if handedness_label == "Right":
            return tip.x < ip.x
        return tip.x > ip.x

    @staticmethod
    def _dist(a, b):
        return math.hypot(a.x - b.x, a.y - b.y)

    def classify(self, landmarks, handedness_label="Right"):
        index_up = self._finger_is_up(landmarks, INDEX_TIP, INDEX_PIP)
        middle_up = self._finger_is_up(landmarks, MIDDLE_TIP, MIDDLE_PIP)
        ring_up = self._finger_is_up(landmarks, RING_TIP, RING_PIP)
        pinky_up = self._finger_is_up(landmarks, PINKY_TIP, PINKY_PIP)
        thumb_up = self._thumb_is_up(landmarks, handedness_label)

        count_up = sum([thumb_up, index_up, middle_up, ring_up, pinky_up])

        thumb_index_dist = self._dist(landmarks[THUMB_TIP], landmarks[INDEX_TIP])
        if thumb_index_dist < 0.05 and middle_up and ring_up and pinky_up:
            return "ok_sign"

        if count_up == 0:
            return "fist"
        if count_up == 5:
            return "open_palm"
        if index_up and not middle_up and not ring_up and not pinky_up and not thumb_up:
            return "pointing"
        if index_up and middle_up and not ring_up and not pinky_up:
            return "peace"
        if thumb_up and not index_up and not middle_up and not ring_up and not pinky_up:
            return "thumbs_up"
        if pinky_up and index_up and not middle_up and not ring_up:
            return "rock_on"
        if thumb_up and pinky_up and not index_up and not middle_up and not ring_up:
            return "call_me"

        return "unknown"

    def close(self):
        self.landmarker.close()