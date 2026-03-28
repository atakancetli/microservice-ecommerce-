#!/bin/bash
# Network Isolation Doğrulama Testi
# Bu betik mikroservislere dışarıdan doğrudan erişilemediğini, 
# sadece Dispatcher üzerinden erişilebildiğini doğrular.

echo "🔍 Network Isolation Kontrolü Başlıyor..."

# 1. Dispatcher Kontrol (Beklenen: 200)
echo -n "1. Dispatcher (Port 8080): "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health)
if [ "$STATUS" == "200" ]; then
    echo "✅ OK ($STATUS)"
else
    echo "❌ HATA ($STATUS)"
fi

# 2. Auth Service Doğrudan Erişim (Beklenen: Hata/Timeout)
echo -n "2. Auth Service (Port 8001): "
STATUS=$(curl -s --connect-timeout 2 -o /dev/null -w "%{http_code}" http://localhost:8001/health)
if [ "$STATUS" == "000" ]; then
    echo "✅ İZOLE EDİLDİ (Erişim Yok)"
else
    echo "❌ GÜVENLİK AÇIĞI (Erişim Var: $STATUS)"
fi

# 3. Product Service Doğrudan Erişim (Beklenen: Hata/Timeout)
echo -n "3. Product Service (Port 8002): "
STATUS=$(curl -s --connect-timeout 2 -o /dev/null -w "%{http_code}" http://localhost:8002/health)
if [ "$STATUS" == "000" ]; then
    echo "✅ İZOLE EDİLDİ (Erişim Yok)"
else
    echo "❌ GÜVENLİK AÇIĞI (Erişim Var: $STATUS)"
fi

# 4. Order Service Doğrudan Erişim (Beklenen: Hata/Timeout)
echo -n "4. Order Service (Port 8003): "
STATUS=$(curl -s --connect-timeout 2 -o /dev/null -w "%{http_code}" http://localhost:8002/health)
if [ "$STATUS" == "000" ]; then
    echo "✅ İZOLE EDİLDİ (Erişim Yok)"
else
    echo "❌ GÜVENLİK AÇIĞI (Erişim Var: $STATUS)"
fi

echo "🏁 Test Tamamlandı."
