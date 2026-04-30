#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Yemek Botu - Günlük Mesaj Scripti
Her sabah 10:00'da bugünün yemeğini gruba atar.
"""

import json
import os
import sys
import requests
from datetime import datetime, date

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# ─── Konfigürasyon ─────────────────────────────────────────────────────────
API_URL     = os.environ.get("GREEN_API_URL",      "https://7103.api.greenapi.com")
INSTANCE_ID = os.environ.get("GREEN_API_INSTANCE", "")
API_TOKEN   = os.environ.get("GREEN_API_TOKEN",    "")
GROUP_ID    = os.environ.get("YEMEK_GROUP_ID",     "")  # Mesajın atılacağı ana grup

MENU_DOSYASI = "menu.json"
LOG_DOSYASI  = "yemek_log.txt"

GUN_KEY_MAP = {
    0: "Pazartesi",
    1: "Sali",
    2: "Carsamba",
    3: "Persembe",
    4: "Cuma",
    5: None,
    6: None,
}

GUN_TR = {
    "Pazartesi": "Pazartesi",
    "Sali":      "Salı",
    "Carsamba":  "Çarşamba",
    "Persembe":  "Perşembe",
    "Cuma":      "Cuma",
}

# ─── Yardımcılar ───────────────────────────────────────────────────────────

def log(mesaj, seviye="INFO"):
    zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    satir = f"[{zaman}] [{seviye}] {mesaj}"
    print(satir)
    with open(LOG_DOSYASI, 'a', encoding='utf-8') as f:
        f.write(satir + "\n")

def _gapi(endpoint):
    return f"{API_URL}/waInstance{INSTANCE_ID}/{endpoint}/{API_TOKEN}"

def metin_gonder(chat_id, metin):
    try:
        r = requests.post(
            _gapi("sendMessage"),
            json={"chatId": chat_id, "message": metin},
            timeout=30
        )
        r.raise_for_status()
        data = r.json()
        log(f"API yanıtı: {data}")
        return "idMessage" in data
    except Exception as e:
        log(f"Mesaj gönderilemedi: {e}", "ERROR")
        return False

def menu_oku():
    if not os.path.exists(MENU_DOSYASI):
        log(f"{MENU_DOSYASI} bulunamadı! Önce menu_oku.py çalıştırın.", "ERROR")
        return None
    with open(MENU_DOSYASI, 'r', encoding='utf-8') as f:
        return json.load(f)

def bugun_mesaji_olustur(gun_key, yemekler, hafta=""):
    gun_tr = GUN_TR.get(gun_key, gun_key)
    tarih = date.today().strftime("%d.%m.%Y")
    yemek_listesi = "\n".join(f"   🍽 {y}" for y in yemekler)
    hafta_satiri = f"📋 {hafta}\n" if hafta else ""

    return (
        f"🍴 GÜNÜN YEMEĞİ 🍴\n\n"
        f"📅 {gun_tr}, {tarih}\n"
        f"{hafta_satiri}\n"
        f"Bugünkü menü:\n"
        f"{yemek_listesi}\n\n"
        f"Afiyet olsun! 😋\n\n"
        f"---\n"
        f"Bu mesaj otomatik yemek hatırlatma sistemi tarafından gönderilmiştir."
    ).strip()

# ─── Ana Program ───────────────────────────────────────────────────────────

def ana_program():
    log("=" * 55)
    log("Yemek Botu Başlatıldı")

    if not all([INSTANCE_ID, API_TOKEN, GROUP_ID]):
        log("Eksik: GREEN_API_INSTANCE, GREEN_API_TOKEN, YEMEK_GROUP_ID", "ERROR")
        sys.exit(1)

    bugun = date.today()
    gun_no = bugun.weekday()
    gun_key = GUN_KEY_MAP.get(gun_no)

    if gun_key is None:
        log(f"Bugün hafta sonu, mesaj gönderilmiyor.", "WARN")
        return

    log(f"Bugün: {GUN_TR.get(gun_key)} ({bugun})")

    menu_data = menu_oku()
    if not menu_data:
        sys.exit(1)

    menu    = menu_data.get("menu", {})
    hafta   = menu_data.get("hafta", "")
    yemekler = menu.get(gun_key, [])

    if not yemekler:
        log(f"{GUN_TR.get(gun_key)} için menü yok! Önce menu_oku.py çalıştırın.", "ERROR")
        sys.exit(1)

    log(f"Bugünün yemekleri: {', '.join(yemekler)}")

    mesaj = bugun_mesaji_olustur(gun_key, yemekler, hafta)

    if metin_gonder(GROUP_ID, mesaj):
        log("Mesaj başarıyla gönderildi!")
    else:
        log("Mesaj gönderilemedi!", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    ana_program()
