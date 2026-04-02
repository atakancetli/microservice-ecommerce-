# Proje Geliştirme Süreci

## Sprint Planı (10 Gün)

| Gün | Tarih | Konular | Durum |
|-----|-------|---------|-------|
| 1 | 23 Mart | Proje iskeleti, Docker Compose, Network isolation | ✅ |
| 2 | 24 Mart | Auth Service (MongoDB, JWT, bcrypt) | ✅ |
| 3 | 25 Mart | TDD ile Dispatcher testleri (RED phase) | ✅ |
| 4 | 25 Mart | Dispatcher implementasyonu (GREEN + REFACTOR) | ✅ |
| 5 | 26 Mart | Product Service (CRUD, arama, filtreleme) | ✅ |
| 6 | 28 Mart | Order Service + Inter-service communication | ✅ |
| 7 | 29 Mart | Monitoring (Prometheus, Grafana Dashboard) | ✅ |
| 8 | 30 Mart | Yük Testi (Locust) + Hata yönetimi | ✅ |
| 9 | 31 Mart | README, dokümantasyon, RMM doğrulama | ✅ |
| 10 | 2 Nisan | Final review, son düzeltmeler | ✅ |

## Commit Stratejisi

Her gün **8 commit** (4 atakancetli + 4 sadikgunay) hedeflendi. Toplam hedef: **72+ commit**.

### Commit İstatistikleri

- **atakancetli:** Dispatcher, Product Service, tests, load testing
- **sadikgunay:** Auth Service, Order Service, infra, monitoring, docs

## TDD Süreci

```
1. RED   → Test yaz, çalıştır, FAIL gör
2. GREEN → Minimum kodu yaz, test geçsin
3. REFACTOR → SOLID prensiplerine uygun hale getir
```

### TDD Örneği: Rate Limiter

```python
# RED — Önce test
async def test_rate_limiter_blocks_excess():
    limiter = RateLimiterService(max_requests=3)
    for _ in range(3):
        await limiter.is_allowed("client")
    assert await limiter.is_allowed("client") is False

# GREEN — Minimum implementasyon
class RateLimiterService:
    async def is_allowed(self, client_id):
        if len(self._requests[client_id]) >= self._max_requests:
            return False
        self._requests[client_id].append(time.time())
        return True

# REFACTOR — Sliding window eklendi
```

## SOLID Prensipleri

| Prensip | Uygulama |
|---------|----------|
| **S** — Single Responsibility | Her servis tek bir iş: Auth → kimlik, Product → ürün |
| **O** — Open/Closed | Interface üzerinden genişletme (IRouter, ILogger) |
| **L** — Liskov Substitution | DispatcherRouter ↔ IRouter yer değiştirebilir |
| **I** — Interface Segregation | Küçük, odaklı interface'ler (IRateLimiter, IProxyService) |
| **D** — Dependency Inversion | Servisler soyutlamalara bağımlı, somut sınıflara değil |
