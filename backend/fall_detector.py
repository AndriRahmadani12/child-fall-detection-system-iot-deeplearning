import cv2
import mediapipe as mp
import numpy as np
import os
import asyncio
from datetime import datetime
from telegram_utils import SendTelegramMessage

class FallDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )

        # Parameter pola jatuh tubuh
        self.vertical_velocity_threshold = 0.04  # Ambang kecepatan vertikal
        self.horizontal_ratio_threshold = 1.2    # Ambang rasio perubahan posisi horizontal
        self.vertical_acceleration_threshold = 0.01  # Ambang percepatan vertikal
        
        # Parameter validasi temporal
        self.fall_frames_threshold = 3     # Jumlah frame berurutan untuk konfirmasi jatuh
        self.fall_frames_counter = 0
        self.recovery_frames_threshold = 10  # Frame untuk menunggu sebelum mendeteksi jatuh lain
        self.recovery_counter = 0
        
        # Pelacakan posisi dan kecepatan
        self.previous_positions = {
            'shoulder': None,
            'hip': None,
            'knee': None
        }
        self.previous_velocities = {
            'shoulder': [0, 0],
            'hip': [0, 0],
            'knee': [0, 0]
        }
        
        # Direktori output
        self.output_dir = "fall_detected_images"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        self.previous_fall_status = False
        self.telegram_utils = SendTelegramMessage()
        
        # Buffer frame untuk verifikasi jatuh yang lebih baik
        self.frame_buffer = []
        self.buffer_size = 15
        
        # Referensi postur tubuh normal
        self.normal_posture_ratio = 0.4  # Rasio tinggi/lebar dalam postur normal

    def calculate_velocities(self, current_positions):
        """Hitung kecepatan dan percepatan gerakan tubuh"""
        velocities = {}
        accelerations = {}
        
        for key, current_pos in current_positions.items():
            if self.previous_positions[key] is not None:
                # Hitung komponen kecepatan horizontal dan vertikal
                dx = current_pos[0] - self.previous_positions[key][0]
                dy = current_pos[1] - self.previous_positions[key][1]
                
                velocities[key] = [dx, dy]
                
                # Hitung percepatan (perubahan kecepatan)
                prev_vel = self.previous_velocities[key]
                ax = dx - prev_vel[0]
                ay = dy - prev_vel[1]
                accelerations[key] = [ax, ay]
                
                # Simpan kecepatan saat ini untuk perhitungan percepatan berikutnya
                self.previous_velocities[key] = velocities[key]
            else:
                velocities[key] = [0, 0]
                accelerations[key] = [0, 0]
            
            # Simpan posisi saat ini untuk perhitungan berikutnya
            self.previous_positions[key] = current_pos
            
        return velocities, accelerations
    
    def calculate_body_proportions(self, landmarks, frame):
        """Hitung proporsi tubuh untuk analisis pola jatuh"""
        # Tinggi dan lebar boundingbox tubuh
        x_values = []
        y_values = []
        
        # Kumpulkan landmark untuk menghitung boundingbox
        keypoints = [
            self.mp_pose.PoseLandmark.NOSE,
            self.mp_pose.PoseLandmark.LEFT_SHOULDER,
            self.mp_pose.PoseLandmark.RIGHT_SHOULDER,
            self.mp_pose.PoseLandmark.LEFT_HIP,
            self.mp_pose.PoseLandmark.RIGHT_HIP,
            self.mp_pose.PoseLandmark.LEFT_KNEE,
            self.mp_pose.PoseLandmark.RIGHT_KNEE,
            self.mp_pose.PoseLandmark.LEFT_ANKLE,
            self.mp_pose.PoseLandmark.RIGHT_ANKLE
        ]
        
        for point in keypoints:
            x = landmarks[point.value].x * frame.shape[1]
            y = landmarks[point.value].y * frame.shape[0]-            x_values.append(x)
            y_values.append(y)
        
        # Hitung boundingbox
        min_x, max_x = min(x_values), max(x_values)
        min_y, max_y = min(y_values), max(y_values)
        
        body_width = max_x - min_x
        body_height = max_y - min_y
        
        # Rasio tinggi/lebar - dalam postur normal, tinggi > lebar
        # Saat jatuh, rasio ini biasanya berubah drastis (tubuh lebih "horizontal")
        if body_width > 0:
            height_width_ratio = body_height / body_width
        else:
            height_width_ratio = 1
            
        return height_width_ratio, (min_x, min_y, max_x, max_y)

    async def save_fall_image(self, current_frame):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = f"fall_detected_{timestamp.replace(':', '-')}.jpg"
        filepath = os.path.join(self.output_dir, filename)
        
        # Buat gambar multi-frame untuk menunjukkan urutan--------- jatuh
        if len(self.frame_buffer) > 0:
            # Ambil frame dari buffer untuk menunjukkan urutan jatuh
            frames_to_show = self.frame_buffer[-5:] + [current_frame]
            height, width = frames_to_show[0].shape[:2]
            
            # Buat grid gambar (2x3)
            grid_img = np.zeros((height*2, width*3, 3), dtype=np.uint8)
            
            for i, img in enumerate(frames_to_show):
                row = i // 3
                col = i % 3
                grid_img[row*height:(row+1)*height, col*width:(col+1)*width] = img
                
                # Tambahkan nomor frame
                cv2.putText(grid_img, f"Frame {i+1}", 
                           (col*width + 10, row*height + 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Tambahkan teks deteksi jatuh
            cv2.putText(grid_img, "FALL DETECTED!", (width, height*2-40),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
            
            cv2.imwrite(filepath, grid_img)
        else:
            # Simpan frame saat ini jika buffer kosong
            cv2.imwrite(filepath, current_frame)

        # Kirim notifikasi dan gambar ke Telegram secara async
        asyncio.create_task(self.telegram_utils.send_telegram_message(f"⚠️ ALERT! Fall Detected at {timestamp}!"))
        asyncio.create_task(self.telegram_utils.send_telegram_photo(filepath, f"Fall Detected at {timestamp}"))

        print(f"Saved and sent fall detection image: {filepath}")

    def detect_falls(self, url):
        print("Detecting falls in video...")
        cap = cv2.VideoCapture(url)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            # Simpan frame asli untuk ditampilkan
            original_frame = frame.copy()
            
            # Tambahkan frame ke buffer
            if len(self.frame_buffer) >= self.buffer_size:
                self.frame_buffer.pop(0)
            self.frame_buffer.append(original_frame.copy())

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb_frame)

            # Nilai default jika pose tidak terdeteksi
            is_falling = False
            height_width_ratio = 1
            vertical_velocity = 0
            vertical_acceleration = 0
            
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark

                self.mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS
                )

                # Ekstrak landmark kunci
                left_shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * frame.shape[1],
                              landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * frame.shape[0]]
                right_shoulder = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x * frame.shape[1],
                               landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y * frame.shape[0]]
                left_hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x * frame.shape[1],
                         landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y * frame.shape[0]]
                right_hip = [landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x * frame.shape[1],
                          landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y * frame.shape[0]]
                left_knee = [landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x * frame.shape[1],
                          landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y * frame.shape[0]]
                right_knee = [landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].x * frame.shape[1],
                           landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].y * frame.shape[0]]
                
                # Hitung titik tengah
                shoulder_mid = [(left_shoulder[0] + right_shoulder[0])/2, (left_shoulder[1] + right_shoulder[1])/2]
                hip_mid = [(left_hip[0] + right_hip[0])/2, (left_hip[1] + right_hip[1])/2]
                knee_mid = [(left_knee[0] + right_knee[0])/2, (left_knee[1] + right_knee[1])/2]
                
                # Hitung proporsi tubuh
                height_width_ratio, bbox = self.calculate_body_proportions(landmarks, frame)
                
                # Analisis kecepatan gerakan
                current_positions = {
                    'shoulder': shoulder_mid,
                    'hip': hip_mid,
                    'knee': knee_mid
                }
                
                velocities, accelerations = self.calculate_velocities(current_positions)
                
                # Dapatkan kecepatan dan percepatan vertikal bagian tubuh tengah (hip)
                vertical_velocity = velocities['hip'][1]
                vertical_acceleration = accelerations['hip'][1]
                
                # Deteksi jatuh berdasarkan pola tubuh
                # 1. Perubahan rasio tinggi/lebar - ketika jatuh, tubuh menjadi lebih "lebar" daripada "tinggi"
                criteria_1 = height_width_ratio < self.normal_posture_ratio
                
                # 2. Kecepatan jatuh vertikal - ketika jatuh, ada kecepatan vertikal signifikan
                criteria_2 = vertical_velocity > self.vertical_velocity_threshold
                
                # 3. Percepatan vertikal - ketika jatuh, ada percepatan vertikal signifikan
                criteria_3 = vertical_acceleration > self.vertical_acceleration_threshold
                
                # 4. Posisi tubuh rendah
                criteria_4 = hip_mid[1] > frame.shape[0] * 0.6
                
                # Hitung pola jatuh (minimal 3 kriteria terpenuhi)
                criteria_count = sum([criteria_1, criteria_2, criteria_3, criteria_4])
                potential_fall = criteria_count >= 3
                
                # Validasi temporal (harus mendeteksi jatuh untuk beberapa frame berurutan)
                if potential_fall:
                    self.fall_frames_counter += 1
                else:
                    self.fall_frames_counter = max(0, self.fall_frames_counter - 1)  # Kurangi counter perlahan
                
                # Hanya dipicu jika kita telah melihat jatuh untuk cukup frame berurutan
                is_falling = (self.fall_frames_counter >= self.fall_frames_threshold)
                
                # Reset counter setelah periode pemulihan
                if self.previous_fall_status and not is_falling:
                    self.recovery_counter += 1
                    if self.recovery_counter >= self.recovery_frames_threshold:
                        self.previous_fall_status = False
                        self.recovery_counter = 0
                
                # Hanya picu peringatan baru jika kita belum dalam keadaan jatuh
                if is_falling and not self.previous_fall_status:
                    asyncio.run(self.save_fall_image(frame))
                    self.previous_fall_status = True
                    self.recovery_counter = 0
                
                # Visualisasi bounding box tubuh
                if is_falling:
                    cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (0, 0, 255), 2)
                else:
                    cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (0, 255, 0), 2)

            # Visualisasi
            status = "FALL DETECTED!" if is_falling else "Normal"
            color = (0, 0, 255) if is_falling else (0, 255, 0)
            
            cv2.putText(frame, f"Status: {status}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            cv2.putText(frame, f"H/W Ratio: {height_width_ratio:.2f}", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(frame, f"Vert Velocity: {vertical_velocity:.3f}", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(frame, f"Vert Accel: {vertical_acceleration:.3f}", (10, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(frame, f"Fall Counter: {self.fall_frames_counter}/{self.fall_frames_threshold}", (10, 150),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            cv2.imshow('Fall Detection', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()