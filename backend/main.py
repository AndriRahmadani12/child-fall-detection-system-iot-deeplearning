from fastapi import FastAPI, UploadFile, File
import cv2
import mediapipe as mp
import numpy as np
import os
from datetime import datetime
from telegram_utils import SendTelegramMessage

app = FastAPI()


class FallDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils  # Tambahkan drawing utils
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.fall_threshold_angle = 60
        self.hip_height_threshold = 0.3
        self.previous_fall_status = False

    def calculate_angle(self, a, b, c):
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        ba = a - b
        bc = c - b
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
        return np.degrees(angle)

    def detect_falls(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            # Gambar landmark pada frame
            self.mp_drawing.draw_landmarks(
                frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS
            )

            shoulder = [
                landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x
                * frame.shape[1],
                landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y
                * frame.shape[0],
            ]
            hip = [
                landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x * frame.shape[1],
                landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y * frame.shape[0],
            ]
            knee = [
                landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x * frame.shape[1],
                landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y * frame.shape[0],
            ]

            body_angle = self.calculate_angle(shoulder, hip, knee)
            hip_height_ratio = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y
            is_falling = (
                body_angle < self.fall_threshold_angle
                and hip_height_ratio > self.hip_height_threshold
            )
            return is_falling, frame
        return False, frame


fall_detector = FallDetector()


@app.post("/detect_fall")
def detect_fall_from_video(file: UploadFile = File(...)):
    video_path = f"temp_{file.filename}"
    with open(video_path, "wb") as buffer:
        buffer.write(file.file.read())

    cap = cv2.VideoCapture(video_path)
    fall_detected = False
    frame_fall = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        is_falling, processed_frame = fall_detector.detect_falls(frame)
        if is_falling:
            fall_detected = True
            frame_fall = processed_frame  # Simpan frame dengan landmark
            break
    cap.release()
    os.remove(video_path)

    if fall_detected and frame_fall is not None:
        # ✅ Simpan frame dengan landmark sebagai gambar
        image_path = "fall_detected.jpg"
        cv2.imwrite(image_path, frame_fall)

        # ✅ Kirim notifikasi + gambar ke Telegram
        SendTelegramMessage.send_telegram_message(
            "⚠️ ALERT! Kejadian jatuh terdeteksi dari video!"
        )
        SendTelegramMessage.send_telegram_photo(
            image_path, "📷 Bukti kejadian jatuh dengan landmark!"
        )

    return {"fall_detected": fall_detected}


@app.get("/detect_fall_live")
def detect_fall_live():
    cap = cv2.VideoCapture(0)
    frame_fall = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        is_falling, processed_frame = fall_detector.detect_falls(frame)
        if is_falling:
            frame_fall = processed_frame  # Simpan frame dengan landmark
            cap.release()

            # ✅ Simpan frame dengan landmark sebagai gambar
            image_path = "fall_detected_live.jpg"
            cv2.imwrite(image_path, frame_fall)

            # ✅ Kirim notifikasi + gambar ke Telegram
            SendTelegramMessage.send_telegram_message(
                "⚠️ ALERT! Kejadian jatuh terdeteksi secara real-time!"
            )
            SendTelegramMessage.send_telegram_photo(
                image_path, "📷 Bukti kejadian jatuh dengan landmark!"
            )

            return {"fall_detected": True}

    cap.release()
    return {"fall_detected": False}
