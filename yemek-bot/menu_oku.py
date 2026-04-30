#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Yemek Botu - Menü Okuma Scripti
WhatsApp grubundaki son MENÜ: mesajını okur ve menu.json'a kaydeder.

Gruba şu formatta yaz:
  MENÜ:
  Pazartesi: Ezogelin Çorbası, Tavuk Izgara, Ayran
  Salı: Mercimek Çorbası, Köfte, Cacık
  Çarşamba: Domates Çorbası, Makarna, Ayran
  Perşembe: Yayla Çorbası, Etli Güveç, Ayran
  Cuma: Tarhana Çorbası, Pilav, Ayran
"""

import json
import os
import sys
import requests
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# ─── Konfigürasyon ─────────────────────────────────────────────────────────
API_URL      = os.environ.get("GREEN_API_URL",       "https://7103.api.greenapi.com")
INSTANCE_ID  = os.environ.get("GREEN_API_INSTANCE",  "")
API_TOKEN    = os.environ.get("GREEN_API_TOKEN",      "")
BOT_GROUP_ID = os.environ.get("YEMEK_BOT_GROUP_ID",  "")  # Menü yazılan özel grup

MENU_DOSYASI = "menu.json"

GUN_MAP = {
    "pazartesi": "Pazartesi",
    "sali":      "Sali",
    "salı":      "Sali",
    "carsamba":  "Carsamba",
    "çarşamba":  "Carsamba",
    "persembe":  "Persembe",
    "perşembe":  "Persembe",
    "cuma":      "Cuma",
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
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{seviye}] {mesaj}")

def _gapi(endpoint):
    return f"{API_URL}/waInstance{INSTANCE_ID}/{endpoint}/{API_TOKEN}"

def mesajlari_getir(chat_id, limit=20):
    try:
        r = requests.post(
            _gapi("getChatHistory"),
            json={"chatId": chat_id, "count": limit},
            timeout=30
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        log(f"Mesajlar alınamadı: {e}", "ERROR")
        return []

def menu_parse(metin):
    satirlar = metin.strip().splitlines()
    menu = {k: [] for k in GUN_MAP.values() if k not in menu_parse.__dict__}
    menu = {"Pazartesi": [], "Sali": [], "Carsamba": [], "Persembe": [], "Cuma": []}

    mevcut_gun = None
    menu_basladi = False

    for satir in satirlar:
        satir = satir.strip()
        if not satir:
            continue

        if satir.upper().startswith("MENÜ:") or satir.upper().startswith("MENU:"):
            menu_basladi = True
            continue

        if not menu_basladi:
            continue

        if ":" in satir:
            gun_kismi, yemek_kismi = satir.split(":", 1)
            gun_key = gun_kismi.strip().lower()
            # Türkçe karakterleri normalize et
            gun_key = gun_key.replace("ş", "s").replace("ı", "i").replace("ç", "c")

            if gun_key in GUN_MAP:
                mevcut_gun = GUN_MAP[gun_key]
                yemekler = [y.strip() for y in yemek_kismi.split(",") if y.strip()]
                menu[mevcut_gun] = yemekler
        elif mevcut_gun:
            yemekler = [y.strip() for y in satir.split(",") if y.strip()]
            menu[mevcut_gun].extend(yemekler)

    if any(menu[g] for g in menu):
        return menu
    return None

def menu_kaydet(menu, hafta_adi=""):
    data = {
        "hafta": hafta_adi,
        "son_guncelleme": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "menu": menu
    }
    with open(MENU_DOSYASI, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    log(f"Menü kaydedildi!")

def menu_yazdir(menu):
    print()
    print("=" * 50)
    print("  HAFTALIK MENÜ")
    print("=" * 50)
    for gun_key, gun_tr in GUN_TR.items():
        yemekler = menu.get(gun_key, [])
        print(f"  {gun_tr}: {', '.join(yemekler) if yemekler else '-'}")
    print("=" * 50)
    print()

# ─── Ana Program ───────────────────────────────────────────────────────────

def ana_program():
    log("Yemek Botu - Menü Okuma Başlatıldı")

    if not all([INSTANCE_ID, API_TOKEN, BOT_GROUP_ID]):
        log("Eksik: GREEN_API_INSTANCE, GREEN_API_TOKEN, YEMEK_BOT_GROUP_ID", "ERROR")
        sys.exit(1)

    log(f"Grup mesajları okunuyor...")
    mesajlar = mesajlari_getir(BOT_GROUP_ID, limit=30)

    if not mesajlar:
        log("Hiç mesaj bulunamadı!", "WARN")
        sys.exit(1)

    bulunan_menu = None
    for msg in mesajlar:
        metin = msg.get("textMessage", "") or msg.get("extendedTextMessage", {}).get("text", "")
        if not metin:
            continue
        if "MENÜ:" in metin.upper() or "MENU:" in metin.upper():
            log("Menü mesajı bulundu!")
            bulunan_menu = menu_parse(metin)
            if bulunan_menu:
                break

    if not bulunan_menu:
        log("Geçerli menü mesajı bulunamadı! Gruba 'MENÜ:' ile başlayan mesaj yaz.", "ERROR")
        sys.exit(1)

    menu_yazdir(bulunan_menu)
    menu_kaydet(bulunan_menu)
    log("Menü başarıyla kaydedildi!")

if __name__ == "__main__":
    ana_program()
