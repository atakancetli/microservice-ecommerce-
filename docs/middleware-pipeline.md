# Dispatcher Middleware Pipeline

Bu belge, API Gateway'in istek işleme akışını (middleware pipeline) detaylı olarak açıklar.

## Pipeline Sırası

```
Client Request
    │
    ▼
┌──────────────────────┐
│ 1. RequestIdMiddleware│  ← UUID v4 ataması
│    X-Request-ID      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ 2. CORS Middleware   │  ← Cross-Origin kontrolü
│    Access-Control-*  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ 3. PrometheusMiddle  │  ← Metrik toplama
│    Counter/Histogram │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ 4. Rate Limiter      │  ← 429 Too Many Requests
│    Sliding Window    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ 5. Route Resolution  │  ← URL → Service mapping
│    /api/products →   │
│    product-service   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ 6. Auth Middleware   │  ← JWT doğrulama
│    Bearer token →    │
│    X-User-Id header  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ 7. Proxy Forward     │  ← httpx ile downstream
│    + Circuit Breaker │
│    + Retry (backoff) │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ 8. Logger            │  ← İstek/yanıt logu
│    method, path,     │
│    status, duration  │
└──────────┬───────────┘
           │
           ▼
     HTTP Response
```

## Middleware Konfigürasyonu

| Middleware | Dosya | Durum |
|-----------|-------|-------|
| Request ID | `middleware/request_id.py` | ✅ Aktif |
| CORS | `middleware/cors.py` | ✅ Aktif |
| Prometheus | `middleware/prometheus_metrics.py` | ✅ Aktif |
| Error Handler | `middleware/error_handler.py` | ✅ Aktif |
| Metrics (legacy) | `middleware/metrics.py` | ⬜ Deprecated |

## Rate Limiter Detayları

- **Algoritma:** Sliding Window
- **Pencere:** 60 saniye
- **Limit:** 100 istek / istemci / dakika
- **Yanıt:** 429 + `X-RateLimit-Remaining` header

## Circuit Breaker Detayları

- **Durumlar:** CLOSED → OPEN → HALF_OPEN → CLOSED
- **Açılma eşiği:** 5 ardışık hata
- **Recovery timeout:** 30 saniye
- **Success threshold (HALF_OPEN):** 2 başarılı istek
