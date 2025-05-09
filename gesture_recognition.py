import cv2
import mediapipe as mp
import numpy as np

class HandGesture:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7)
        self.mp_draw = mp.solutions.drawing_utils
        self.gesture_buffer = []
        self.buffer_size = 7

    def detect_gesture(self, frame):
        gesture = "Unknown"
        results = self.hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                landmarks = hand_landmarks.landmark
                finger_states = self.finger_status(landmarks)
                count = sum(finger_states)

                # Gesture classification
                if count == 0:
                    gesture = "Rock"
                elif finger_states == [False, True, True, False, False]:
                    gesture = "Scissors"
                elif count == 5:
                    gesture = "Paper"
                elif finger_states == [True, True, False, False, True]:
                    gesture = "Lizard"
                elif finger_states == [True, False, True, True, True]:
                    gesture = "Spock"

                self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

        # Buffer logic for smoothing
        self.gesture_buffer.append(gesture)
        if len(self.gesture_buffer) > self.buffer_size:
            self.gesture_buffer.pop(0)
        if len(self.gesture_buffer) == self.buffer_size:
            gesture = max(set(self.gesture_buffer), key=self.gesture_buffer.count)

        return frame, gesture

    def finger_status(self, landmarks):
        tips_ids = [4, 8, 12, 16, 20]
        fingers = []

        # Thumb: check if tip is to the right/left of IP joint (depending on hand orientation)
        is_thumb_open = landmarks[4].x < landmarks[3].x if landmarks[4].x < 0.5 else landmarks[4].x > landmarks[3].x
        fingers.append(is_thumb_open)

        # Other fingers: check if tip is above PIP joint
        for i in range(1, 5):
            tip_id = tips_ids[i]
            pip_id = tip_id - 2
            fingers.append(landmarks[tip_id].y < landmarks[pip_id].y)

        return fingers

    def finger_distance(self, landmarks, id1, id2):
        x1, y1 = landmarks[id1].x, landmarks[id1].y
        x2, y2 = landmarks[id2].x, landmarks[id2].y
        return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def calculate_finger_angle(self, landmarks, tip1, tip2, wrist):
        p1 = np.array([landmarks[tip1].x, landmarks[tip1].y])
        p2 = np.array([landmarks[tip2].x, landmarks[tip2].y])
        p3 = np.array([landmarks[wrist].x, landmarks[wrist].y])
        v1 = p1 - p3
        v2 = p2 - p3
        denominator = np.linalg.norm(v1) * np.linalg.norm(v2)
        if denominator == 0:
            return 180
        angle = np.degrees(np.arccos(np.dot(v1, v2) / denominator))
        return angle

    def calculate_palm_angle(self, landmarks):
        wrist = np.array([landmarks[0].x, landmarks[0].y])
        middle_mcp = np.array([landmarks[9].x, landmarks[9].y])
        middle_tip = np.array([landmarks[12].x, landmarks[12].y])
        v1 = middle_mcp - wrist
        v2 = middle_tip - middle_mcp
        denominator = np.linalg.norm(v1) * np.linalg.norm(v2)
        if denominator == 0:
            return 180
        angle = np.degrees(np.arccos(np.dot(v1, v2) / denominator))
        return angle
