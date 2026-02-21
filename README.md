# 🥤 Kola Sırası Hatırlatma Botu

Her Perşembe akşamı otomatik olarak WhatsApp grubuna kola sırası hatırlatıcısı gönderen Python otomasyonu.

## 🚀 Kurulum

```bash
# 1. Kütüphaneleri yükle
pip install -r requirements.txt

# 2. kola_sirasi.txt dosyasına isimleri ekle

# 3. (İsteğe bağlı) Kola Turka resmini ekle: kola_turka.jpg

# 4. Test et
python kola_bot.py
```

## 📝 Kullanım

**Manuel çalıştır:**
- `kola_bot.bat` dosyasını çift tıkla

**Sıra değiştir:**
- `sira_degistir.bat` dosyasını çift tıkla

**Otomatik çalıştırma (her Perşembe 18:00):**
1. `otomatik_gorev_olustur.bat` dosyasına sağ tık
2. **"Yönetici olarak çalıştır"** seç

## 🔒 Korumalar

| Özellik | Açıklama |
|---|---|
| Perşembe kontrolü | Bot yalnızca Perşembe günü çalışır (override seçeneği ile) |
| Mükerrer koruma | Aynı günde iki kez çalışırsa uyarı verir ve durur |
| Log sistemi | Tüm işlemler `bot_log.txt` dosyasına kaydedilir |

## 📷 Resim Gönderme

- Resmin adı `kola_turka.jpg` olarak proje klasöründe olmalı
- Bot otomatik olarak resmi panoya kopyalayıp WhatsApp'ta yapıştırır
- Otomatik gönderilemezse manuel adımlar ekranda gösterilir

## 🎯 Sıra Değiştirme

```bash
python sira_degistir.py
```
veya `sira_degistir.bat` dosyasını çift tıkla

Manuel: `index.json` dosyasındaki `current_index` değerini değiştir.

## 📁 Dosyalar

| Dosya | Açıklama |
|---|---|
| `kola_bot.py` | Ana program |
| `kola_bot.bat` | Manuel çalıştırma |
| `sira_degistir.py` | Sıra değiştirme aracı |
| `sira_degistir.bat` | Sıra değiştirme (çift tıkla) |
| `otomatik_gorev_olustur.bat` | Otomatik görev kurulumu |
| `gorevi_sil.bat` | Görevi silme |
| `kola_sirasi.txt` | İsim listesi |
| `index.json` | Sıra takibi |
| `bot_log.txt` | İşlem kayıtları (otomatik oluşur) |
| `kola_turka.jpg` | Kola Turka resmi (isteğe bağlı) |
