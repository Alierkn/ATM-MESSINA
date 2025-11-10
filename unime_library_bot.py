"""
Università degli Studi di Messina - Kütüphane Otomatik Rezervasyon Botu
Geliştirici: Ali Erkan Ocaklı
Amaç: Kütüphane rezervasyonunu otomatik yapmak
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException
from selenium.webdriver.common.action_chains import ActionChains
import time
from datetime import datetime, timedelta
import logging
import json
from plyer import notification
import schedule
import os
from functools import wraps
try:
    from zoneinfo import ZoneInfo
except ImportError:
    # Python 3.8 ve öncesi için pytz kullan
    try:
        import pytz
        ZoneInfo = None
    except ImportError:
        ZoneInfo = None
        pytz = None

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rezervasyon_log.txt'),
        logging.StreamHandler()
    ]
)

class UniMeKutuphaneBot:
    """Messina Üniversitesi Kütüphane Rezervasyon Botu"""
    
    def __init__(self, config):
        """
        Bot başlatıcı
        
        Args:
            config (dict): Kullanıcı bilgileri ve tercihler
        """
        self.config = config
        self.driver = None
        self.rezervasyon_url = "https://antonello.unime.it/prenotazione-postazione-biblioteca/?formid=28"
        self.wait_timeout = 15  # Bekleme süresi (saniye)
        
    def _retry_on_failure(self, max_retries=3, delay=1):
        """Retry decorator"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                for attempt in range(max_retries):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        if attempt == max_retries - 1:
                            raise
                        logging.warning(f"{func.__name__} başarısız (deneme {attempt + 1}/{max_retries}): {str(e)}")
                        time.sleep(delay)
                return None
            return wrapper
        return decorator
    
    def _find_element_multiple_strategies(self, strategies, timeout=None):
        """
        Birden fazla strateji ile element bul
        
        Args:
            strategies: List of tuples (By, selector)
            timeout: Bekleme süresi
        """
        if timeout is None:
            timeout = self.wait_timeout
            
        wait = WebDriverWait(self.driver, timeout)
        
        for by, selector in strategies:
            try:
                element = wait.until(EC.presence_of_element_located((by, selector)))
                if element:
                    logging.debug(f"Element bulundu: {by} = {selector}")
                    return element
            except (TimeoutException, NoSuchElementException):
                continue
        
        raise NoSuchElementException(f"Element bulunamadı. Denenen stratejiler: {strategies}")
    
    def _safe_click(self, element, use_javascript=False):
        """Güvenli tıklama - önce normal, sonra JavaScript"""
        try:
            if use_javascript:
                self.driver.execute_script("arguments[0].click();", element)
            else:
                # Element görünür ve tıklanabilir olana kadar bekle
                WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(element))
                element.click()
            return True
        except ElementNotInteractableException:
            # JavaScript ile dene
            try:
                self.driver.execute_script("arguments[0].click();", element)
                return True
            except Exception as e:
                logging.warning(f"JavaScript click de başarısız: {str(e)}")
                return False
        except Exception as e:
            logging.warning(f"Tıklama hatası: {str(e)}")
            return False
    
    def _safe_send_keys(self, element, text, clear_first=True):
        """Güvenli metin girişi"""
        try:
            if clear_first:
                element.clear()
            element.send_keys(text)
            time.sleep(0.3)  # Kısa bekleme
            return True
        except Exception as e:
            logging.warning(f"Metin girişi hatası: {str(e)}")
            # JavaScript ile dene
            try:
                self.driver.execute_script(f"arguments[0].value = '{text}';", element)
                return True
            except:
                return False
    
    def _wait_for_page_load(self, timeout=10):
        """Sayfanın yüklenmesini bekle"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            time.sleep(1)  # Ekstra bekleme
        except:
            pass
    
    def _take_screenshot(self, filename=None):
        """Hata durumunda screenshot al"""
        try:
            if filename is None:
                filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.driver.save_screenshot(filename)
            logging.info(f"Screenshot kaydedildi: {filename}")
        except Exception as e:
            logging.warning(f"Screenshot alınamadı: {str(e)}")
        
    def setup_driver(self, headless=False):
        """Chrome driver ayarları"""
        options = webdriver.ChromeOptions()
        
        # Temel ayarlar
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Headless mod (arka planda çalıştırma)
        if headless:
            options.add_argument('--headless=new')  # Yeni headless mod
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            
        # Performans ayarları
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-logging')
        options.add_argument('--log-level=3')
        
        # User agent ayarı (bot algılamaması için)
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Prefs ayarları
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0,
            "profile.managed_default_content_settings.images": 2
        }
        options.add_experimental_option("prefs", prefs)
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(30)
            self.driver.maximize_window()
            
            # Bot algılamayı önlemek için JavaScript çalıştır
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })
            
            logging.info("Driver başarıyla başlatıldı")
        except Exception as e:
            logging.error(f"Driver başlatılamadı: {str(e)}")
            raise
        
    def rezervasyon_yap(self, tarih=None, otomatik_tarih=True):
        """
        Ana rezervasyon fonksiyonu
        
        Args:
            tarih: Rezervasyon tarihi (None ise otomatik seçer)
            otomatik_tarih: En yakın müsait tarihi otomatik seç
        """
        try:
            self.setup_driver(headless=self.config.get('headless', False))
            
            # Rezervasyon sayfasına git
            logging.info(f"Rezervasyon sayfasına gidiliyor: {self.rezervasyon_url}")
            self.driver.get(self.rezervasyon_url)
            self._wait_for_page_load()
            
            # Sayfanın yüklendiğini doğrula
            time.sleep(2)
            
            # Form doldurma
            logging.info("Form dolduruluyor...")
            self._form_doldur()
            
            # Tarih seçimi
            logging.info("Tarih seçiliyor...")
            if otomatik_tarih:
                self._musait_tarih_sec()
            elif tarih:
                self._belirli_tarih_sec(tarih)
            
            time.sleep(1)
                
            # Checkboxları işaretle
            logging.info("Checkboxlar işaretleniyor...")
            self._checkboxlari_isaretle()
            
            time.sleep(1)
            
            # Rezervasyonu gönder
            logging.info("Rezervasyon gönderiliyor...")
            self._rezervasyonu_gonder()
            
            # Başarı kontrolü
            time.sleep(2)
            if self._rezervasyon_basarili_mi():
                self._bildirim_gonder("Başarılı!", "Kütüphane rezervasyonu yapıldı!")
                logging.info("✅ Rezervasyon başarıyla tamamlandı!")
                return True
            else:
                logging.warning("⚠️ Rezervasyon başarısız oldu - başarı mesajı bulunamadı")
                self._take_screenshot()
                return False
                
        except TimeoutException as e:
            logging.error(f"⏱️ Zaman aşımı hatası: {str(e)}")
            self._take_screenshot()
            self._bildirim_gonder("Hata!", f"Zaman aşımı: {str(e)}")
            return False
        except NoSuchElementException as e:
            logging.error(f"🔍 Element bulunamadı: {str(e)}")
            self._take_screenshot()
            self._bildirim_gonder("Hata!", f"Element bulunamadı: {str(e)}")
            return False
        except Exception as e:
            logging.error(f"❌ Rezervasyon hatası: {str(e)}", exc_info=True)
            self._take_screenshot()
            self._bildirim_gonder("Hata!", f"Rezervasyon yapılamadı: {str(e)}")
            return False
            
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                    logging.info("Driver kapatıldı")
                except:
                    pass
                
    def _form_doldur(self):
        """Form alanlarını doldur"""
        try:
            wait = WebDriverWait(self.driver, self.wait_timeout)
            
            # Nominativo (Ad Soyad) alanı - gerçek ID: fieldname2_1
            nome_strategies = [
                (By.ID, "fieldname2_1"),  # Gerçek ID
                (By.XPATH, "//input[@placeholder='Nome e Cognome']"),
                (By.XPATH, "//input[contains(@placeholder, 'Nome') or contains(@placeholder, 'Cognome')]"),
                (By.XPATH, "//input[@name='nome' or @name='cognome' or @name='nominativo']"),
            ]
            nome_field = self._find_element_multiple_strategies(nome_strategies)
            self._safe_send_keys(nome_field, self.config['nome_cognome'])
            logging.info("✅ İsim girildi")
            time.sleep(0.5)
            
            # Tipologia posto (Yer tipi) dropdown - gerçek class: ahbfield_service
            tipologia_strategies = [
                (By.CLASS_NAME, "ahbfield_service"),  # Gerçek class
                (By.XPATH, "//select[contains(@class, 'ahbfield_service')]"),
                (By.XPATH, "//select[contains(@class, 'tipologia')]"),
                (By.XPATH, "//select[contains(@class, 'service')]"),
                (By.XPATH, "//select[@name='tipologia' or @id='tipologia']"),
            ]
            
            tipologia_element = self._find_element_multiple_strategies(tipologia_strategies)
            tipologia_dropdown = Select(tipologia_element)
            
            # Dropdown seçeneklerini kontrol et
            try:
                # Önce tam eşleşme dene
                tipologia_dropdown.select_by_visible_text(self.config['sala_tipo'])
                logging.info(f"✅ Salon tipi seçildi: {self.config['sala_tipo']}")
            except:
                # Kısmi eşleşme dene
                options = [opt.text for opt in tipologia_dropdown.options]
                logging.info(f"Dropdown seçenekleri: {options}")
                found = False
                for opt in options:
                    if self.config['sala_tipo'].lower() in opt.lower() or opt.lower() in self.config['sala_tipo'].lower():
                        tipologia_dropdown.select_by_visible_text(opt)
                        logging.info(f"✅ Salon tipi seçildi (kısmi eşleşme): {opt}")
                        found = True
                        break
                if not found:
                    # Value ile dene (Rettorato için value: 330)
                    if "rettorato" in self.config['sala_tipo'].lower():
                        try:
                            tipologia_dropdown.select_by_value("330")
                            logging.info("✅ Salon tipi seçildi (value: 330 - Rettorato)")
                        except:
                            raise Exception(f"Salon tipi bulunamadı: {self.config['sala_tipo']}. Mevcut seçenekler: {options}")
                    else:
                        raise Exception(f"Salon tipi bulunamadı: {self.config['sala_tipo']}. Mevcut seçenekler: {options}")
            
            time.sleep(0.5)
            
            # E-mail - gerçek ID: email_1
            email_strategies = [
                (By.ID, "email_1"),  # Gerçek ID
                (By.XPATH, "//input[@placeholder='Email' or @type='email']"),
                (By.XPATH, "//input[@name='email' or @id='email']"),
            ]
            email_field = self._find_element_multiple_strategies(email_strategies)
            self._safe_send_keys(email_field, self.config['email'])
            logging.info("✅ Email girildi")
            time.sleep(0.5)
            
            # Matricola (Öğrenci numarası) - gerçek ID: fieldname5_1
            matricola_strategies = [
                (By.ID, "fieldname5_1"),  # Gerçek ID
                (By.XPATH, "//input[contains(@placeholder, 'Matricola')]"),
                (By.XPATH, "//input[@name='matricola' or @id='matricola']"),
            ]
            matricola_field = self._find_element_multiple_strategies(matricola_strategies)
            self._safe_send_keys(matricola_field, self.config['matricola'])
            logging.info("✅ Matricola girildi")
            time.sleep(0.5)
            
        except Exception as e:
            logging.error(f"❌ Form doldurma hatası: {str(e)}")
            self._take_screenshot()
            raise
            
    def _musait_tarih_sec(self, max_ay_gecis=3):
        """En yakın müsait tarihi otomatik seç"""
        try:
            wait = WebDriverWait(self.driver, self.wait_timeout)
            
            # Takvimi bul - birden fazla strateji
            calendar_strategies = [
                (By.CLASS_NAME, "calendar"),
                (By.XPATH, "//div[contains(@class, 'calendar')]"),
                (By.XPATH, "//table[contains(@class, 'calendar')]"),
                (By.ID, "calendar")
            ]
            
            try:
                calendar = self._find_element_multiple_strategies(calendar_strategies, timeout=5)
            except:
                logging.warning("Takvim bulunamadı, sayfadaki tüm tarihleri kontrol ediliyor...")
            
            # Müsait günleri bul - birden fazla strateji
            available_xpaths = [
                "//td[not(contains(@class, 'disabled')) and not(contains(@class, 'past')) and not(contains(@class, 'unavailable'))]",
                "//td[@class and not(contains(@class, 'disabled'))]",
                "//td[not(@disabled) and not(contains(@class, 'disabled'))]",
                "//button[not(@disabled) and not(contains(@class, 'disabled'))]",
                "//a[not(contains(@class, 'disabled'))]"
            ]
            
            available_days = []
            for xpath in available_xpaths:
                try:
                    days = self.driver.find_elements(By.XPATH, xpath)
                    # Sadece sayısal değerleri filtrele (gün numaraları)
                    for day in days:
                        text = day.text.strip()
                        if text.isdigit() and 1 <= int(text) <= 31:
                            available_days.append(day)
                    if available_days:
                        break
                except:
                    continue
            
            if available_days:
                # İlk müsait günü seç
                selected_day = available_days[0]
                day_text = selected_day.text
                if self._safe_click(selected_day):
                    logging.info(f"✅ Müsait tarih seçildi: {day_text}")
                    time.sleep(1.5)
                    
                    # Saat seçimi varsa
                    self._saat_sec()
                    return True
                else:
                    logging.warning("Tarih tıklanamadı, JavaScript ile deneniyor...")
                    self._safe_click(selected_day, use_javascript=True)
                    time.sleep(1.5)
                    self._saat_sec()
                    return True
            else:
                # Sonraki aya geç
                if max_ay_gecis > 0:
                    next_button_strategies = [
                        (By.XPATH, "//button[contains(@class, 'next-month')]"),
                        (By.XPATH, "//button[contains(@class, 'next')]"),
                        (By.XPATH, "//a[contains(@class, 'next')]"),
                        (By.XPATH, "//button[contains(text(), '>') or contains(text(), 'Next')]")
                    ]
                    
                    try:
                        next_button = self._find_element_multiple_strategies(next_button_strategies, timeout=5)
                        if self._safe_click(next_button):
                            logging.info("Sonraki aya geçiliyor...")
                            time.sleep(2)
                            return self._musait_tarih_sec(max_ay_gecis - 1)
                    except:
                        logging.warning("Sonraki ay butonu bulunamadı")
                        raise Exception("Müsait tarih bulunamadı")
                else:
                    raise Exception("Müsait tarih bulunamadı - maksimum ay geçişi aşıldı")
                
        except Exception as e:
            logging.error(f"❌ Tarih seçme hatası: {str(e)}")
            self._take_screenshot()
            raise
            
    def _belirli_tarih_sec(self, tarih):
        """Belirli bir tarihi seç"""
        try:
            # Tarih formatını parse et
            tarih_gun = tarih.split('-')[2].lstrip('0')  # Başındaki sıfırları kaldır
            
            # Tarih elementini bul - birden fazla strateji
            tarih_xpaths = [
                f"//td[text()='{tarih_gun}' and not(contains(@class, 'disabled'))]",
                f"//td[normalize-space(text())='{tarih_gun}' and not(contains(@class, 'disabled'))]",
                f"//button[text()='{tarih_gun}' and not(@disabled)]",
                f"//a[text()='{tarih_gun}' and not(contains(@class, 'disabled'))]"
            ]
            
            tarih_element = None
            for xpath in tarih_xpaths:
                try:
                    tarih_element = self.driver.find_element(By.XPATH, xpath)
                    break
                except:
                    continue
            
            if tarih_element:
                if self._safe_click(tarih_element):
                    logging.info(f"✅ Tarih seçildi: {tarih}")
                    time.sleep(1)
                    self._saat_sec()
                    return True
                else:
                    raise Exception("Tarih tıklanamadı")
            else:
                raise NoSuchElementException(f"Tarih bulunamadı: {tarih}")
            
        except NoSuchElementException:
            logging.warning(f"⚠️ Belirtilen tarih müsait değil: {tarih}")
            # Otomatik olarak en yakın müsait tarihi seç
            logging.info("En yakın müsait tarih aranıyor...")
            self._musait_tarih_sec()
            
    def _saat_sec(self):
        """Müsait saat slotu seç"""
        try:
            # Saat slotlarını bul - birden fazla strateji
            time_slot_strategies = [
                (By.CLASS_NAME, "time-slot"),
                (By.XPATH, "//div[contains(@class, 'time-slot')]"),
                (By.XPATH, "//button[contains(@class, 'time')]"),
                (By.XPATH, "//div[contains(@class, 'slot')]"),
                (By.XPATH, "//button[contains(@class, 'slot')]")
            ]
            
            time_slots = []
            for by, selector in time_slot_strategies:
                try:
                    slots = self.driver.find_elements(by, selector)
                    if slots:
                        time_slots = slots
                        break
                except:
                    continue
            
            if not time_slots:
                logging.info("Saat seçimi gerekmiyor veya bulunamadı")
                return
            
            # Müsait slotu bul ve seç
            for slot in time_slots:
                try:
                    class_attr = slot.get_attribute("class") or ""
                    if "available" in class_attr.lower() or "free" in class_attr.lower():
                        if "disabled" not in class_attr.lower():
                            if self._safe_click(slot):
                                logging.info(f"✅ Saat seçildi: {slot.text}")
                                time.sleep(0.5)
                                return
                except:
                    continue
            
            # Eğer available class'ı yoksa, disabled olmayan ilk slotu seç
            for slot in time_slots:
                try:
                    class_attr = slot.get_attribute("class") or ""
                    if "disabled" not in class_attr.lower():
                        if self._safe_click(slot):
                            logging.info(f"✅ Saat seçildi: {slot.text}")
                            time.sleep(0.5)
                            return
                except:
                    continue
                    
            logging.warning("Müsait saat slotu bulunamadı")
                    
        except Exception as e:
            logging.warning(f"⚠️ Saat seçimi yapılamadı: {str(e)}")
            
    def _checkboxlari_isaretle(self):
        """Gerekli checkboxları işaretle"""
        try:
            # Gerçek checkbox ID'leri: fieldname3_1 ve fieldname6_1
            checkbox_strategies = [
                (By.ID, "fieldname3_1"),  # İlk checkbox
                (By.ID, "fieldname6_1"),  # İkinci checkbox
                (By.XPATH, "//input[@type='checkbox'][contains(@name, 'accettazione') or contains(@name, 'terms')]"),
                (By.XPATH, "//input[@type='checkbox'][contains(@name, 'trattamento') or contains(@name, 'privacy')]"),
            ]
            
            # İlk checkbox (fieldname3_1)
            try:
                checkbox1 = self.driver.find_element(By.ID, "fieldname3_1")
                if not checkbox1.is_selected():
                    if self._safe_click(checkbox1):
                        logging.info("✅ İlk checkbox işaretlendi (fieldname3_1)")
                        time.sleep(0.3)
            except:
                logging.warning("İlk checkbox (fieldname3_1) bulunamadı")
            
            # İkinci checkbox (fieldname6_1)
            try:
                checkbox2 = self.driver.find_element(By.ID, "fieldname6_1")
                if not checkbox2.is_selected():
                    if self._safe_click(checkbox2):
                        logging.info("✅ İkinci checkbox işaretlendi (fieldname6_1)")
                        time.sleep(0.3)
            except:
                logging.warning("İkinci checkbox (fieldname6_1) bulunamadı")
            
            # Yedek strateji: Tüm checkboxları bul ve işaretle
            all_checkboxes = self.driver.find_elements(By.XPATH, "//input[@type='checkbox' and @class='field required']")
            for checkbox in all_checkboxes:
                try:
                    if not checkbox.is_selected():
                        if self._safe_click(checkbox):
                            logging.info(f"✅ Checkbox işaretlendi: {checkbox.get_attribute('id') or checkbox.get_attribute('name')}")
                            time.sleep(0.3)
                except:
                    continue
                
        except Exception as e:
            logging.warning(f"⚠️ Checkbox işaretleme hatası: {str(e)}")
            
    def _rezervasyonu_gonder(self):
        """Rezervasyon formunu gönder"""
        try:
            # Submit butonunu bul - birden fazla strateji
            submit_strategies = [
                (By.XPATH, "//button[contains(text(), 'Prenota posto') or contains(text(), 'Prenota')]"),
                (By.XPATH, "//button[contains(text(), 'Conferma') or contains(text(), 'conferma')]"),
                (By.XPATH, "//button[@type='submit']"),
                (By.XPATH, "//input[@type='submit']"),
                (By.XPATH, "//button[contains(@class, 'submit') or contains(@class, 'prenota')]"),
                (By.ID, "submit"),
                (By.NAME, "submit")
            ]
            
            submit_button = self._find_element_multiple_strategies(submit_strategies)
            
            # Butona scroll et
            self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
            time.sleep(0.5)
            
            # Butona tıkla
            if self._safe_click(submit_button):
                logging.info("✅ Rezervasyon gönderildi")
            else:
                # JavaScript ile dene
                self.driver.execute_script("arguments[0].click();", submit_button)
                logging.info("✅ Rezervasyon gönderildi (JavaScript)")
            
            # Sonuç sayfasının yüklenmesini bekle
            self._wait_for_page_load()
            time.sleep(2)
            
        except Exception as e:
            logging.error(f"❌ Form gönderme hatası: {str(e)}")
            self._take_screenshot()
            raise
            
    def _rezervasyon_basarili_mi(self):
        """Rezervasyonun başarılı olup olmadığını kontrol et"""
        try:
            # Sayfa kaynağını kontrol et
            page_source_lower = self.driver.page_source.lower()
            
            # Başarı kelimeleri
            success_keywords = [
                'confermata', 'confermato', 'successo', 'successful', 
                'prenotazione confermata', 'prenotato', 'completata',
                'completato', 'riuscita', 'riuscito'
            ]
            
            # Hata kelimeleri
            error_keywords = [
                'errore', 'error', 'fallito', 'failed', 'impossibile',
                'non disponibile', 'non disponibile', 'rifiutato'
            ]
            
            # Hata kontrolü
            for keyword in error_keywords:
                if keyword in page_source_lower:
                    logging.warning(f"❌ Hata mesajı bulundu: {keyword}")
                    return False
            
            # Başarı mesajını kontrol et - birden fazla strateji
            success_xpaths = [
                "//div[contains(@class, 'success')]",
                "//div[contains(@class, 'alert-success')]",
                "//div[contains(@class, 'alert') and contains(@class, 'success')]",
                "//div[contains(text(), 'confermata')]",
                "//div[contains(text(), 'successo')]",
                "//div[contains(text(), 'prenotazione confermata')]",
                "//p[contains(text(), 'confermata')]",
                "//span[contains(text(), 'confermata')]",
                "//*[contains(text(), 'prenotazione confermata')]"
            ]
            
            for xpath in success_xpaths:
                try:
                    element = self.driver.find_element(By.XPATH, xpath)
                    if element and element.is_displayed():
                        logging.info(f"✅ Başarı mesajı bulundu: {element.text[:50]}")
                        return True
                except:
                    continue
            
            # Sayfa kaynağında başarı kelimelerini kontrol et
            for keyword in success_keywords:
                if keyword in page_source_lower:
                    logging.info(f"✅ Başarı kelimesi bulundu: {keyword}")
                    return True
                    
            # URL değişikliği kontrolü (bazen başarılı rezervasyon sonrası URL değişir)
            current_url = self.driver.current_url.lower()
            if 'success' in current_url or 'conferma' in current_url or 'completato' in current_url:
                logging.info("✅ URL'de başarı göstergesi bulundu")
                return True
                
            logging.warning("⚠️ Başarı mesajı bulunamadı")
            return False
            
        except Exception as e:
            logging.error(f"❌ Başarı kontrolü hatası: {str(e)}")
            return False
            
    def _bildirim_gonder(self, baslik, mesaj):
        """Masaüstü bildirimi gönder"""
        try:
            notification.notify(
                title=baslik,
                message=mesaj,
                app_icon=None,
                timeout=10
            )
        except:
            logging.info(f"Bildirim: {baslik} - {mesaj}")
            
    def surekli_deneme(self, max_deneme=50, bekleme_suresi=2):
        """
        Rezervasyon açılana kadar sürekli dene
        
        Args:
            max_deneme: Maksimum deneme sayısı
            bekleme_suresi: Denemeler arası bekleme (saniye)
        """
        logging.info(f"Sürekli deneme modu başlatıldı. Max deneme: {max_deneme}")
        
        for deneme in range(1, max_deneme + 1):
            logging.info(f"Deneme {deneme}/{max_deneme}")
            
            if self.rezervasyon_yap():
                logging.info("Rezervasyon başarılı! İşlem tamamlandı.")
                return True
                
            if deneme < max_deneme:
                logging.info(f"{bekleme_suresi} saniye bekleniyor...")
                time.sleep(bekleme_suresi)
                
        logging.warning("Maksimum deneme sayısına ulaşıldı. Rezervasyon yapılamadı.")
        return False
        
    def zamanli_rezervasyon(self, saat, dakika=0):
        """
        Belirli bir saatte rezervasyon yap
        
        Args:
            saat: Rezervasyon saati (0-23)
            dakika: Dakika (0-59)
        """
        hedef_saat = f"{saat:02d}:{dakika:02d}"
        logging.info(f"Rezervasyon saati: {hedef_saat}")
        
        schedule.every().day.at(hedef_saat).do(self.rezervasyon_yap)
        
        logging.info("Zamanlayıcı başlatıldı. Bekleniyor...")
        while True:
            schedule.run_pending()
            time.sleep(1)
    
    def _italya_saati_al(self):
        """İtalya saatini al"""
        try:
            if ZoneInfo:
                # Python 3.9+
                return datetime.now(ZoneInfo("Europe/Rome"))
            elif pytz:
                # Python 3.8 ve öncesi için pytz
                rome_tz = pytz.timezone("Europe/Rome")
                return datetime.now(rome_tz)
            else:
                # Timezone desteği yoksa UTC+1 (yaklaşık)
                return datetime.now() + timedelta(hours=1)
        except Exception as e:
            logging.warning(f"İtalya saati alınamadı, UTC+1 kullanılıyor: {str(e)}")
            return datetime.now() + timedelta(hours=1)
    
    def italya_saatine_gore_zamanli_rezervasyon(self, saatler=[(0, 0), (8, 0)]):
        """
        İtalya saatine göre belirli saatlerde rezervasyon yap
        
        Args:
            saatler: (saat, dakika) tuple'larının listesi. Varsayılan: [(0, 0), (8, 0)]
        """
        logging.info("="*60)
        logging.info("İTALYA SAATİNE GÖRE ZAMANLANMIŞ REZERVASYON")
        logging.info("="*60)
        
        # İtalya saatini göster
        italya_saati = self._italya_saati_al()
        logging.info(f"Şu anki İtalya saati: {italya_saati.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Her saat için zamanlayıcı bilgisi
        for saat, dakika in saatler:
            hedef_saat = f"{saat:02d}:{dakika:02d}"
            logging.info(f"✅ Zamanlayıcı eklendi: Her gün {hedef_saat} (İtalya saati)")
        
        logging.info("="*60)
        logging.info("Zamanlayıcılar aktif. Bot çalışmaya devam ediyor...")
        logging.info("Durdurmak için Ctrl+C basın")
        logging.info("="*60)
        
        # Son çalıştırma zamanlarını takip et (aynı dakikada iki kez çalışmasın)
        son_calistirma = {}
        
        try:
            while True:
                italya_saati = self._italya_saati_al()
                su_an = (italya_saati.hour, italya_saati.minute)
                
                # Her zamanlanmış saat için kontrol et
                for saat, dakika in saatler:
                    if su_an == (saat, dakika):
                        # Aynı dakikada tekrar çalışmasın
                        anahtar = f"{saat:02d}:{dakika:02d}"
                        if anahtar not in son_calistirma or son_calistirma[anahtar] != su_an:
                            logging.info(f"⏰ İtalya saati {saat:02d}:{dakika:02d} - Rezervasyon başlatılıyor...")
                            son_calistirma[anahtar] = su_an
                            try:
                                self.rezervasyon_yap()
                            except Exception as e:
                                logging.error(f"Rezervasyon hatası: {str(e)}")
                
                # Her dakika kontrol et
                time.sleep(60)
                
        except KeyboardInterrupt:
            logging.info("\n⏹️ Zamanlayıcı durduruldu.")


def main():
    """Ana fonksiyon"""
    
    # Kullanıcı ayarları
    config = {
        'nome_cognome': 'Ali Erkan Ocaklı',
        'email': 'alierkn.ocakli@gmail.com',
        'matricola': '555012',
        'sala_tipo': 'Sala Lettura -Rettorato',  # Dropdown'dan seçilecek salon tipi (kısmi eşleşme yapılır)
        'headless': False  # True yaparak arka planda çalıştırabilirsiniz
    }
    
    # Bot oluştur
    bot = UniMeKutuphaneBot(config)
    
    print("""
    ╔════════════════════════════════════════════════╗
    ║     UniMe Kütüphane Rezervasyon Botu v1.0     ║
    ╠════════════════════════════════════════════════╣
    ║  1. Hemen rezervasyon yap                     ║
    ║  2. Sürekli deneme modu (slot açılana kadar)  ║
    ║  3. İtalya saatine göre zamanlanmış (00:00 & 08:00) ║
    ║  4. Özel tarih için rezervasyon               ║
    ║  5. Çıkış                                      ║
    ╚════════════════════════════════════════════════╝
    """)
    
    secim = input("Seçiminiz (1-5): ")
    
    if secim == "1":
        # Hemen rezervasyon yap
        bot.rezervasyon_yap()
        
    elif secim == "2":
        # Sürekli deneme modu
        max_deneme = int(input("Maksimum deneme sayısı (örn: 100): "))
        bekleme = int(input("Denemeler arası bekleme süresi (saniye): "))
        bot.surekli_deneme(max_deneme, bekleme)
        
    elif secim == "3":
        # İtalya saatine göre zamanlanmış rezervasyon (00:00 ve 08:00)
        print("\n🇮🇹 İtalya saatine göre zamanlanmış rezervasyon başlatılıyor...")
        print("Her gün 00:00 ve 08:00'da (İtalya saati) otomatik rezervasyon yapılacak.")
        print("Durdurmak için Ctrl+C basın.\n")
        bot.italya_saatine_gore_zamanli_rezervasyon(saatler=[(0, 0), (8, 0)])
        
    elif secim == "4":
        # Özel tarih
        tarih = input("Tarih (YYYY-MM-DD formatında): ")
        bot.rezervasyon_yap(tarih=tarih, otomatik_tarih=False)
        
    elif secim == "5":
        print("Çıkılıyor...")
        return
        
    else:
        print("Geçersiz seçim!")


if __name__ == "__main__":
    main()
