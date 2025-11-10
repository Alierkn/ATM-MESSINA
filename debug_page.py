#!/usr/bin/env python3
"""
Sayfa yapısını inceleme scripti
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def debug_page():
    """Sayfanın HTML yapısını incele"""
    
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    
    url = "https://antonello.unime.it/prenotazione-postazione-biblioteca/?formid=28"
    
    print("Sayfaya gidiliyor...")
    driver.get(url)
    time.sleep(5)
    
    print("\n" + "="*60)
    print("SAYFA BİLGİLERİ")
    print("="*60)
    print(f"URL: {driver.current_url}")
    print(f"Başlık: {driver.title}")
    
    print("\n" + "="*60)
    print("TÜM INPUT ELEMENTLERİ")
    print("="*60)
    inputs = driver.find_elements(By.TAG_NAME, "input")
    for i, inp in enumerate(inputs, 1):
        print(f"\n{i}. Input:")
        print(f"   Type: {inp.get_attribute('type')}")
        print(f"   Name: {inp.get_attribute('name')}")
        print(f"   ID: {inp.get_attribute('id')}")
        print(f"   Class: {inp.get_attribute('class')}")
        print(f"   Placeholder: {inp.get_attribute('placeholder')}")
    
    print("\n" + "="*60)
    print("TÜM SELECT ELEMENTLERİ")
    print("="*60)
    selects = driver.find_elements(By.TAG_NAME, "select")
    for i, sel in enumerate(selects, 1):
        print(f"\n{i}. Select:")
        print(f"   Name: {sel.get_attribute('name')}")
        print(f"   ID: {sel.get_attribute('id')}")
        print(f"   Class: {sel.get_attribute('class')}")
        print("   Seçenekler:")
        try:
            from selenium.webdriver.support.ui import Select
            select_obj = Select(sel)
            for opt in select_obj.options:
                print(f"      - {opt.text} (value: {opt.get_attribute('value')})")
        except:
            print("      (Seçenekler okunamadı)")
    
    print("\n" + "="*60)
    print("TÜM BUTTON ELEMENTLERİ")
    print("="*60)
    buttons = driver.find_elements(By.TAG_NAME, "button")
    for i, btn in enumerate(buttons, 1):
        print(f"\n{i}. Button:")
        print(f"   Text: {btn.text}")
        print(f"   Type: {btn.get_attribute('type')}")
        print(f"   Name: {btn.get_attribute('name')}")
        print(f"   ID: {btn.get_attribute('id')}")
        print(f"   Class: {btn.get_attribute('class')}")
    
    print("\n" + "="*60)
    print("SAYFA KAYNAĞI (İlk 5000 karakter)")
    print("="*60)
    print(driver.page_source[:5000])
    
    print("\n\nTarayıcı 30 saniye açık kalacak, inceleme yapabilirsiniz...")
    time.sleep(30)
    
    driver.quit()
    print("\nTarayıcı kapatıldı.")

if __name__ == "__main__":
    debug_page()

