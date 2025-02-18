import cv2
import mediapipe as mp
import numpy as np
import os
import requests
from datetime import datetime
from telegram_utils import SendTelegramMessage

class FallDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Parameter deteksi jatuh
        self.fall_threshold_angle = 60
        self.hip_height_threshold = 0.3
        

        # Output directory
        self.output_dir = "fall_detected_images"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        self.previous_fall_status = False
        self.telegram_utils = SendTelegramMessage()

        
    def calculate_angle(self, a, b, c):
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        ba = a - b
        bc = c - b
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
        return np.degrees(angle)
    
    def save_fall_image(self, frame):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = f"fall_detected_{timestamp.replace(':', '-')}.jpg"
        filepath = os.path.join(self.output_dir, filename)
        cv2.imwrite(filepath, frame)
        
        # Kirim notifikasi dan gambar ke Telegram
        self.telegram_utils.send_telegram_message(f"⚠️ ALERT! Fall Detected at {timestamp}!")
        self.telegram_utils.send_telegram_photo(filepath, f"Fall Detected at {timestamp}")
        
        print(f"Saved and sent fall detection image: {filepath}")

    def detect_falls(self, video_path):
        print("Detecting    falls in video...")
        cap = cv2.VideoCapture(video_path)
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb_frame)

            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark

                self.mp_drawing.draw_landmarks(
                    frame, 
                    results.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS
                )

                shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * frame.shape[1],
                            landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * frame.shape[0]]
                hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x * frame.shape[1],
                        landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y * frame.shape[0]]
                knee = [landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x * frame.shape[1],
                        landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y * frame.shape[0]]

                body_angle = self.calculate_angle(shoulder, hip, knee)
                hip_height_ratio = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y

                is_falling = (body_angle < self.fall_threshold_angle and 
                            hip_height_ratio > self.hip_height_threshold)

                if is_falling and not self.previous_fall_status:
                    self.save_fall_image(frame)
                
                self.previous_fall_status = is_falling

                status = "FALL DETECTED!" if is_falling else "Normal"
                color = (0, 0, 255) if is_falling else (0, 255, 0)
                
                cv2.putText(frame, f"Status: {status}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                cv2.putText(frame, f"Body Angle: {body_angle:.1f}", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            cv2.imshow('Fall Detection', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()


