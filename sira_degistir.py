# -*- coding: utf-8 -*-
import json

ISIM_DOSYASI = "kola_sirasi.txt"
INDEX_DOSYASI = "index.json"

print("=" * 50)
print("  KOLA SIRASI DEGISTIRME ARACI")
print("=" * 50)
print()

# Isim listesini oku
with open(ISIM_DOSYASI, 'r', encoding='utf-8') as f:
    isimler = [line.strip() for line in f if line.strip()]

# Mevcut index'i oku
with open(INDEX_DOSYASI, 'r', encoding='utf-8') as f:
    index_data = json.load(f)
    current_index = index_data["current_index"]

# Mevcut durumu goster
print("Mevcut sira:", isimler[current_index], "(Index:", current_index, ")")
print()
print("Isim Listesi:")
print("-" * 50)

for i in range(len(isimler)):
    if i == current_index:
        print(" ", i, ".", isimler[i], "<-- MEVCUT")
    else:
        print(" ", i, ".", isimler[i])

print("-" * 50)
print()

# Yeni index al
try:
    yeni_index = int(input("Yeni sira numarasini girin (0-" + str(len(isimler)-1) + "): "))
    
    if 0 <= yeni_index < len(isimler):
        # Index'i guncelle
        data = {
            "current_index": yeni_index,
            "last_sent_date": None
        }
        with open(INDEX_DOSYASI, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print()
        print("Basarili! Sira", isimler[yeni_index], "olarak guncellendi.")
        sonraki = (yeni_index + 1) % len(isimler)
        print("Sonraki sira:", isimler[sonraki])
    else:
        print("Hatali numara!")

except:
    print("Hata olustu!")

print()
input("Devam etmek icin Enter'a basin...")
