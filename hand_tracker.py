import cv2
import mediapipe as mp
import math


class HandTracker:
    def __init__(self, max_hands=1, detection_conf=0.7, tracking_conf=0.7):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_conf,
            min_tracking_confidence=tracking_conf,
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.results = None

        # Landmark indices we care about
        self.TIP_IDS = {
            "thumb": 4,
            "index": 8,
            "middle": 12,
            "ring": 16,
            "pinky": 20,
        }

    def find_hands(self, frame, draw=True):
        """Process a BGR frame and optionally draw landmarks on it."""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(rgb)

        if self.results.multi_hand_landmarks and draw:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                )
        return frame

    def get_landmark_positions(self, frame, hand_index=0):
        """Return list of (id, x_px, y_px) for the requested hand, or [] if not found."""
        landmark_list = []
        if self.results and self.results.multi_hand_landmarks:
            if hand_index >= len(self.results.multi_hand_landmarks):
                return landmark_list
            hand = self.results.multi_hand_landmarks[hand_index]
            h, w, _ = frame.shape
            for idx, lm in enumerate(hand.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                landmark_list.append((idx, cx, cy))
        return landmark_list

    def get_fingertip(self, landmark_list, finger="index"):
        """Return (x, y) of a given fingertip from a landmark_list, or None."""
        tip_id = self.TIP_IDS.get(finger)
        for idx, x, y in landmark_list:
            if idx == tip_id:
                return (x, y)
        return None

    @staticmethod
    def distance(p1, p2):
        if p1 is None or p2 is None:
            return float("inf")
        return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

    def close(self):
        self.hands.close()