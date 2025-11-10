"""
Agresif Sürekli Deneme Script - Slot Kapma Modu
Müsait slot açıldığı anda rezervasyon yapar
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from datetime import datetime
import winsound  # Windows için ses uyarısı

# AYARLAR
NOME_COGNOME = "Ali Erkan Ocaklı"
EMAIL = "alierkn.ocakli@gmail.com"
MATRICOLA = "555012"
SALA_TIPO = "Sala lettura - Rettorato"
REZERVASYON_URL = "https://www.unime.it/prenotazioni-biblioteca"  # GERÇEK URL

# Deneme ayarları
DENEME_ARALIGI = 1  # Saniye (ne kadar düşükse o kadar hızlı dener)
MAX_DENEME = 1000  # Maksimum deneme sayısı
HEADLESS = False  # True = Arka planda çalışır

def ses_cal():
    """Başarılı rezervasyon için ses uyarısı"""
    try:
        for _ in range(3):
            winsound.Beep(1000, 500)  # Windows
            time.sleep(0.5)
    except:
        print("\a\a\a")  # Alternatif bip sesi

def hizli_rezervasyon():
    """Ana rezervasyon fonksiyonu"""
    
    # Chrome ayarları
    options = webdriver.ChromeOptions()
    if HEADLESS:
        options.add_argument('--headless')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(10)
    
    deneme_sayisi = 0
    basarili = False
    
    print(f"""
    ╔════════════════════════════════════════════════╗
    ║     SLOT KAPMA MODU AKTİF!                    ║
    ║     Deneme aralığı: {DENEME_ARALIGI} saniye               ║
    ║     Max deneme: {MAX_DENEME}                         ║
    ╚════════════════════════════════════════════════╝
    """)
    
    while deneme_sayisi < MAX_DENEME and not basarili:
        deneme_sayisi += 1
        saat = datetime.now().strftime("%H:%M:%S")
        
        try:
            print(f"[{saat}] Deneme #{deneme_sayisi}...", end="")
            
            # Sayfaya git
            driver.get(REZERVASYON_URL)
            
            # Form doldur (HIZLI)
            driver.find_element(By.XPATH, "//input[contains(@placeholder, 'Nome')]").send_keys(NOME_COGNOME)
            Select(driver.find_element(By.TAG_NAME, "select")).select_by_visible_text(SALA_TIPO)
            driver.find_element(By.XPATH, "//input[@type='email']").send_keys(EMAIL)
            driver.find_element(By.XPATH, "//input[contains(@placeholder, 'Matricola')]").send_keys(MATRICOLA)
            
            # İlk müsait tarihi seç
            musait_gun = driver.find_elements(By.XPATH, "//td[not(contains(@class,'disabled')) and not(contains(@class,'past'))]")
            
            if musait_gun:
                musait_gun[0].click()
                
                # Checkboxları işaretle
                for cb in driver.find_elements(By.XPATH, "//input[@type='checkbox']"):
                    if not cb.is_selected():
                        cb.click()
                
                # Gönder
                driver.find_element(By.XPATH, "//button[contains(text(), 'Prenota')]").click()
                
                # Başarı kontrolü
                time.sleep(2)
                if "success" in driver.page_source.lower() or "conferm" in driver.page_source.lower():
                    print(" ✅ BAŞARILI!")
                    print(f"\n🎉 REZERVASYON YAPILDI! Saat: {saat}")
                    ses_cal()
                    basarili = True
                    
                    # Email detaylarını göster
                    print(f"Email adresinizi kontrol edin: {EMAIL}")
                    input("\nKapatmak için Enter'a basın...")
                else:
                    print(" ❌ Başarısız")
            else:
                print(" ⚠️ Müsait slot yok")
                
        except TimeoutException:
            print(" ⏱️ Zaman aşımı")
        except Exception as e:
            print(f" ❗ Hata: {str(e)[:30]}")
        
        if not basarili and deneme_sayisi < MAX_DENEME:
            time.sleep(DENEME_ARALIGI)
    
    if not basarili:
        print(f"\n❌ {MAX_DENEME} deneme sonrası rezervasyon yapılamadı.")
    
    driver.quit()
    return basarili

def surekli_kontrol():
    """Belirlenen saatlerde otomatik başlatma"""
    
    # Kritik saatler (rezervasyonların açıldığı saatler)
    KONTROL_SAATLERI = ["00:00", "08:00", "12:00", "18:00"]
    
    print(f"Otomatik kontrol saatleri: {', '.join(KONTROL_SAATLERI)}")
    print("Program çalışıyor... (Durdurmak için Ctrl+C)")
    
    while True:
        simdi = datetime.now().strftime("%H:%M")
        
        if simdi in KONTROL_SAATLERI:
            print(f"\n⏰ {simdi} - Otomatik kontrol başlatılıyor!")
            if hizli_rezervasyon():
                break
            time.sleep(61)  # Aynı dakikada tekrar çalışmasını engelle
        
        time.sleep(30)  # 30 saniyede bir kontrol et

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════╗
    ║     UniMe Kütüphane - Agresif Slot Kapma      ║
    ╠════════════════════════════════════════════════╣
    ║  1. Hemen başlat (sürekli deneme)             ║
    ║  2. Belirlenen saatlerde otomatik kontrol     ║
    ║  3. Çıkış                                      ║
    ╚════════════════════════════════════════════════╝
    """)
    
    secim = input("Seçiminiz (1-3): ")
    
    if secim == "1":
        hizli_rezervasyon()
    elif secim == "2":
        surekli_kontrol()
    else:
        print("Çıkılıyor...")
