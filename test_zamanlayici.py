#!/usr/bin/env python3
"""
Zamanlayıcı test scripti - İtalya saatini kontrol eder
"""

from unime_library_bot import UniMeKutuphaneBot
import logging

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rezervasyon_log.txt'),
        logging.StreamHandler()
    ]
)

def test_zamanlayici():
    """Zamanlayıcıyı test et"""
    
    # Kullanıcı ayarları
    config = {
        'nome_cognome': 'Ali Erkan Ocaklı',
        'email': 'alierkn.ocakli@gmail.com',
        'matricola': '555012',
        'sala_tipo': 'Sala Lettura -Rettorato',
        'headless': False
    }
    
    print("=" * 60)
    print("İTALYA SAATİ ZAMANLAYICI TESTİ")
    print("=" * 60)
    
    # Bot oluştur
    bot = UniMeKutuphaneBot(config)
    
    # İtalya saatini göster
    italya_saati = bot._italya_saati_al()
    print(f"\nŞu anki İtalya saati: {italya_saati.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Yerel saat: {italya_saati}")
    
    # Test için 1 dakika sonrasını ayarla (hızlı test)
    from datetime import datetime, timedelta
    test_saat = italya_saati + timedelta(minutes=1)
    test_saat_saat = test_saat.hour
    test_saat_dakika = test_saat.minute
    
    print(f"\nTest için zamanlayıcı: {test_saat_saat:02d}:{test_saat_dakika:02d}")
    print("(Normal kullanımda 00:00 ve 08:00 kullanılır)")
    print("\nZamanlayıcı başlatılıyor... (Ctrl+C ile durdurun)\n")
    
    # Test için 1 dakika sonrasını kullan
    bot.italya_saatine_gore_zamanli_rezervasyon(saatler=[(test_saat_saat, test_saat_dakika)])

if __name__ == "__main__":
    test_zamanlayici()

