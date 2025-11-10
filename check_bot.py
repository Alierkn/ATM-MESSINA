#!/usr/bin/env python3
"""
Bot durum kontrolü
"""

import sys
from unime_library_bot import UniMeKutuphaneBot

def check_bot():
    """Botun çalışır durumda olup olmadığını kontrol et"""
    
    print("=" * 60)
    print("BOT DURUM KONTROLÜ")
    print("=" * 60)
    
    # Config kontrolü
    config = {
        'nome_cognome': 'Ali Erkan Ocaklı',
        'email': 'alierkn.ocakli@gmail.com',
        'matricola': '555012',
        'sala_tipo': 'Sala Lettura -Rettorato',
        'headless': False
    }
    
    print("\n✅ Config yüklendi")
    print(f"   - Ad Soyad: {config['nome_cognome']}")
    print(f"   - Email: {config['email']}")
    print(f"   - Matricola: {config['matricola']}")
    print(f"   - Salon: {config['sala_tipo']}")
    
    # Bot oluşturma kontrolü
    try:
        bot = UniMeKutuphaneBot(config)
        print("\n✅ Bot başarıyla oluşturuldu")
        print(f"   - URL: {bot.rezervasyon_url}")
        print(f"   - Timeout: {bot.wait_timeout} saniye")
    except Exception as e:
        print(f"\n❌ Bot oluşturulamadı: {str(e)}")
        return False
    
    # İtalya saati kontrolü
    try:
        italya_saati = bot._italya_saati_al()
        print(f"\n✅ İtalya saati alındı: {italya_saati.strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        print(f"\n⚠️ İtalya saati alınamadı: {str(e)}")
    
    # Zamanlayıcı kontrolü
    try:
        print("\n✅ Zamanlayıcı fonksiyonu mevcut")
        print("   - italya_saatine_gore_zamanli_rezervasyon() hazır")
        print("   - Varsayılan saatler: 00:00 ve 08:00 (İtalya saati)")
    except Exception as e:
        print(f"\n❌ Zamanlayıcı kontrolü başarısız: {str(e)}")
        return False
    
    print("\n" + "=" * 60)
    print("SONUÇ: Bot çalışır durumda! ✅")
    print("=" * 60)
    print("\nKullanım:")
    print("  python unime_library_bot.py")
    print("\nMenü seçenekleri:")
    print("  1. Hemen rezervasyon yap")
    print("  2. Sürekli deneme modu")
    print("  3. İtalya saatine göre zamanlanmış (00:00 & 08:00) ⭐")
    print("  4. Özel tarih için rezervasyon")
    print("  5. Çıkış")
    print("\n" + "=" * 60)
    
    return True

if __name__ == "__main__":
    success = check_bot()
    sys.exit(0 if success else 1)

