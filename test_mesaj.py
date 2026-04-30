import requests
import os
import json

INSTANCE_ID = os.environ.get("GREEN_API_INSTANCE", "7103524312")
API_TOKEN   = os.environ.get("GREEN_API_TOKEN",    "cd4385d13baa46188c47145f5e81fe9443390cc5c4d44a57af")
API_URL     = "https://7103.api.greenapi.com"

# Kisisel numara (sadece sana)
HEDEF = "905337906205@c.us"

# Siradaki ismi oku
with open("kola_sirasi.txt", "r", encoding="utf-8") as f:
    isimler = [line.strip() for line in f if line.strip()]

with open("index.json", "r", encoding="utf-8") as f:
    index_data = json.load(f)

current_index = index_data.get("current_index", 0)
siradaki = isimler[current_index]

# Kola botu mesaji
mesaj = (
    "⚡ ACİL DUYURU ⚡\n\n"
    "🎯 Hedef: Kola temini\n"
    "📅 Tarih: Yarın (Cuma)\n"
    "⏰ Saat: Namaz sonrası\n"
    f"👤 Görevli: *{siradaki}*\n\n"
    "Görev tanımlaması:\n"
    "✅ Kola al\n"
    "✅ Soğuk olsun\n"
    "✅ Herkese yetsin\n"
    "✅ Unutma!\n\n"
    "Başarılar asker! 🫡\n\n"
    "---\n"
    "Bu görev mesajı otomatik olarak atanmıştır.\n"
    "Şikayet ve öneriler için: /dev/null"
)

print(f"Siradaki kisi: {siradaki}")
print("Mesaj gonderiliyor...")

url = f"{API_URL}/waInstance{INSTANCE_ID}/sendMessage/{API_TOKEN}"
r = requests.post(url, json={"chatId": HEDEF, "message": mesaj})

print("Durum:", r.status_code)
print("Yanit:", r.json())
