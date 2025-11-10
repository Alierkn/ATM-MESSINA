#!/bin/bash

# Bot Durdurma Scripti

echo "🛑 Bot durduruluyor..."

# Process ID'yi bul
PID=$(ps aux | grep "python.*unime_library_bot" | grep -v grep | awk '{print $2}')

if [ -z "$PID" ]; then
    echo "❌ Bot çalışmıyor."
    exit 0
fi

echo "📋 Bulunan Process ID: $PID"

# Önce normal şekilde durdurmayı dene
kill $PID 2>/dev/null

# 5 saniye bekle
sleep 5

# Hala çalışıyorsa zorla durdur
if ps -p $PID > /dev/null 2>&1; then
    echo "⚠️ Bot hala çalışıyor, zorla durduruluyor..."
    kill -9 $PID 2>/dev/null
    sleep 1
fi

# Tekrar kontrol et
if ps -p $PID > /dev/null 2>&1; then
    echo "❌ Bot durdurulamadı. Manuel olarak kontrol edin."
    exit 1
else
    echo "✅ Bot başarıyla durduruldu."
    exit 0
fi

