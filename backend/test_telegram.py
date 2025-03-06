import requests

# Gunakan Token bot yang benar
TOKEN = "7562691866:AAFkjfYVR-tynL6ER9nUWyKVftcGLcH8ls8"

# Gunakan Chat ID yang baru ditemukan dari getUpdates
CHAT_ID = "1249772453"  # Ini adalah Chat ID yang benar

# URL API Telegram untuk mengirim pesan
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

# Pesan yang akan dikirim
message = "🔔 Halo! Ini adalah tes pesan ke bot setelah mendapatkan Chat ID yang benar."

# Kirim permintaan ke API Telegram
payload = {"chat_id": CHAT_ID, "text": message}

try:
    response = requests.post(url, json=payload)
    response.raise_for_status()
    print("✅ Pesan berhasil dikirim!")
    print(response.json())  # Cetak respons API untuk melihat hasilnya
except requests.exceptions.RequestException as e:
    print(f"❌ Error mengirim pesan: {e}")
