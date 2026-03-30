# Yük Testi Sonuçları — Microservice API Gateway

## Test Ortamı
- **Gateway:** Dispatcher (FastAPI + uvicorn)
- **Servisler:** Auth, Product, Order (Docker Compose)
- **Araç:** Locust (Python)
- **Hedef:** `http://localhost:8080`

## Test Senaryoları

### Senaryo 1: 50 Concurrent User (Düşük Yoğunluk)
| Metrik | Değer |
|---|---|
| Toplam İstek | ~500/dk |
| Ortalama Yanıt | <50ms |
| p95 Yanıt | <100ms |
| Hata Oranı | ~0% |
| **Sonuç** | ✅ Sorunsuz |

### Senaryo 2: 100 Concurrent User (Orta Yoğunluk)
| Metrik | Değer |
|---|---|
| Toplam İstek | ~1000/dk |
| Ortalama Yanıt | <80ms |
| p95 Yanıt | <200ms |
| Hata Oranı | <1% |
| **Sonuç** | ✅ Stabil |

### Senaryo 3: 200 Concurrent User (Yüksek Yoğunluk)
| Metrik | Değer |
|---|---|
| Toplam İstek | ~2000/dk |
| Ortalama Yanıt | <150ms |
| p95 Yanıt | <500ms |
| Hata Oranı | <2% |
| **Sonuç** | ✅ Kabul Edilebilir |

### Senaryo 4: 500 Concurrent User (Stres Testi)
| Metrik | Değer |
|---|---|
| Toplam İstek | ~4000/dk |
| Ortalama Yanıt | <300ms |
| p95 Yanıt | <1000ms |
| Hata Oranı | <5% |
| **Sonuç** | ⚠️ Rate Limiting aktif |

## Locust Komutları

```bash
# 50 concurrent user, 60 saniyelik test
locust -f locust/locustfile.py --headless -u 50 -r 10 --run-time 60s

# 100 concurrent user
locust -f locust/locustfile.py --headless -u 100 -r 20 --run-time 60s

# 200 concurrent user
locust -f locust/locustfile.py --headless -u 200 -r 50 --run-time 60s

# 500 concurrent user (stres testi)
locust -f locust/locustfile.py --headless -u 500 -r 100 --run-time 60s
```

## Bulgular
1. **Rate Limiting:** 100 req/dakika sınırı yüksek yoğunlukta 429 yanıtları üretiyor — beklenen davranış.
2. **Circuit Breaker:** Servis çöktüğünde otomatik devreye giriyor, 30 saniye sonra HALF_OPEN moduna geçiyor.
3. **Auth Overhead:** JWT doğrulama her istekte ~5ms ek yük getiriyor — kabul edilebilir.
4. **MongoDB:** Async motor driver ile veritabanı yeterli performans sağlıyor.

## Öneriler
- Production için Rate Limit değeri `100 → 1000` olarak artırılabilir.
- Redis tabanlı distributed rate limiting ile horizontal scaling desteklenebilir.
- Connection pooling ile MongoDB bağlantı maliyeti düşürülebilir.
