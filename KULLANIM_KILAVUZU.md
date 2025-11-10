# UniMe Kütüphane Rezervasyon Botu - Kurulum ve Kullanım Kılavuzu

## 📋 İçindekiler
1. [Hızlı Başlangıç](#hızlı-başlangıç)
2. [Detaylı Kurulum](#detaylı-kurulum)
3. [Script Açıklamaları](#script-açıklamaları)
4. [Kullanım Senaryoları](#kullanım-senaryoları)
5. [Sorun Giderme](#sorun-giderme)
6. [Güvenlik Notları](#güvenlik-notları)

---

## 🚀 Hızlı Başlangıç

### Adım 1: Python Kurulumu
```bash
# Python yüklü değilse: https://www.python.org/downloads/
python --version  # Kontrol için
```

### Adım 2: Gerekli Kütüphaneleri Kur
```bash
pip install -r requirements.txt
```

### Adım 3: Chrome Driver İndirme
```bash
# Otomatik kurulum için:
pip install webdriver-manager
```

### Adım 4: Bilgilerinizi Güncelleyin
Her script'te şu satırları kendi bilgilerinizle değiştirin:
```python
NOME_COGNOME = "Ali Erkan Ocaklı"  # Adınız Soyadınız
EMAIL = "alierkn.ocakli@gmail.com"  # @unime.it veya @studenti.unime.it
MATRICOLA = "555012"  # Öğrenci numaranız
SALA_TIPO = "Sala lettura - Rettorato"  # İstediğiniz salon
```

### Adım 5: URL'yi Güncelleyin
```python
REZERVASYON_URL = "https://www.unime.it/prenotazioni-biblioteca"  # Gerçek URL'yi yazın
```

---

## 📦 Script Açıklamaları

### 1. **unime_library_bot.py** (Ana Bot)
**Özellikler:**
- Tam özellikli rezervasyon botu
- Masaüstü bildirimleri
- Log kayıtları
- Zamanlama özellikleri
- Hata yönetimi

**Kullanım:**
```bash
python unime_library_bot.py
```

### 2. **quick_reservation.py** (Hızlı Rezervasyon)
**Özellikler:**
- Minimalist ve hızlı
- Tek seferlik rezervasyon
- Basit arayüz

**Kullanım:**
```bash
python quick_reservation.py
```

### 3. **aggressive_slot_catcher.py** (Slot Kapma Modu)
**Özellikler:**
- Sürekli deneme
- Ses uyarısı
- Otomatik saat kontrolü
- Yüksek başarı oranı

**Kullanım:**
```bash
python aggressive_slot_catcher.py
```

---

## 💡 Kullanım Senaryoları

### Senaryo 1: Her Gün Saat 00:00'da Otomatik Rezervasyon
```python
# unime_library_bot.py içinde
bot = UniMeKutuphaneBot(config)
bot.zamanli_rezervasyon(0, 0)  # 00:00'da çalışır
```

### Senaryo 2: Slot Açılana Kadar Deneme
```python
# aggressive_slot_catcher.py çalıştırın
# Seçenek 1'i seçin
# Script otomatik olarak müsait slot bulana kadar deneyecek
```

### Senaryo 3: Belirli Bir Tarih İçin Rezervasyon
```python
bot = UniMeKutuphaneBot(config)
bot.rezervasyon_yap(tarih="2025-11-15", otomatik_tarih=False)
```

---

## 🛠️ Sorun Giderme

### Problem: "No more slots available" hatası
**Çözüm:**
- `aggressive_slot_catcher.py` kullanın
- Deneme aralığını azaltın (DENEME_ARALIGI = 0.5)
- Farklı salon tiplerini deneyin

### Problem: Chrome driver hatası
**Çözüm:**
```bash
# Otomatik güncelleme
pip install --upgrade webdriver-manager
```

### Problem: Element bulunamadı hatası
**Çözüm:**
1. Sayfanın HTML yapısını kontrol edin (F12)
2. XPath veya CSS selector'ları güncelleyin
3. Bekleme sürelerini artırın

### Problem: IP Ban / Çok fazla istek
**Çözüm:**
```python
# Proxy kullanımı ekleyin
options.add_argument('--proxy-server=http://your-proxy:port')

# Veya VPN kullanın
```

---

## 🔒 Güvenlik Notları

### 1. Şifre Güvenliği
```python
# Şifreyi kod içinde saklamayın!
import os
from getpass import getpass

# Çevre değişkeni kullanın
PASSWORD = os.getenv('UNIME_PASSWORD')

# Veya runtime'da isteyin
PASSWORD = getpass("Şifrenizi girin: ")
```

### 2. Config Dosyası Kullanımı
```python
# config.json oluşturun
{
    "nome_cognome": "Ali Erkan Ocaklı",
    "email": "alierkn.ocakli@gmail.com",
    "matricola": "555012"
}

# Script'te okuyun
import json
with open('config.json') as f:
    config = json.load(f)
```

### 3. Log Dosyalarını Gizleyin
```bash
# .gitignore dosyasına ekleyin
*.log
config.json
credentials.txt
```

---

## 📊 Performans İpuçları

### 1. Headless Mode (Arka Plan)
```python
options.add_argument('--headless')  # Görsel arayüz olmadan çalışır
```

### 2. Paralel Deneme
```python
from concurrent.futures import ThreadPoolExecutor

def paralel_deneme():
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(rezervasyon_yap) for _ in range(3)]
```

### 3. Optimal Deneme Zamanları
- **00:00-00:05**: Yeni günün açılması
- **08:00-08:05**: Sabah slotları
- **12:00-12:05**: Öğle slotları

---

## 🚨 Önemli Uyarılar

1. **Üniversite Kuralları**: Bot kullanımının kurallara uygun olduğundan emin olun
2. **Adil Kullanım**: Diğer öğrencilerin haklarını gözetin
3. **Test Ortamı**: Önce test sayfalarında deneyin
4. **Yedekleme**: Manuel rezervasyon yapmayı da bilin

---

## 📞 Destek

Sorularınız için:
- Email: alierkn.ocakli@gmail.com
- Matricola: 555012

---

## 🔄 Güncelleme Notları

**v1.0** (Kasım 2025)
- İlk sürüm
- 3 farklı script
- Otomatik zamanlama
- Ses bildirimleri

---

## Windows Task Scheduler ile Otomatik Çalıştırma

1. Task Scheduler'ı açın
2. "Create Basic Task" seçin
3. Tetikleyici olarak "Daily" seçin
4. Saat: 23:59
5. Action: Start a program
6. Program: `C:\Python\python.exe`
7. Arguments: `C:\Scripts\aggressive_slot_catcher.py`

## Linux/Mac Cron ile Otomatik Çalıştırma

```bash
# Terminal'de
crontab -e

# Ekleyin (her gün 23:59'da)
59 23 * * * /usr/bin/python3 /home/user/aggressive_slot_catcher.py

# Kaydedin ve çıkın
```

---

İyi rezervasyonlar! 🎓📚