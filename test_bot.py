#!/usr/bin/env python3
"""
Bot test scripti - Hemen rezervasyon yapmayı dener
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

def test_bot():
    """Botu test et"""
    
    # Kullanıcı ayarları
    config = {
        'nome_cognome': 'Ali Erkan Ocaklı',
        'email': 'alierkn.ocakli@gmail.com',
        'matricola': '555012',
        'sala_tipo': 'Sala Lettura -Rettorato',
        'headless': False  # False = tarayıcıyı göster (test için)
    }
    
    print("=" * 60)
    print("UniMe Kütüphane Botu - Test Modu")
    print("=" * 60)
    print(f"URL: {config.get('url', 'https://antonello.unime.it/prenotazione-postazione-biblioteca/?formid=28')}")
    print(f"Ad Soyad: {config['nome_cognome']}")
    print(f"Email: {config['email']}")
    print(f"Matricola: {config['matricola']}")
    print(f"Salon: {config['sala_tipo']}")
    print("=" * 60)
    print("\nBot başlatılıyor...\n")
    
    # Bot oluştur
    bot = UniMeKutuphaneBot(config)
    
    # Hemen rezervasyon yapmayı dene
    try:
        result = bot.rezervasyon_yap()
        if result:
            print("\n✅ TEST BAŞARILI: Rezervasyon yapıldı!")
        else:
            print("\n⚠️ TEST SONUCU: Rezervasyon yapılamadı (loglara bakın)")
    except Exception as e:
        print(f"\n❌ TEST HATASI: {str(e)}")
        logging.exception("Test hatası")

if __name__ == "__main__":
    test_bot()

