#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kola Sırası Hatırlatma Botu - Green API + Tatil Kontrolü
Resmi tatillerde mesajı otomatik değiştirir, sırayı korur
"""

import json
import os
import sys
import requests
from datetime import datetime, date, timedelta

# Windows için UTF-8 desteği (yerel test)
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# ─── Konfigürasyon ─────────────────────────────────────────────────────────
API_URL        = os.environ.get("GREEN_API_URL",       "https://7103.api.greenapi.com")
MEDIA_API_URL  = os.environ.get("GREEN_API_MEDIA_URL", "https://7103.media.greenapi.com")
INSTANCE_ID    = os.environ.get("GREEN_API_INSTANCE",  "")
API_TOKEN      = os.environ.get("GREEN_API_TOKEN",     "")
GROUP_CHAT_ID  = os.environ.get("WHATSAPP_GROUP_ID",   "")
GITHUB_RAW_URL = os.environ.get("GITHUB_RAW_URL",      "")

ADMIN_NUMBER   = "905337906205@c.us"
IS_REMINDER    = os.environ.get("KOLA_REMINDER", "false").lower() == "true"

ISIM_DOSYASI   = "kola_sirasi.txt"
INDEX_DOSYASI  = "index.json"
LOG_DOSYASI    = "bot_log.txt"
RESIM_DOSYASI  = "kola_turka.jpg"
MAX_LOG_BOYUT  = 500_000

# ─── Türkiye Resmi Tatilleri ───────────────────────────────────────────────

def turkiye_tatilleri(yil: int) -> dict:
    """Türkiye resmi tatillerini döndürür (sabit + dini)"""

    # Sabit milli tatiller
    tatiller = {
        date(yil, 1, 1):   "Yılbaşı",
        date(yil, 4, 23):  "Ulusal Egemenlik ve Çocuk Bayramı",
        date(yil, 5, 1):   "Emek ve Dayanışma Günü",
        date(yil, 5, 19):  "Atatürk'ü Anma, Gençlik ve Spor Bayramı",
        date(yil, 7, 15):  "Demokrasi ve Millî Birlik Günü",
        date(yil, 8, 30):  "Zafer Bayramı",
        date(yil, 10, 29): "Cumhuriyet Bayramı",
    }

    # Dini tatiller (Ramazan ve Kurban Bayramı - her yıl değişir)
    # Ramazan Bayramı: 1 gün arefe + 3 gün bayram = 4 gün
    # Kurban Bayramı: 1 gün arefe + 4 gün bayram = 5 gün
    dini = {
        # ── 2026 ──────────────────────────────────────────────────
        # Ramazan Bayramı 2026: 19-21 Mart
        date(2026, 3, 18): "Ramazan Bayramı Arefesi",
        date(2026, 3, 19): "Ramazan Bayramı 1. Günü",
        date(2026, 3, 20): "Ramazan Bayramı 2. Günü",
        date(2026, 3, 21): "Ramazan Bayramı 3. Günü",
        # Kurban Bayramı 2026: 26-29 Mayıs
        date(2026, 5, 25): "Kurban Bayramı Arefesi",
        date(2026, 5, 26): "Kurban Bayramı 1. Günü",
        date(2026, 5, 27): "Kurban Bayramı 2. Günü",
        date(2026, 5, 28): "Kurban Bayramı 3. Günü",
        date(2026, 5, 29): "Kurban Bayramı 4. Günü",

        # ── 2027 ──────────────────────────────────────────────────
        # Ramazan Bayramı 2027: 8-10 Mart
        date(2027, 3, 7):  "Ramazan Bayramı Arefesi",
        date(2027, 3, 8):  "Ramazan Bayramı 1. Günü",
        date(2027, 3, 9):  "Ramazan Bayramı 2. Günü",
        date(2027, 3, 10): "Ramazan Bayramı 3. Günü",
        # Kurban Bayramı 2027: 15-18 Mayıs
        date(2027, 5, 14): "Kurban Bayramı Arefesi",
        date(2027, 5, 15): "Kurban Bayramı 1. Günü",
        date(2027, 5, 16): "Kurban Bayramı 2. Günü",
        date(2027, 5, 17): "Kurban Bayramı 3. Günü",
        date(2027, 5, 18): "Kurban Bayramı 4. Günü",

        # ── 2028 ──────────────────────────────────────────────────
        # Ramazan Bayramı 2028: 25-27 Şubat
        date(2028, 2, 24): "Ramazan Bayramı Arefesi",
        date(2028, 2, 25): "Ramazan Bayramı 1. Günü",
        date(2028, 2, 26): "Ramazan Bayramı 2. Günü",
        date(2028, 2, 27): "Ramazan Bayramı 3. Günü",
        # Kurban Bayramı 2028: 3-6 Mayıs
        date(2028, 5, 2):  "Kurban Bayramı Arefesi",
        date(2028, 5, 3):  "Kurban Bayramı 1. Günü",
        date(2028, 5, 4):  "Kurban Bayramı 2. Günü",
        date(2028, 5, 5):  "Kurban Bayramı 3. Günü",
        date(2028, 5, 6):  "Kurban Bayramı 4. Günü",
    }

    # Sadece ilgili yılın dini tatillerini ekle
    for gun, ad in dini.items():
        if gun.year == yil:
            tatiller[gun] = ad

    return tatiller

def tatil_mi(kontrol_tarihi: date):
    """Verilen tarihin tatil olup olmadığını kontrol eder."""
    yil = kontrol_tarihi.year
    tatiller = turkiye_tatilleri(yil)
    if kontrol_tarihi in tatiller:
        return True, tatiller[kontrol_tarihi]
    return False, ""

def sonraki_cuma_bul(bugun: date):
    """Yarın tatilse bir sonraki Cuma'yı bulur."""
    yarin = bugun + timedelta(days=1)
    tatil, tatil_adi = tatil_mi(yarin)
    if tatil:
        log_yaz(f"Yarin ({yarin}) tatil: {tatil_adi}")
        sonraki = yarin + timedelta(days=7)
        log_yaz(f"Sonraki Cuma: {sonraki}")
        return sonraki, tatil_adi
    return yarin, ""

