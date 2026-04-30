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

def gun_normalize(metin):
    """Metinden gün adını normalize eder"""
    metin = metin.strip().lower()
    metin = metin.replace("ş", "s").replace("ı", "i").replace("ç", "c").replace("ğ", "g").replace("ü", "u").replace("ö", "o")
    for gun_key, gun_val in GUN_MAP.items():
        if gun_key in metin:
            return gun_val
    return None

def menu_parse(metin):
    """
    İki formatı destekler:

    Format 1 (klasik):
      MENÜ:
      Pazartesi: Ezogelin Çorbası, Tavuk, Ayran
      Salı: Mercimek, Köfte

    Format 2 (tarihli, alt satır):
      MENÜ:
      4 Mayıs Pazartesi
      Mercimek Çorbası
      Izgara Tavuk
      5 Mayıs Salı
      Ezogelin Çorbası
      Et Sote
    """
    satirlar = metin.strip().splitlines()
    menu = {"Pazartesi": [], "Sali": [], "Carsamba": [], "Persembe": [], "Cuma": []}

    mevcut_gun = None
    menu_basladi = False

    for satir in satirlar:
        satir = satir.strip()
        if not satir:
            continue

        # MENÜ: başlığını yakala
        if satir.upper().startswith("MENÜ:") or satir.upper().startswith("MENU:"):
            menu_basladi = True
            # Aynı satırda yemek varsa (MENÜ: Pazartesi: ...) devam et
            satir = satir.split(":", 1)[1].strip() if ":" in satir else ""
            if not satir:
                continue

        if not menu_basladi:
            continue

        # Format 1: "Pazartesi: yemek1, yemek2"
        if ":" in satir:
            gun_kismi, yemek_kismi = satir.split(":", 1)
            gun = gun_normalize(gun_kismi)
            if gun:
                mevcut_gun = gun
                yemekler = [y.strip() for y in yemek_kismi.split(",") if y.strip()]
                if yemekler:
                    menu[mevcut_gun] = yemekler
                continue

        # Format 2: Satırda gün adı var mı? (örn: "4 Mayıs Pazartesi")
        gun = gun_normalize(satir)
        if gun:
            mevcut_gun = gun
            continue

        # Yemek satırı - mevcut güne ekle
        if mevcut_gun and satir:
            # Virgülle ayrılmış birden fazla yemek olabilir
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
