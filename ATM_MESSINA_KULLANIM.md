# 🚌 ATM Messina Otobüs Takip Sistemi

ATM Messina duraklarınızdan otobüs bilgilerini çekip güzel bir arayüzle görüntüleyen web uygulaması.

## 📋 Özellikler

- ✅ Durak URL'lerini kaydetme ve yönetme
- ✅ Duraklardan otobüs bilgilerini otomatik çekme
- ✅ Modern ve responsive tasarım
- ✅ Otomatik yenileme (30 saniye)
- ✅ Gerçek zamanlı veri güncelleme
- ✅ Kolay kullanım

## 🚀 Kurulum

### 1. Gerekli Paketleri Kurun

```bash
pip install -r requirements.txt
```

### 2. Uygulamayı Başlatın

```bash
python atm_messina_app.py
```

### 3. Tarayıcıda Açın

Uygulama başladıktan sonra tarayıcınızda şu adresi açın:
```
http://localhost:5000
```

## 📖 Kullanım

### Durak Ekleme

1. Ana sayfada "Durak Adı" ve "Durak URL'si" alanlarını doldurun
2. "Durak Ekle" butonuna tıklayın
3. Durak listenize eklenecektir

### Otobüs Bilgilerini Görüntüleme

- **Tek Durak:** Durak kartındaki "Otobüsleri Göster" butonuna tıklayın
- **Tüm Duraklar:** "Tüm Durakları Yenile" butonuna tıklayın

### Otomatik Yenileme

"Otomatik Yenile (30 saniye)" seçeneğini işaretleyerek otobüs bilgilerinin otomatik olarak güncellenmesini sağlayabilirsiniz.

## ⚙️ Özelleştirme

### ATM Messina URL Yapısına Göre Ayarlama

`atm_messina_app.py` dosyasındaki `fetch_durak_data()` fonksiyonunu ATM Messina'nın gerçek URL yapısına göre özelleştirmeniz gerekebilir.

#### Örnek 1: JSON API Kullanıyorsa

Eğer ATM Messina JSON formatında veri döndürüyorsa, fonksiyon zaten bunu destekliyor. Sadece JSON yapısına göre `json_data.get()` kısımlarını güncelleyin:

```python
return {
    'success': True,
    'otobusler': json_data.get('buses', []),  # 'buses' yerine gerçek key'i yazın
    'durak_adi': json_data.get('stop_name', ''),
    'timestamp': datetime.now().isoformat()
}
```

#### Örnek 2: HTML Scraping Gerekliyse

Eğer HTML sayfasından veri çekmeniz gerekiyorsa, BeautifulSoup selector'larını güncelleyin:

```python
# Örnek: Belirli class veya id'ye sahip elementleri bul
otobus_elements = soup.find_all('div', class_='bus-info')

otobusler = []
for element in otobus_elements:
    otobus = {
        'hat': element.find('span', class_='line-number').text,
        'varis': element.find('span', class_='arrival-time').text,
        'yon': element.find('span', class_='direction').text
    }
    otobusler.append(otobus)
```

#### Örnek 3: API Endpoint'i Farklıysa

Eğer URL'den farklı bir endpoint'e istek atmanız gerekiyorsa:

```python
# URL'den durak ID'sini çıkar
durak_id = url.split('/')[-1]
api_url = f'https://api.atmmessina.it/stops/{durak_id}/arrivals'

response = requests.get(api_url, headers=headers, timeout=10)
```

## 📁 Dosya Yapısı

```
.
├── atm_messina_app.py      # Flask backend uygulaması
├── templates/
│   └── atm_messina.html    # Frontend HTML sayfası
├── duraklar.json           # Kaydedilen duraklar (otomatik oluşur)
└── requirements.txt        # Python paketleri
```

## 🔧 Sorun Giderme

### Durak Verisi Çekilemiyor

1. URL'nin doğru olduğundan emin olun
2. ATM Messina'nın HTML/API yapısını kontrol edin
3. `fetch_durak_data()` fonksiyonunu gerçek yapıya göre güncelleyin
4. Tarayıcı geliştirici araçlarında (F12) Network sekmesinden gerçek API isteklerini inceleyin

### Port Zaten Kullanılıyor

Eğer 5000 portu kullanılıyorsa, `atm_messina_app.py` dosyasının sonundaki port numarasını değiştirin:

```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Farklı port
```

### Duraklar Görünmüyor

- `duraklar.json` dosyasının oluşturulduğundan emin olun
- Tarayıcı konsolunda (F12) hata mesajlarını kontrol edin

## 💡 İpuçları

1. **Gerçek URL Yapısını Öğrenme:**
   - ATM Messina'nın QR kodunu okutun
   - Tarayıcıda sayfayı açın
   - F12 ile Developer Tools'u açın
   - Network sekmesinden gerçek API isteklerini görün
   - Response'u inceleyerek veri yapısını anlayın

2. **Test Etme:**
   - Önce bir durak ekleyip test edin
   - Console'da (F12) hata mesajlarını kontrol edin
   - `fetch_durak_data()` fonksiyonunu adım adım test edin

3. **Performans:**
   - Çok fazla durak varsa, otomatik yenileme süresini artırın
   - Rate limiting için `time.sleep()` süresini ayarlayın

## 📝 Notlar

- Bu uygulama ATM Messina'nın resmi API'si değildir
- URL yapısı değişirse `fetch_durak_data()` fonksiyonunu güncellemeniz gerekebilir
- Veri çekme hızı ATM Messina'nın sunucu yanıt süresine bağlıdır

## 🎨 Özelleştirme

HTML/CSS'i özelleştirmek için `templates/atm_messina.html` dosyasını düzenleyebilirsiniz:
- Renkleri değiştirmek için CSS'teki `#667eea` ve `#764ba2` değerlerini değiştirin
- Layout'u değiştirmek için grid yapısını düzenleyin
- Yeni özellikler eklemek için JavaScript fonksiyonlarını genişletin

---

**İyi kullanımlar! 🚌**