# ─── Yardımcılar ───────────────────────────────────────────────────────────

def log_yaz(mesaj: str, seviye: str = "INFO"):
    zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    satir = f"[{zaman}] [{seviye}] {mesaj}"
    print(satir)
    if os.path.exists(LOG_DOSYASI) and os.path.getsize(LOG_DOSYASI) > MAX_LOG_BOYUT:
        with open(LOG_DOSYASI, 'w', encoding='utf-8') as f:
            f.write(f"[{zaman}] [INFO] Log temizlendi.\n")
    with open(LOG_DOSYASI, 'a', encoding='utf-8') as f:
        f.write(satir + "\n")

def isim_listesini_oku():
    if not os.path.exists(ISIM_DOSYASI):
        raise FileNotFoundError(f"{ISIM_DOSYASI} bulunamadi!")
    with open(ISIM_DOSYASI, 'r', encoding='utf-8') as f:
        isimler = [line.strip() for line in f if line.strip()]
    if not isimler:
        raise ValueError("Isim listesi bos!")
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
        log_yaz(f"Eksik degiskenler: {', '.join(eksikler)}", "ERROR")
        log_yaz("GitHub Secrets veya ortam degiskenlerini ayarlayin.", "ERROR")
        sys.exit(1)

# ─── Green API ─────────────────────────────────────────────────────────────

def _gapi(endpoint: str) -> str:
    return f"{API_URL}/waInstance{INSTANCE_ID}/{endpoint}/{API_TOKEN}"

