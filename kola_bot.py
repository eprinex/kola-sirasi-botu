#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kola Sırası Hatırlatma Botu - Green API Versiyonu
PC gerektirmez, GitHub Actions üzerinden çalışır.
"""

import json
import os
import sys
import requests
from datetime import datetime, date

# Windows için UTF-8 desteği (yerel test)
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# ─── Konfigürasyon ─────────────────────────────────────────────────────────
# GitHub Secrets'tan okunur. Yerel test için: ortam değişkeni set edin.

API_URL        = os.environ.get("GREEN_API_URL",       "https://7103.api.greenapi.com")
MEDIA_API_URL  = os.environ.get("GREEN_API_MEDIA_URL", "https://7103.media.greenapi.com")
INSTANCE_ID    = os.environ.get("GREEN_API_INSTANCE",  "")
API_TOKEN      = os.environ.get("GREEN_API_TOKEN",     "")
GROUP_CHAT_ID  = os.environ.get("WHATSAPP_GROUP_ID",   "120363161853351367@g.us")
GITHUB_RAW_URL = os.environ.get("GITHUB_RAW_URL",      "")   # Resim için ham GitHub URL'i

IS_REMINDER    = os.environ.get("KOLA_REMINDER", "false").lower() == "true"

ISIM_DOSYASI   = "kola_sirasi.txt"
INDEX_DOSYASI  = "index.json"
LOG_DOSYASI    = "bot_log.txt"
RESIM_DOSYASI  = "kola_turka.jpg"
MAX_LOG_BOYUT  = 500_000  # 500 KB; aşarsa log temizlenir


# ─── Yardımcılar ───────────────────────────────────────────────────────────

def log_yaz(mesaj: str, seviye: str = "INFO"):
    zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    satir = f"[{zaman}] [{seviye}] {mesaj}"
    print(satir)
    # Log boyut kontrolü
    if os.path.exists(LOG_DOSYASI) and os.path.getsize(LOG_DOSYASI) > MAX_LOG_BOYUT:
        with open(LOG_DOSYASI, 'w', encoding='utf-8') as f:
            f.write(f"[{zaman}] [INFO] Log dosyası boyut sınırı aşıldı, temizlendi.\n")
    with open(LOG_DOSYASI, 'a', encoding='utf-8') as f:
        f.write(satir + "\n")


def isim_listesini_oku():
    if not os.path.exists(ISIM_DOSYASI):
        raise FileNotFoundError(f"{ISIM_DOSYASI} bulunamadı!")
    with open(ISIM_DOSYASI, 'r', encoding='utf-8') as f:
        isimler = [line.strip() for line in f if line.strip()]
    if not isimler:
        raise ValueError("İsim listesi boş!")
    return isimler


def index_oku():
    if not os.path.exists(INDEX_DOSYASI):
        return {"current_index": 0, "last_sent_date": None, "last_sent_person": None}
    with open(INDEX_DOSYASI, 'r', encoding='utf-8') as f:
        return json.load(f)


def index_guncelle(yeni_index: int, tarih: str, kisi: str):
    data = {
        "current_index": yeni_index,
        "last_sent_date": tarih,
        "last_sent_person": kisi,
    }
    with open(INDEX_DOSYASI, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def bugun_gonderildi_mi(index_data: dict) -> bool:
    son_tarih = index_data.get("last_sent_date")
    if not son_tarih:
        return False
    try:
        son_gun = datetime.strptime(son_tarih, "%Y-%m-%d %H:%M:%S").date()
        return son_gun == date.today()
    except (ValueError, TypeError):
        return False


def konfig_kontrol():
    eksikler = [k for k, v in {
        "GREEN_API_INSTANCE": INSTANCE_ID,
        "GREEN_API_TOKEN": API_TOKEN,
        "WHATSAPP_GROUP_ID": GROUP_CHAT_ID,
    }.items() if not v]
    if eksikler:
        log_yaz(f"Eksik değişkenler: {', '.join(eksikler)}", "ERROR")
        log_yaz("GitHub Secrets veya ortam değişkenlerini ayarlayın.", "ERROR")
        sys.exit(1)


# ─── Green API ─────────────────────────────────────────────────────────────

def _gapi(endpoint: str) -> str:
    return f"{API_URL}/waInstance{INSTANCE_ID}/{endpoint}/{API_TOKEN}"

def _gapi_media(endpoint: str) -> str:
    return f"{MEDIA_API_URL}/waInstance{INSTANCE_ID}/{endpoint}/{API_TOKEN}"


def metin_gonder(chat_id: str, metin: str) -> bool:
    try:
        r = requests.post(
            _gapi("sendMessage"),
            json={"chatId": chat_id, "message": metin},
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        log_yaz(f"API yanıtı: {data}")
        return "idMessage" in data
    except Exception as e:
        log_yaz(f"Metin gönderilemedi: {e}", "ERROR")
        return False


def resim_gonder_url(chat_id: str, url: str, caption: str = "") -> bool:
    """GitHub'daki resmi URL üzerinden gönderir."""
    try:
        r = requests.post(
            _gapi("sendFileByUrl"),
            json={
                "chatId": chat_id,
                "urlFile": url,
                "fileName": "kola_turka.jpg",
                "caption": caption,
            },
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        log_yaz(f"Resim API yanıtı: {data}")
        return "idMessage" in data
    except Exception as e:
        log_yaz(f"Resim gönderilemedi: {e}", "WARN")
        return False


def gruplari_listele():
    """Tüm WhatsApp gruplarını listeler — WHATSAPP_GROUP_ID bulmak için kullanın."""
    try:
        r = requests.get(_gapi("getChats"), timeout=30)
        r.raise_for_status()
        chats = r.json()
        gruplar = [c for c in chats if c.get("id", "").endswith("@g.us")]
        print("\n📋 WhatsApp Grupları")
        print("─" * 60)
        for g in gruplar:
            print(f"  ID  : {g.get('id')}")
            print(f"  Ad  : {g.get('name', '?')}")
            print()
        if not gruplar:
            print("  Hiç grup bulunamadı.")
    except Exception as e:
        print(f"Hata: {e}")


# ─── Mesaj Şablonları ──────────────────────────────────────────────────────

def ana_mesaj(isim: str) -> str:
    return (
        "⚡ ACİL DUYURU ⚡\n\n"
        "🎯 Hedef: Kola temini\n"
        "📅 Tarih: Yarın (Cuma)\n"
        "⏰ Saat: Namaz sonrası\n"
        f"👤 Görevli: *{isim}*\n\n"
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


def hatirlatma_mesaji(isim: str) -> str:
    return (
        "🔔 HATIRLATMA 🔔\n\n"
        f"👤 *{isim}*, yarınki kola görevini unutma!\n\n"
        "⏰ Yarın (Cuma) namaz sonrası\n"
        "🥤 Soğuk kola, herkese yetecek kadar\n\n"
        "Bu mesaj otomatik hatırlatma servisi tarafından gönderildi. 🤖"
    )


# ─── Ana Program ───────────────────────────────────────────────────────────

def ana_program():
    log_yaz("═" * 55)
    mod = "HATIRLATMA 🔔" if IS_REMINDER else "ANA MESAJ 📣"
    log_yaz(f"🤖 Kola Botu Başlatıldı — {mod}")

    konfig_kontrol()

    isimler = isim_listesini_oku()
    log_yaz(f"📋 {len(isimler)} kişi yüklendi")

    index_data = index_oku()
    current_index = index_data.get("current_index", 0)

    # Sınır kontrolü
    if current_index >= len(isimler):
        current_index = 0

    # ── Akşam Hatırlatma ─────────────────────────────────────────
    if IS_REMINDER:
        if not bugun_gonderildi_mi(index_data):
            log_yaz("Bugün henüz ana mesaj gönderilmemiş, hatırlatma atlanıyor.", "WARN")
            return

        kisi = index_data.get("last_sent_person") or isimler[max(current_index - 1, 0)]
        log_yaz(f"🔔 Hatırlatma → {kisi}")

        if metin_gonder(GROUP_CHAT_ID, hatirlatma_mesaji(kisi)):
            log_yaz("✅ Hatırlatma gönderildi!")
        else:
            log_yaz("❌ Hatırlatma gönderilemedi!", "ERROR")
            sys.exit(1)
        return

    # ── Sabah Ana Mesaj ───────────────────────────────────────────
    siradaki = isimler[current_index]
    log_yaz(f"🎯 Sıradaki kişi: {siradaki}")

    mesaj = ana_mesaj(siradaki)
    basari = False

    # Resim varsa önce resimle dene
    if GITHUB_RAW_URL and os.path.exists(RESIM_DOSYASI):
        resim_url = f"{GITHUB_RAW_URL}/{RESIM_DOSYASI}"
        log_yaz(f"📷 Resimli mesaj deneniyor: {resim_url}")
        basari = resim_gonder_url(GROUP_CHAT_ID, resim_url, caption=mesaj)

    # Resim başarısızsa sadece metin gönder
    if not basari:
        log_yaz("Metin olarak gönderiliyor...")
        basari = metin_gonder(GROUP_CHAT_ID, mesaj)

    if basari:
        yeni_index = (current_index + 1) % len(isimler)
        bugun = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        index_guncelle(yeni_index, bugun, siradaki)
        log_yaz(f"✅ Başarılı! Index {current_index} → {yeni_index}")
        log_yaz(f"📅 Sonraki sıra: {isimler[yeni_index]}")
    else:
        log_yaz("❌ Mesaj gönderilemedi! Index güncellenmedi.", "ERROR")
        sys.exit(1)


# ─── Entry Point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    if "--list-groups" in sys.argv:
        konfig_kontrol()
        gruplari_listele()
    else:
        ana_program()
