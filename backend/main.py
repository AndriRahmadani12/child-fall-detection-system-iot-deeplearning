from fall_detector import FallDetector
import os

if __name__ == "__main__":
    print("Running fall detection...")

    video_path = r"D:\Portfolio\child-fall-detection-system-iot-deeplearning\backend\sample_4.mp4"

    if not os.path.exists(video_path):
        print(f"ERROR: Video file '{video_path}' not found!")
    else:
        print(f"Video file found: {video_path}")
    
    try:
        detector = FallDetector()
        print("Detector initialized. Starting fall detection...")
        
        detector.detect_falls(video_path)
        
        print("Fall detection completed!")
    except Exception as e:
        print(f"An error occurred during fall detection: {e}")
