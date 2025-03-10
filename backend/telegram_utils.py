import requests


class SendTelegramMessage:
    TOKEN = "7562691866:AAFkjfYVR-tynL6ER9nUWyKVftcGLcH8ls8"
    CHAT_ID = "1249772453"

    @classmethod
    def send_telegram_message(cls, message):
        """Mengirim pesan teks ke Telegram"""
        url = f"https://api.telegram.org/bot{cls.TOKEN}/sendMessage"
        payload = {"chat_id": cls.CHAT_ID, "text": message}
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            print("✅ Telegram Response:", response.json())
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error sending message: {e}")
            return None

    @classmethod
    def send_telegram_photo(cls, photo_path, caption=""):
        """Mengirim foto ke Telegram dengan caption"""
        url = f"https://api.telegram.org/bot{cls.TOKEN}/sendPhoto"
        try:
            with open(photo_path, "rb") as photo:
                files = {"photo": photo}
                data = {"chat_id": cls.CHAT_ID, "caption": caption}
                response = requests.post(url, data=data, files=files)
                response.raise_for_status()
                print("✅ Foto berhasil dikirim ke Telegram!")
                return response.json()
        except (requests.exceptions.RequestException, FileNotFoundError) as e:
            print(f"❌ Error sending photo: {e}")
            return None
