import aiohttp
import dotenv
class SendTelegramMessage:
    TOKEN = "dotenv"
    CHAT_ID = "-4797772163"

    @classmethod
    async def send_telegram_message(cls, message):
        """Mengirim pesan teks ke Telegram secara asinkron."""
        url = f"https://api.telegram.org/bot{cls.TOKEN}/sendMessage"
        payload = {
            "chat_id": cls.CHAT_ID,
            "text": message
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    return await response.json()
        except Exception as e:
            print(f"Error sending message: {e}")
            return None

    @classmethod
    async def send_telegram_photo(cls, photo_path, caption=""):
        """Mengirim foto ke Telegram secara asinkron."""
        url = f"https://api.telegram.org/bot{cls.TOKEN}/sendPhoto"
        try:
            async with aiohttp.ClientSession() as session:
                with open(photo_path, 'rb') as photo:
                    files = {'photo': photo}
                    data = {'chat_id': cls.CHAT_ID, 'caption': caption}
                    async with session.post(url, data=data, files=files) as response:
                        return await response.json()
        except Exception as e:
            print(f"Error sending photo: {e}")
            return None
