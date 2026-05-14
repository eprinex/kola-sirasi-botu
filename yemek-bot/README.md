# 🍴 Yemek Botu

Her sabah 10:00'da günün yemeğini WhatsApp grubuna otomatik gönderir.

## 🚀 Nasıl Çalışır?

```
Sen → Özel gruba "MENÜ:" mesajı yazarsın
         ↓ Pazartesi 10:30'da otomatik
    Bot menüyü okur, menu.json'a kaydeder
         ↓
    Her sabah 10:00'da (Pzt-Cuma)
         ↓
    Bugünün yemeğini ana gruba atar
```

## 📝 Menü Formatı

Özel gruba şu formatta yaz:

```
MENÜ:
Pazartesi: Ezogelin Çorbası, Tavuk Izgara, Ayran
Salı: Mercimek Çorbası, Köfte, Cacık
Çarşamba: Domates Çorbası, Makarna, Ayran
Perşembe: Yayla Çorbası, Etli Güveç, Ayran
Cuma: Tarhana Çorbası, Pilav, Ayran
```

## ⚙️ GitHub Secrets

| Secret | Açıklama |
|--------|----------|
| `GREEN_API_INSTANCE` | Green API Instance ID |
| `GREEN_API_TOKEN` | Green API Token |
| `YEMEK_BOT_GROUP_ID` | Menü yazılan özel grup ID |
| `YEMEK_GROUP_ID` | Mesajın atılacağı ana grup ID |

## 📅 Zamanlama

- **Pazartesi 10:30** → Menü okunur ve kaydedilir
- **Her gün 10:00** (Pzt-Cuma) → Günün yemeği atılır

## 📱 Örnek Mesaj

```
🍴 GÜNÜN YEMEĞİ 🍴

📅 Pazartesi, 04.05.2026

Bugünkü menü:
   🍽 Ezogelin Çorbası
   🍽 Tavuk Izgara
   🍽 Ayran

Afiyet olsun! 😋

---
Bu mesaj otomatik yemek hatırlatma sistemi tarafından gönderilmiştir.
```

## 🧪 Manuel Test

```bash
# Menü oku
python menu_oku.py

# Günlük mesaj gönder
python yemek_bot.py
```

## 🔧 Kurulum

1. GitHub'da yeni repo oluştur: `yemek-botu`
2. Bu dosyaları yükle
3. Secrets ekle (4 adet)
4. Özel grup oluştur, menüyü oraya yaz
5. Bitti! 🎉
