# Bot Durdurma Talimatları

## 🛑 Botu Durdurma Yöntemleri

### Yöntem 1: Terminal'de Ctrl+C (Önerilen)
Bot çalışırken terminal penceresinde:
```
Ctrl + C
```
Basın. Bot güvenli bir şekilde durur.

### Yöntem 2: Process ID ile Durdurma
Eğer bot arka planda çalışıyorsa:

1. **Process ID'yi bul:**
```bash
ps aux | grep "python.*unime_library_bot" | grep -v grep
```

2. **Process'i durdur:**
```bash
kill <PID>
```

Veya zorla durdurmak için:
```bash
kill -9 <PID>
```

### Yöntem 3: Tüm Python Bot Process'lerini Durdur
```bash
pkill -f "unime_library_bot"
```

### Yöntem 4: macOS Activity Monitor
1. Activity Monitor'u açın
2. "python" veya "unime_library_bot" ara
3. Process'i seçip "Quit" veya "Force Quit" yapın

## 📝 Notlar

- Bot zamanlanmış modda çalışıyorsa (seçenek 3), Ctrl+C ile güvenli şekilde durur
- Bot rezervasyon yaparken durdurursanız, mevcut işlem tamamlanana kadar bekleyebilir
- Log dosyası (`rezervasyon_log.txt`) her zaman güncel durumu gösterir

## ✅ Bot Çalışıyor mu Kontrol Et

```bash
ps aux | grep "python.*unime_library_bot" | grep -v grep
```

Eğer çıktı varsa, bot çalışıyor demektir.