def metin_gonder(chat_id: str, metin: str) -> bool:
    try:
        r = requests.post(
            _gapi("sendMessage"),
            json={"chatId": chat_id, "message": metin},
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        log_yaz(f"API yaniti: {data}")
        return "idMessage" in data
    except Exception as e:
        log_yaz(f"Metin gonderilemedi: {e}", "ERROR")
        return False

def resim_gonder_url(chat_id: str, url: str, caption: str = "") -> bool:
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
        log_yaz(f"Resim API yaniti: {data}")
        return "idMessage" in data
    except Exception as e:
        log_yaz(f"Resim gonderilemedi: {e}", "WARN")
        return False

def gruplari_listele():
    try:
        r = requests.get(_gapi("getChats"), timeout=30)
        r.raise_for_status()
        chats = r.json()
        gruplar = [c for c in chats if c.get("id", "").endswith("@g.us")]
        print("\nWhatsApp Gruplari")
        print("-" * 60)
        for g in gruplar:
            print(f"  ID  : {g.get('id')}")
            print(f"  Ad  : {g.get('name', '?')}")
            print()
        if not gruplar:
            print("  Hic grup bulunamadi.")
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

def tatil_mesaji(isim: str, tatil_adi: str, sonraki_tarih: date) -> str:
    tarih_str = sonraki_tarih.strftime("%d.%m.%Y")
    gunler = ["Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"]
    gun_str = gunler[sonraki_tarih.weekday()]
    return (
        "🎉 RESMİ TATİL DUYURUSU 🎉\n\n"
        f"Yarın *{tatil_adi}* nedeniyle resmi tatil olduğundan "
        f"bu haftaki kola molası iptal edilmiştir.\n\n"
        "📅 Yeni Görev Tarihi:\n"
        f"🗓 {gun_str}, {tarih_str}\n\n"
        f"👤 Görevli: *{isim}* (sıra değişmedi)\n\n"
        "Herkese iyi tatiller! 🌟\n\n"
        "---\n"
        "Bu mesaj otomatik tatil kontrol sistemi tarafından gönderilmiştir."
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
    log_yaz("=" * 55)
    mod = "HATIRLATMA" if IS_REMINDER else "ANA MESAJ"
    log_yaz(f"Kola Botu Baslatildi - {mod}")

    konfig_kontrol()

    isimler = isim_listesini_oku()
    log_yaz(f"{len(isimler)} kisi yuklendi")

    index_data = index_oku()
    current_index = index_data.get("current_index", 0)

    if current_index >= len(isimler):
        current_index = 0

    # ── Akşam Hatırlatma ─────────────────────────────────────────
    if IS_REMINDER:
        if not bugun_gonderildi_mi(index_data):
            log_yaz("Bugun henuz ana mesaj gonderilmemis, hatirlatma atlaniyor.", "WARN")
            return
        kisi = index_data.get("last_sent_person") or isimler[max(current_index - 1, 0)]
        log_yaz(f"Hatirlatma -> {kisi}")
        if metin_gonder(GROUP_CHAT_ID, hatirlatma_mesaji(kisi)):
            log_yaz("Hatirlatma gonderildi!")
        else:
            log_yaz("Hatirlatma gonderilemedi!", "ERROR")
            sys.exit(1)
        return

    # ── Tatil Kontrolü ────────────────────────────────────────────
    bugun = date.today()
    sonraki_cuma, tatil_adi = sonraki_cuma_bul(bugun)
    tatil_var = bool(tatil_adi)

    siradaki = isimler[current_index]
    log_yaz(f"Siradaki kisi: {siradaki}")

    if tatil_var:
        log_yaz(f"Tatil tespit edildi: {tatil_adi} - Tatil mesaji gonderiliyor")
        mesaj = tatil_mesaji(siradaki, tatil_adi, sonraki_cuma)
        # Tatilde index güncellenmez, sıra aynı kişide kalır
        if metin_gonder(GROUP_CHAT_ID, mesaj):
            log_yaz("Tatil mesaji gonderildi! Sira degismedi.")
            bugun_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            index_guncelle(current_index, bugun_str, siradaki)
        else:
            log_yaz("Tatil mesaji gonderilemedi!", "ERROR")
            sys.exit(1)
        return

    # ── Normal Hafta - Ana Mesaj ──────────────────────────────────
    mesaj = ana_mesaj(siradaki)
    basari = False

    if GITHUB_RAW_URL:
        resim_url = f"{GITHUB_RAW_URL}/{RESIM_DOSYASI}"
        log_yaz(f"Resimli mesaj deneniyor...")
        if resim_gonder_url(GROUP_CHAT_ID, resim_url, caption=mesaj):
            basari = True
            log_yaz("Resimli mesaj gonderildi.")
        else:
            log_yaz("Resim basarisiz, metin deneniyor...", "WARN")

    if not basari:
        basari = metin_gonder(GROUP_CHAT_ID, mesaj)

    if basari:
        yeni_index = (current_index + 1) % len(isimler)
        bugun_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        index_guncelle(yeni_index, bugun_str, siradaki)
        log_yaz(f"Basarili! Index {current_index} -> {yeni_index}")
        log_yaz(f"Sonraki sira: {isimler[yeni_index]}")
    else:
        log_yaz("Mesaj gonderilemedi!", "ERROR")
        sys.exit(1)

# ─── Entry Point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    if "--list-groups" in sys.argv:
        konfig_kontrol()
        gruplari_listele()
    else:
        ana_program()
