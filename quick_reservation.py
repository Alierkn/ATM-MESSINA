"""
Hızlı Başlangıç Script - UniMe Kütüphane Rezervasyonu
Minimalist ve hızlı çalışan versiyon
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time

# AYARLAR - BU KISMI KENDİNİZE GÖRE DÜZENLEYİN
NOME_COGNOME = "Ali Erkan Ocaklı"
EMAIL = "alierkn.ocakli@gmail.com" 
MATRICOLA = "555012"
SALA_TIPO = "Sala lettura - Rettorato"

# Chrome driver başlat
driver = webdriver.Chrome()

try:
    # Sayfa URL'sini güncelle
    driver.get("https://www.unime.it/prenotazioni-biblioteca")  # GERÇEK URL'Yİ BURAYA YAZIN
    time.sleep(2)
    
    # Form doldurma
    print("Form dolduruluyor...")
    
    # İsim Soyisim
    nome_input = driver.find_element(By.XPATH, "//input[contains(@placeholder, 'Nome')]")
    nome_input.send_keys(NOME_COGNOME)
    
    # Salon tipi seç
    tipologia = Select(driver.find_element(By.TAG_NAME, "select"))
    tipologia.select_by_visible_text(SALA_TIPO)
    
    # Email
    email_input = driver.find_element(By.XPATH, "//input[@type='email']")
    email_input.send_keys(EMAIL)
    
    # Matricola
    matricola_input = driver.find_element(By.XPATH, "//input[contains(@placeholder, 'Matricola')]")
    matricola_input.send_keys(MATRICOLA)
    
    # Takvimden ilk müsait günü seç
    print("Müsait tarih aranıyor...")
    calendar_days = driver.find_elements(By.XPATH, "//td[not(@class='disabled')]")
    
    for day in calendar_days:
        try:
            day.click()
            print(f"Tarih seçildi: {day.text}")
            break
        except:
            continue
    
    time.sleep(1)
    
    # Checkboxları işaretle
    checkboxes = driver.find_elements(By.XPATH, "//input[@type='checkbox']")
    for checkbox in checkboxes:
        if not checkbox.is_selected():
            checkbox.click()
    
    # Rezervasyon butonuna tıkla
    print("Rezervasyon gönderiliyor...")
    submit_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Prenota')]")
    submit_btn.click()
    
    time.sleep(3)
    
    # Sonucu kontrol et
    if "success" in driver.page_source.lower() or "conferm" in driver.page_source.lower():
        print("✅ REZERVASYON BAŞARILI!")
    else:
        print("❌ Rezervasyon başarısız, sayfayı kontrol edin")
        
    input("Devam etmek için Enter'a basın...")
    
except Exception as e:
    print(f"Hata: {e}")
    input("Devam etmek için Enter'a basın...")
    
finally:
    driver.quit()
