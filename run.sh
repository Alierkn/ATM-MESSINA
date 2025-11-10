#!/bin/bash

# UniMe Kütüphane Botu Çalıştırma Scripti

cd "$(dirname "$0")"

# Virtual environment kontrolü
if [ ! -d "venv" ]; then
    echo "Virtual environment bulunamadı. Oluşturuluyor..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Botu çalıştır
python unime_library_bot.py

