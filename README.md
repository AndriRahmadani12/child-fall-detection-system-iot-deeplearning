# Child Fall Detection System using IoT and Deep Learning

![Project Logo](https://via.placeholder.com/150) <!-- Ganti dengan logo proyek Anda jika ada -->

## Deskripsi Proyek

Sistem **Child Fall Detection** ini dirancang untuk mendeteksi kejadian jatuh pada anak secara real-time menggunakan **ESP32-CAM** sebagai perangkat IoT dan **MediaPipe** untuk analisis gerakan. Sistem ini mengirimkan notifikasi langsung ke Telegram jika terdeteksi kejadian jatuh. 

Proyek ini menggabungkan kemampuan ESP32-CAM untuk menangkap gambar, MediaPipe untuk mendeteksi pose manusia, dan FastAPI sebagai backend untuk memproses data serta mengirim notifikasi.

## Fitur Utama

- **Deteksi Jatuh Real-Time**: Menggunakan MediaPipe untuk menganalisis pose manusia dan mendeteksi kejadian jatuh.
- **Notifikasi Telegram**: Mengirim notifikasi ke Telegram secara otomatis jika terdeteksi jatuh.
- **IoT Sederhana**: Menggunakan ESP32-CAM sebagai perangkat IoT untuk menangkap gambar.
- **Backend Cepat**: FastAPI digunakan untuk memproses data dan mengelola notifikasi.

## Teknologi yang Digunakan

- **IoT**: ESP32-CAM untuk menangkap gambar.
- **Computer Vision**: MediaPipe untuk deteksi pose manusia.
- **Backend**: FastAPI untuk server backend dan API.
- **Notifikasi**: Telegram Bot untuk notifikasi real-time.
- **Bahasa Pemrograman**: Python untuk backend dan analisis data.

## Instalasi

### Prasyarat

- Python 3.8 atau lebih baru
- ESP32-CAM dengan firmware yang sesuai
- Library Python: `fastapi`, `uvicorn`, `mediapipe`, `opencv-python`
- Akun Telegram dan Bot Token (dapat dibuat via [BotFather](https://core.telegram.org/bots#botfather))
