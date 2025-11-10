# UniMe Kütüphane Rezervasyon Botu

Messina Üniversitesi kütüphane rezervasyon sistemini otomatikleştiren Python botu.

## 🚀 Kurulum

### 1. Gereksinimler
- Python 3.7+
- Chrome tarayıcı
- ChromeDriver (Selenium 4.x otomatik yönetir)

### 2. Paketleri Yükleme

```bash
# Virtual environment oluştur
python3 -m venv venv

# Virtual environment'ı aktif et
source venv/bin/activate  # macOS/Linux
# veya
venv\Scripts\activate  # Windows

# Paketleri yükle
pip install -r requirements.txt
```

## 📖 Kullanım

### Botu Çalıştırma

```bash
# Virtual environment'ı aktif et
source venv/bin/activate

# Botu çalıştır
python unime_library_bot.py
```

### Menü Seçenekleri

1. **Hemen rezervasyon yap**: Anında rezervasyon yapmaya çalışır
2. **Sürekli deneme modu**: Slot açılana kadar sürekli dener
3. **Zamanlanmış rezervasyon**: Her gün belirli saatte otomatik rezervasyon
4. **Özel tarih için rezervasyon**: Belirli bir tarih için rezervasyon
5. **Çıkış**: Botu kapatır

## ⚙️ Yapılandırma

`unime_library_bot.py` dosyasındaki `main()` fonksiyonunda kullanıcı bilgilerinizi güncelleyin:

```python
config = {
    'nome_cognome': 'Adınız Soyadınız',
    'email': 'email@example.com',
    'matricola': 'Öğrenci Numaranız',
    'sala_tipo': 'Sala lettura - Rettorato',  # Salon tipi
    'headless': False  # True = arka planda çalışır
}
```

## 🔧 Özellikler

- ✅ Esnek element bulma (birden fazla strateji)
- ✅ Güvenli tıklama ve form doldurma
- ✅ Otomatik hata yönetimi ve screenshot alma
- ✅ Detaylı logging
- ✅ Masaüstü bildirimleri
- ✅ Bot algılamayı önleyen ayarlar

## 📝 Loglar

Bot çalışırken `rezervasyon_log.txt` dosyasına loglar kaydedilir.

## ⚠️ Notlar

- Gerçek web sitesinin HTML yapısına göre XPath'ler güncellenebilir
- Hata durumunda screenshot'lar otomatik kaydedilir
- ChromeDriver Selenium 4.x ile otomatik yönetilir

## 🐛 Sorun Giderme

1. **ChromeDriver hatası**: Selenium 4.x otomatik yönetir, manuel kurulum gerekmez
2. **Element bulunamadı**: Screenshot'lara bakarak XPath'leri güncelleyin
3. **Import hatası**: Virtual environment'ın aktif olduğundan emin olun

## 📄 Lisans

Bu proje kişisel kullanım içindir.

