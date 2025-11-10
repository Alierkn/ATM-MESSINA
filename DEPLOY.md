# 🚀 ATM Messina Bot - Deploy Kılavuzu

Bu uygulamayı cloud'a deploy etmek için aşağıdaki adımları izleyin.

## 📋 Seçenekler

### 1. **Render.com** (Önerilen - Ücretsiz)

1. [Render.com](https://render.com) hesabı oluşturun
2. "New +" → "Web Service" seçin
3. GitHub repo'nuzu bağlayın veya direkt deploy edin
4. Ayarlar:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python atm_messina_app.py`
   - **Environment Variables**:
     - `PORT`: `5001` (Render otomatik atar)
     - `FLASK_DEBUG`: `False`

### 2. **Railway.app** (Ücretsiz)

1. [Railway.app](https://railway.app) hesabı oluşturun
2. "New Project" → "Deploy from GitHub repo"
3. Repo'nuzu seçin
4. Railway otomatik olarak `railway.json` dosyasını kullanır

### 3. **Heroku** (Ücretli olabilir)

1. [Heroku](https://heroku.com) hesabı oluşturun
2. Heroku CLI kurun
3. Terminal'de:
```bash
heroku create atm-messina-bot
git push heroku main
```

## 📁 Veri Saklama

Duraklar `data/duraklar.json` dosyasında saklanır. Cloud platformlarda bu dosya persistent storage'da kalır.

**Not**: Bazı platformlarda (örneğin Heroku) dosya sistemi ephemeral olabilir. Bu durumda:
- Heroku için: PostgreSQL addon kullanın
- Railway için: Persistent volume ekleyin
- Render için: Disk storage kullanın

## 🔧 Gerekli Dosyalar

- ✅ `requirements.txt` - Python paketleri
- ✅ `Procfile` - Heroku/Railway için
- ✅ `runtime.txt` - Python versiyonu
- ✅ `render.yaml` - Render için
- ✅ `railway.json` - Railway için

## 📝 GitHub'a Push

```bash
git init
git add .
git commit -m "ATM Messina Bot - Initial commit"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

## 🌐 Deploy Sonrası

Deploy edildikten sonra:
1. Platform size bir URL verecek (örn: `https://atm-messina-bot.onrender.com`)
2. Bu URL'yi telefonunuzdan açabilirsiniz
3. Duraklarınız cloud'da saklanır

## ⚠️ Önemli Notlar

- **Port**: Cloud platformlar genelde `PORT` environment variable kullanır
- **Debug**: Production'da `debug=False` olmalı
- **Veri**: Duraklar `data/duraklar.json` dosyasında saklanır
- **Rate Limiting**: ATM Messina'nın rate limit'lerine dikkat edin

## 🐛 Sorun Giderme

### Port hatası
- `PORT` environment variable'ını kontrol edin
- Platform'un otomatik port atamasını kullanın

### Veri kayboluyor
- Persistent storage kullanın
- Database (PostgreSQL) kullanmayı düşünün

### Build hatası
- `requirements.txt` dosyasını kontrol edin
- Python versiyonunu kontrol edin (`runtime.txt`)

---

**İyi deploylar! 🚀**

