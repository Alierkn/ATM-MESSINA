"""
ATM Messina Otobüs Durakları Takip Sistemi
Durak URL'lerinden veri çekerek gelecek otobüsleri gösterir
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import datetime
import time
from typing import Dict, List, Optional

app = Flask(__name__)
# CORS ekle - mobil ve farklı domain'lerden erişim için
CORS(app)

# Error handler'lar - API endpoint'leri için JSON döndür
@app.errorhandler(404)
def not_found(error):
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': 'Endpoint bulunamadı'}), 404
    return error

@app.errorhandler(500)
def internal_error(error):
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': 'Sunucu hatası'}), 500
    return error

@app.errorhandler(Exception)
def handle_exception(e):
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': str(e)}), 500
    return e

# Retry stratejisi ile session oluştur
def create_session():
    """Retry mekanizmalı HTTP session oluştur"""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

# Durak URL'lerini saklayacak dosya
# Cloud deploy için persistent storage kullan
DURAKLAR_FILE = os.path.join(os.path.dirname(__file__), 'data', 'duraklar.json')

# data klasörünü oluştur
os.makedirs(os.path.dirname(DURAKLAR_FILE), exist_ok=True)

def load_duraklar() -> List[Dict]:
    """Durak listesini yükle"""
    if os.path.exists(DURAKLAR_FILE):
        try:
            with open(DURAKLAR_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_duraklar(duraklar: List[Dict]):
    """Durak listesini kaydet"""
    os.makedirs(os.path.dirname(DURAKLAR_FILE), exist_ok=True)
    with open(DURAKLAR_FILE, 'w', encoding='utf-8') as f:
        json.dump(duraklar, f, ensure_ascii=False, indent=2)

def fetch_durak_data(url: str) -> Dict:
    """
    ATM Messina durağından otobüs bilgilerini çek
    
    URL formatı: https://www.atmmessinaspa.it/smartpoles2.php?palina=1766&rnd=7
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        
        # Retry mekanizmalı session kullan
        session = create_session()
        
        # Timeout'u artır (30 saniye)
        try:
            response = session.get(url, headers=headers, timeout=(10, 30))  # (connect timeout, read timeout)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            # Timeout durumunda daha fazla bekle ve tekrar dene
            time.sleep(3)
            response = session.get(url, headers=headers, timeout=(15, 45))
            response.raise_for_status()
        
        # Encoding'i düzelt
        response.encoding = response.apparent_encoding or 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')
        
        otobusler = []
        durak_adi = 'Bilinmeyen Durak'
        
        # Durak adını bul - daha esnek yöntem
        # Önce tüm metni al ve FERMATA içeren kısmı bul
        page_text = soup.get_text()
        fermata_match = re.search(r'FERMATA[^•]*•[^*]*\*\*_?([^*]+?)_?\*\*', page_text, re.IGNORECASE)
        if fermata_match:
            durak_adi = fermata_match.group(1).replace('_', '').strip()
        else:
            # Alternatif: başlık elementlerinde ara
            title_elements = soup.find_all(['h1', 'h2', 'h3', 'p', 'div', 'b', 'strong'])
            for elem in title_elements:
                text = elem.get_text()
                if 'FERMATA' in text.upper():
                    # ** ile çevrili kısmı bul
                    match = re.search(r'\*\*_?([^*]+?)_?\*\*', text)
                    if match:
                        durak_adi = match.group(1).replace('_', '').strip()
                        break
        
        # Tüm tabloları bul
        tables = soup.find_all('table')
        
        # Eğer tablo yoksa, tüm HTML'i text olarak parse et
        if not tables or len(tables) == 0:
            # Direkt metinden parse et
            page_text = soup.get_text()
            # Pattern: **32** **Staz. Centrale** **18:05** formatını bul
            pattern = r'\*\*(\d+[A-Z\s]*)\*\*\s*\*\*([^*]+?)\*\*\s*\*\*(\d{1,2}):(\d{1,2})\*\*'
            matches = re.finditer(pattern, page_text, re.IGNORECASE)
            for match in matches:
                hour = match.group(3).zfill(2)
                minute = match.group(4).zfill(2)
                otobus = {
                    'hat': match.group(1).strip(),
                    'varis': match.group(2).strip(),
                    'saat': f"{hour}:{minute}",
                    'tip': 'Schedulato'
                }
                if not any(o['hat'] == otobus['hat'] and o['saat'] == otobus['saat'] for o in otobusler):
                    otobusler.append(otobus)
        
        # Tablolardan TÜM otobüs bilgilerini çek (geçmiş/gelecek ayrımı yapmadan)
        # Her otobüs için ayrı bir tablo var
        # Format: | Linea | Destinazione | Orario |
        # İkinci satır: _(Orario Schedulato)_ veya _(Orario aggiornato in Tempo Reale ...)_
        
        for table in tables:
            try:
                # Tablo içeriğini al
                table_html = str(table)
                table_text = table.get_text()
                
                # Önce regex ile direkt tablo HTML'inden çek
                # Pattern: <td> veya <th> içinde **32** **Staz. Centrale** **18:05** formatı
                pattern = r'<t[dh][^>]*>\s*\*\*(\d+[A-Z\s]*)\*\*\s*</t[dh]>\s*<t[dh][^>]*>\s*\*\*([^*]+?)\*\*\s*</t[dh]>\s*<t[dh][^>]*>\s*\*\*(\d{1,2}):(\d{1,2})\*\*\s*</t[dh]'
                matches = re.finditer(pattern, table_html, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    hour = match.group(3).zfill(2)
                    minute = match.group(4).zfill(2)
                    otobus = {
                        'hat': match.group(1).strip(),
                        'varis': match.group(2).strip(),
                        'saat': f"{hour}:{minute}",
                        'tip': 'Schedulato'
                    }
                    # Tip bilgisini kontrol et
                    if 'tempo reale' in table_text.lower() or 'aggiornato' in table_text.lower():
                        otobus['tip'] = 'Tempo Reale'
                    if not any(o['hat'] == otobus['hat'] and o['saat'] == otobus['saat'] for o in otobusler):
                        otobusler.append(otobus)
                
                # Tablo hücrelerini manuel parse et (hem ** işaretli hem de düz metin formatı için)
                rows = table.find_all('tr')
                
                # Başlık satırını atla (Linea, Destinazione, Orario içeren)
                data_rows = []
                for row in rows:
                    row_text = row.get_text(strip=True).lower()
                    # Başlık satırı değilse ve veri içeriyorsa ekle
                    if 'linea' not in row_text or len(row.find_all(['td', 'th'])) > 0:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 2:  # En az 2 hücre varsa veri satırı olabilir
                            data_rows.append(row)
                
                # Her veri satırını işle
                for row in data_rows:
                    try:
                        cells = row.find_all(['td', 'th'])
                        cell_texts = [cell.get_text(strip=True) for cell in cells]
                        
                        # Başlık satırını atla
                        if any(text.lower() in ['linea', 'destinazione', 'orario'] for text in cell_texts):
                            continue
                        
                        linea = ''
                        destinazione = ''
                        orario = ''
                        tip = 'Schedulato'
                        
                        # Hücreleri analiz et
                        for i, text in enumerate(cell_texts):
                            # Temizle (** işaretlerini kaldır)
                            clean_text = re.sub(r'\*+', '', text).strip()
                            
                            # Linea: Sadece sayı veya sayı + harf (örn: "1", "31 BIS")
                            if re.match(r'^\d+[A-Z\s]*$', clean_text) and not linea:
                                linea = clean_text
                                continue
                            
                            # Saat: HH:MM formatı
                            time_match = re.search(r'(\d{1,2}):(\d{1,2})', clean_text)
                            if time_match and not orario:
                                hour = time_match.group(1).zfill(2)
                                minute = time_match.group(2).zfill(2)
                                orario = f"{hour}:{minute}"
                                continue
                            
                            # Destinazione: Uzun metin (Linea ve Orario değilse)
                            if clean_text and len(clean_text) > 2 and not destinazione:
                                if clean_text not in ['Linea', 'Destinazione', 'Orario']:
                                    if not re.match(r'^\d+[A-Z\s]*$', clean_text):
                                        if not re.match(r'^\d{1,2}:\d{2}', clean_text):
                                            destinazione = clean_text
                        
                        # Tip bilgisini kontrol et (aynı satırda veya sonraki satırda)
                        row_text_lower = row.get_text(strip=True).lower()
                        if 'tempo reale' in row_text_lower or 'aggiornato' in row_text_lower:
                            tip = 'Tempo Reale'
                        
                        # Sonraki satırı da kontrol et (tip bilgisi orada olabilir)
                        row_index = rows.index(row) if row in rows else -1
                        if row_index >= 0 and row_index + 1 < len(rows):
                            next_row_text = rows[row_index + 1].get_text(strip=True).lower()
                            if 'tempo reale' in next_row_text or 'aggiornato' in next_row_text:
                                tip = 'Tempo Reale'
                        
                        # Eğer hala bulamadıysak, tablo metninden regex ile ara
                        if not orario:
                            time_matches = re.findall(r'(\d{1,2}):(\d{1,2})', table_text)
                            if time_matches:
                                hour, minute = time_matches[0]
                                orario = f"{hour.zfill(2)}:{minute.zfill(2)}"
                        
                        if not linea:
                            # Tablo metninden sayı ile başlayan metni bul
                            linea_match = re.search(r'\b(\d+[A-Z\s]*)\b', table_text)
                            if linea_match:
                                potential_linea = linea_match.group(1).strip()
                                if not re.match(r'^\d{1,2}:\d{2}', potential_linea):
                                    linea = potential_linea
                        
                        # Otobüsü ekle (Linea ve Orario varsa)
                        if linea and orario:
                            otobus = {
                                'hat': linea,
                                'varis': destinazione if destinazione else 'Bilinmiyor',
                                'saat': orario,
                                'tip': tip
                            }
                            if not any(o['hat'] == otobus['hat'] and o['saat'] == otobus['saat'] for o in otobusler):
                                otobusler.append(otobus)
                    except Exception as e:
                        # Bu satırı atla
                        continue
            except Exception as e:
                # Bu tabloyu atla, diğerlerine devam et
                continue
        
        # Eğer hala otobüs bulunamadıysa, tüm sayfadan regex ile ara
        if not otobusler:
            # Tüm HTML'i text olarak al
            page_html = str(soup)
            page_text = soup.get_text()
            
            # Pattern 1: **32** **Staz. Centrale** **18:05** formatı (HTML içinde)
            pattern1 = r'\*\*(\d+[A-Z\s]*)\*\*\s*\*\*([^*]+?)\*\*\s*\*\*(\d{1,2}):(\d{1,2})\*\*'
            matches1 = re.finditer(pattern1, page_html, re.IGNORECASE | re.DOTALL)
            for match in matches1:
                hour = match.group(3).zfill(2)
                minute = match.group(4).zfill(2)
                otobus = {
                    'hat': match.group(1).strip(),
                    'varis': match.group(2).strip(),
                    'saat': f"{hour}:{minute}",
                    'tip': 'Schedulato'
                }
                # Tip kontrolü - eğer bu otobüsün yakınında "tempo reale" varsa
                match_start = match.start()
                context = page_html[max(0, match_start-200):match_start+200].lower()
                if 'tempo reale' in context or 'aggiornato' in context:
                    otobus['tip'] = 'Tempo Reale'
                if not any(o['hat'] == otobus['hat'] and o['saat'] == otobus['saat'] for o in otobusler):
                    otobusler.append(otobus)
            
            # Pattern 2: Sadece text'ten (eğer HTML pattern çalışmadıysa)
            if not otobusler:
                matches2 = re.finditer(pattern1, page_text, re.IGNORECASE)
                for match in matches2:
                    hour = match.group(3).zfill(2)
                    minute = match.group(4).zfill(2)
                    otobus = {
                        'hat': match.group(1).strip(),
                        'varis': match.group(2).strip(),
                        'saat': f"{hour}:{minute}",
                        'tip': 'Schedulato'
                    }
                    if not any(o['hat'] == otobus['hat'] and o['saat'] == otobus['saat'] for o in otobusler):
                        otobusler.append(otobus)
            
            # Pattern 3: Tüm ** ile çevrili metinleri bul ve grupla
            if not otobusler:
                bold_matches = re.findall(r'\*\*([^*]+)\*\*', page_text)
                i = 0
                while i < len(bold_matches) - 2:
                    # Linea, Destinazione, Orario sırası
                    if re.match(r'^\d+[A-Z\s]*$', bold_matches[i].strip()):
                        linea = bold_matches[i].strip()
                        destinazione = bold_matches[i+1].strip() if i+1 < len(bold_matches) else 'Bilinmiyor'
                        orario_text = bold_matches[i+2].strip() if i+2 < len(bold_matches) else ''
                        time_match = re.search(r'(\d{1,2}):(\d{1,2})', orario_text)
                        if time_match:
                            hour = time_match.group(1).zfill(2)
                            minute = time_match.group(2).zfill(2)
                            otobus = {
                                'hat': linea,
                                'varis': destinazione,
                                'saat': f"{hour}:{minute}",
                                'tip': 'Schedulato'
                            }
                            if not any(o['hat'] == otobus['hat'] and o['saat'] == otobus['saat'] for o in otobusler):
                                otobusler.append(otobus)
                        i += 3
                    else:
                        i += 1
        
        # TÜM otobüsleri göster - hiçbir filtreleme yapma
        # Sayfada ne varsa hepsini göster (geçmiş/gelecek ayrımı yapmadan)
        # Sadece saate göre sırala
        otobusler.sort(key=lambda x: x['saat'])
        
        return {
            'success': True,
            'otobusler': otobusler,
            'durak_adi': durak_adi,
            'durak_id': None,  # URL'den çıkarılabilir
            'timestamp': datetime.now().isoformat()
        }
        
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f'Bağlantı hatası: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Hata: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }

@app.route('/')
def index():
    """Ana sayfa"""
    return render_template('atm_messina.html')

@app.route('/health')
@app.route('/ping')
def health_check():
    """Health check endpoint - Uptime monitoring için"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'service': 'ATM Messina Bot'
    }), 200

@app.route('/api/duraklar', methods=['GET'])
def get_duraklar():
    """Tüm durakları getir"""
    try:
        duraklar = load_duraklar()
        return jsonify(duraklar)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'duraklar': []}), 500

@app.route('/api/duraklar', methods=['POST'])
def add_durak():
    """Yeni durak ekle"""
    try:
        data = request.get_json() or {}
        
        if not data.get('ad') or not data.get('url'):
            return jsonify({'success': False, 'error': 'Durak adı ve URL gerekli'}), 400
        
        duraklar = load_duraklar()
        
        yeni_durak = {
            'id': len(duraklar) + 1,
            'ad': data.get('ad', 'İsimsiz Durak'),
            'url': data.get('url', ''),
            'eklenme_tarihi': datetime.now().isoformat()
        }
        
        duraklar.append(yeni_durak)
        save_duraklar(duraklar)
        
        return jsonify(yeni_durak), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/duraklar/<int:durak_id>', methods=['DELETE'])
def delete_durak(durak_id):
    """Durak sil"""
    try:
        duraklar = load_duraklar()
        duraklar = [d for d in duraklar if d.get('id') != durak_id]
        save_duraklar(duraklar)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/duraklar/<int:durak_id>/veri', methods=['GET'])
def get_durak_veri(durak_id):
    """Belirli bir durağın verisini çek"""
    try:
        duraklar = load_duraklar()
        durak = next((d for d in duraklar if d.get('id') == durak_id), None)
        
        if not durak:
            return jsonify({'success': False, 'error': 'Durak bulunamadı'}), 404
        
        url = durak.get('url')
        if not url:
            return jsonify({'success': False, 'error': 'Durak URL\'si yok'}), 400
        
        veri = fetch_durak_data(url)
        veri['durak_adi'] = durak.get('ad', 'Bilinmeyen')
        veri['durak_id'] = durak_id
        
        return jsonify(veri)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/duraklar/tum-veriler', methods=['GET'])
def get_tum_veriler():
    """Tüm durakların verilerini çek"""
    try:
        duraklar = load_duraklar()
        sonuclar = []
        
        for durak in duraklar:
            url = durak.get('url')
            if url:
                try:
                    veri = fetch_durak_data(url)
                    veri['durak_adi'] = durak.get('ad', 'Bilinmeyen')
                    veri['durak_id'] = durak.get('id')
                    sonuclar.append(veri)
                    time.sleep(0.5)  # Rate limiting
                except Exception as e:
                    # Bir durakta hata olsa bile diğerlerini çekmeye devam et
                    sonuclar.append({
                        'success': False,
                        'durak_adi': durak.get('ad', 'Bilinmeyen'),
                        'durak_id': durak.get('id'),
                        'error': str(e)
                    })
        
        return jsonify(sonuclar)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/debug/<int:durak_id>', methods=['GET'])
def debug_durak(durak_id):
    """Debug: Durak HTML'ini göster"""
    duraklar = load_duraklar()
    durak = next((d for d in duraklar if d.get('id') == durak_id), None)
    
    if not durak:
        return jsonify({'error': 'Durak bulunamadı'}), 404
    
    url = durak.get('url')
    if not url:
        return jsonify({'error': 'Durak URL\'si yok'}), 400
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        session = create_session()
        try:
            response = session.get(url, headers=headers, timeout=(10, 30))
            response.raise_for_status()
        except requests.exceptions.Timeout:
            time.sleep(3)
            response = session.get(url, headers=headers, timeout=(15, 45))
            response.raise_for_status()
        response.encoding = response.apparent_encoding or 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')
        
        return jsonify({
            'url': url,
            'html_preview': str(soup)[:5000],  # İlk 5000 karakter
            'text_preview': soup.get_text()[:2000],  # İlk 2000 karakter
            'tables_count': len(soup.find_all('table')),
            'parsed_data': fetch_durak_data(url)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Örnek duraklar dosyası oluştur (eğer yoksa)
    if not os.path.exists(DURAKLAR_FILE):
        ornek_duraklar = [
            {
                'id': 1,
                'ad': 'Örnek Durak 1',
                'url': 'https://example.com/durak1',
                'eklenme_tarihi': datetime.now().isoformat()
            }
        ]
        save_duraklar(ornek_duraklar)
    
    # Port'u environment variable'dan al (cloud deploy için)
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print("=" * 60)
    print("🚌 ATM Messina Otobüs Takip Sistemi")
    print("=" * 60)
    print(f"🌐 Uygulama başlatılıyor: http://0.0.0.0:{port}")
    print(f"📁 Duraklar dosyası: {DURAKLAR_FILE}")
    print("=" * 60)
    
    app.run(debug=debug, host='0.0.0.0', port=port)

