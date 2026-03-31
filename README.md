# 🛒 E-Commerce Microservice Architecture

**Kocaeli Üniversitesi — Bilişim Sistemleri Mühendisliği**  
**Yazılım Geliştirme Laboratuvarı-II — Proje 1**

## 👥 Ekip Üyeleri

| İsim | GitHub | E-posta |
|------|--------|---------|
| Atakan Çetli | [@atakancetli](https://github.com/atakancetli) | atakancetli5@gmail.com |
| Sadık Günay | [@sadikgunay](https://github.com/sadikgunay) | sadkgny2003@gmail.com |

**Tarih:** Mart 2026

---

## 📋 İçindekiler

1. [Giriş](#-giriş)
2. [Mimari Tasarım](#-mimari-tasarım)
3. [Servisler](#-servisler)
4. [Richardson Olgunluk Modeli](#-richardson-olgunluk-modeli)
5. [Veri Tabanı Tasarımı](#-veri-tabanı-tasarımı)
6. [Docker & Orkestrasyon](#-docker--orkestrasyon)
7. [Test Stratejisi](#-test-stratejisi)
8. [Performans Testleri](#-performans-testleri)
9. [Network Isolation](#-network-isolation)
10. [Sonuç ve Tartışma](#-sonuç-ve-tartışma)

---

## 📖 Giriş

Bu proje, modern yazılım geliştirme süreçlerinin temelini oluşturan **Mikroservis Mimarisi** ve servisler arası trafik yönetimini sağlayan bir **Dispatcher (API Gateway)** yazılımının uçtan uca geliştirilmesini kapsamaktadır.

### Problemin Tanımı

Monolitik uygulamalarda ölçeklenebilirlik, bağımsız dağıtım ve hata izolasyonu gibi konularda yaşanan sorunlara çözüm olarak, bir e-ticaret senaryosu üzerinde mikroservis tabanlı mimari tasarlanmıştır.

### Amaç

- Bağımsız servislerin orkestrasyonunu sağlayan bir Dispatcher geliştirmek
- TDD (Test-Driven Development) ile güvenilir yazılım üretmek
- Docker ile servis izolasyonu ve kolay dağıtım sağlamak
- Yük testleri ile sistem performansını doğrulamak

---

## 🏗 Mimari Tasarım

### Sistem Mimarisi

```mermaid
graph TB
    Client["🌐 Client"]
    
    subgraph Docker["Docker Compose"]
        subgraph Frontend["Frontend Network (Dış Erişim)"]
            Dispatcher["🚦 Dispatcher<br/>API Gateway<br/>:8080"]
            Grafana["📊 Grafana<br/>:3000"]
            Prometheus["📈 Prometheus<br/>:9090"]
        end
        
        subgraph Backend["Backend Network (İç Ağ - İzole)"]
            Auth["🔐 Auth Service<br/>:8001"]
            Product["📦 Product Service<br/>:8002"]
            Order["🛒 Order Service<br/>:8003"]
            
            Redis[("Redis<br/>Dispatcher DB")]
            AuthDB[("MongoDB<br/>Auth DB")]
            ProductDB[("MongoDB<br/>Product DB")]
            OrderDB[("MongoDB<br/>Order DB")]
        end
    end
    
    Client -->|HTTP| Dispatcher
    Dispatcher -->|Route| Auth
    Dispatcher -->|Route| Product
    Dispatcher -->|Route| Order
    
    Order -.->|Stock Check| Product
    
    Dispatcher --- Redis
    Auth --- AuthDB
    Product --- ProductDB
    Order --- OrderDB
    
    Dispatcher -.->|Metrics| Prometheus
    Prometheus -.->|Data| Grafana

    style Frontend fill:#1a365d,color:#fff
    style Backend fill:#2d3748,color:#fff
```

### Sınıf Diyagramı — Dispatcher

```mermaid
classDiagram
    class IRouter {
        <<interface>>
        +register_service(service) void
        +unregister_service(name) void
        +resolve_route(path) RouteResult
        +get_registered_services() List
    }
    
    class IAuthMiddleware {
        <<interface>>
        +authenticate(token) AuthUser
        +authorize(user, path, method) bool
        +is_public_route(path) bool
    }
    
    class ILogger {
        <<interface>>
        +log(entry) void
        +get_logs(level, service, limit) List
        +get_stats() dict
    }
    
    class IProxyService {
        <<interface>>
        +forward_request(method, url, headers, body) dict
    }
    
    class IRateLimiter {
        <<interface>>
        +is_allowed(client_id) bool
        +get_remaining(client_id) int
    }
    
    class DispatcherRouter {
        -_services: Dict
        -ROUTE_MAP: Dict
        +register_service(service) void
        +resolve_route(path) RouteResult
    }
    
    class AuthMiddlewareService {
        -_secret_key: str
        -_public_routes: List
        +authenticate(token) AuthUser
        +authorize(user, path, method) bool
    }
    
    class RequestLogger {
        -_logs: List
        +log(entry) void
        +get_logs(level, service, limit) List
    }
    
    class ProxyServiceImpl {
        +forward_request(method, url, headers, body) dict
    }
    
    class RateLimiterService {
        -_max_requests: int
        -_window_seconds: int
        -_requests: Dict
        +is_allowed(client_id) bool
        +get_remaining(client_id) int
    }
    
    class CircuitBreaker {
        -_failure_threshold: int
        -_recovery_timeout: int
        +get_state(service) CircuitState
        +record_success(service) void
        +record_failure(service) void
    }
    
    class RetryHandler {
        -_max_retries: int
        -_base_delay: float
        +should_retry(status_code, attempt) bool
        +get_delay(attempt) float
    }
    
    IRouter <|.. DispatcherRouter
    IAuthMiddleware <|.. AuthMiddlewareService
    ILogger <|.. RequestLogger
    IProxyService <|.. ProxyServiceImpl
    IRateLimiter <|.. RateLimiterService
```

### Sequence Diyagramı — İstek Akışı

```mermaid
sequenceDiagram
    actor Client
    participant GW as Dispatcher (Gateway)
    participant RL as Rate Limiter
    participant Auth as Auth Middleware
    participant Router as Router
    participant Proxy as Proxy Service
    participant Svc as Downstream Service
    participant Log as Logger

    Client->>GW: HTTP Request
    GW->>RL: is_allowed(client_ip)?
    alt Rate Limit Exceeded
        RL-->>GW: false
        GW-->>Client: 429 Too Many Requests
    else Allowed
        RL-->>GW: true
        GW->>Router: resolve_route(path)
        alt Route Not Found
            Router-->>GW: null
            GW-->>Client: 404 Not Found
        else Route Found
            Router-->>GW: RouteResult
            GW->>Auth: is_public_route(path)?
            alt Protected Route
                Auth-->>GW: false
                GW->>Auth: authenticate(token)
                alt Invalid Token
                    Auth-->>GW: null
                    GW-->>Client: 401 Unauthorized
                else Valid Token
                    Auth-->>GW: AuthUser
                    GW->>Auth: authorize(user, path, method)
                end
            end
            GW->>Proxy: forward_request(method, url, body)
            Proxy->>Svc: HTTP Request
            Svc-->>Proxy: HTTP Response
            Proxy-->>GW: result
            GW->>Log: log(entry)
            GW-->>Client: HTTP Response
        end
    end
```

### Sequence Diyagramı — Sipariş Akışı (Inter-Service)

```mermaid
sequenceDiagram
    actor Client
    participant GW as API Gateway
    participant OS as Order Service
    participant PS as Product Service
    participant DB as Order MongoDB

    Client->>GW: POST /api/orders
    GW->>GW: Auth Check (JWT)
    GW->>OS: POST /orders (X-User-Id header)
    OS->>PS: GET /products/{id} (Stock Check)
    alt Stock Available
        PS-->>OS: 200 OK (product data)
        OS->>DB: Insert Order
        DB-->>OS: Order Created
        OS-->>GW: 201 Created
        GW-->>Client: 201 Order Created
    else Out of Stock
        PS-->>OS: 404 / stock=0
        OS-->>GW: 400 Bad Request
        GW-->>Client: 400 Stock Insufficient
    end
```

---

## 🔌 Servisler

### 1. Dispatcher (API Gateway) — Port 8080

Tüm dış isteklerin tek giriş noktası. Sorumlulukları:

| Özellik | Açıklama |
|---------|----------|
| **Routing** | URL tabanlı servis yönlendirme (`/api/auth/*`, `/api/products/*`, `/api/orders/*`) |
| **Authentication** | JWT token doğrulama (public route'lar hariç) |
| **Authorization** | Kullanıcı rol bazlı yetkilendirme |
| **Rate Limiting** | Sliding window (100 req/dk) — 429 yanıtı |
| **Circuit Breaker** | Hatalı servisleri geçici devre dışı bırakma |
| **Retry** | 5xx hatalarında exponential backoff ile tekrar deneme |
| **Logging** | Merkezi istek/yanıt loglama |
| **Metrics** | Prometheus formatında metrik sunumu |
| **CORS** | Cross-Origin Resource Sharing yapılandırması |
| **Request ID** | Dağıtık izleme için UUID ataması |

### 2. Auth Service — Port 8001

| Endpoint | Metot | Açıklama | Auth |
|----------|-------|----------|------|
| `/auth/register` | POST | Kullanıcı kaydı | ❌ Public |
| `/auth/login` | POST | Giriş + JWT token | ❌ Public |
| `/auth/users` | GET | Kullanıcı listesi | ✅ Admin |

**Teknoloji:** MongoDB + bcrypt + python-jose (JWT)

### 3. Product Service — Port 8002

| Endpoint | Metot | Açıklama | Auth |
|----------|-------|----------|------|
| `/products` | POST | Ürün oluştur | ✅ |
| `/products` | GET | Ürün listesi (pagination + filter) | ✅ |
| `/products/search` | GET | Ürün arama | ✅ |
| `/products/{id}` | GET | Ürün detayı | ✅ |
| `/products/{id}` | PUT | Ürün güncelle (partial) | ✅ |
| `/products/{id}` | DELETE | Ürün sil | ✅ |

**Teknoloji:** MongoDB + motor (async)

### 4. Order Service — Port 8003

| Endpoint | Metot | Açıklama | Auth |
|----------|-------|----------|------|
| `/orders` | POST | Sipariş oluştur | ✅ |
| `/orders` | GET | Kullanıcı siparişleri | ✅ |
| `/orders/{id}` | GET | Sipariş detayı | ✅ |
| `/orders/{id}/status` | PATCH | Durum güncelle | ✅ |

**Teknoloji:** MongoDB + httpx (inter-service communication)

---

## 📐 Richardson Olgunluk Modeli

Projemiz **RMM Seviye 2** uyumluluğunu sağlamaktadır:

| Seviye | Özellik | Durum |
|--------|---------|-------|
| **Level 0** | Tek URL, tek metot | ✅ Aşıldı |
| **Level 1** | Kaynak bazlı URL'ler (`/products`, `/orders`) | ✅ Uygulandı |
| **Level 2** | Doğru HTTP metotları ve durum kodları | ✅ Uygulandı |
| **Level 3** | HATEOAS (Hypermedia) | ⬜ Kapsam dışı |

### HTTP Durum Kodları

| Kod | Kullanım |
|-----|----------|
| `200 OK` | Başarılı GET/PUT/PATCH |
| `201 Created` | Başarılı POST (yeni kaynak) |
| `204 No Content` | Başarılı DELETE |
| `400 Bad Request` | Geçersiz istek (stok yetersiz vb.) |
| `401 Unauthorized` | Token eksik/geçersiz |
| `403 Forbidden` | Yetersiz yetki |
| `404 Not Found` | Kaynak bulunamadı |
| `422 Unprocessable` | Validasyon hatası |
| `429 Too Many Requests` | Rate limit aşıldı |
| `500 Internal Server Error` | Sunucu hatası |

---

## 💾 Veri Tabanı Tasarımı

### Auth DB (MongoDB)

```json
{
  "_id": "ObjectId",
  "username": "string",
  "email": "string (unique)",
  "hashed_password": "string (bcrypt)",
  "role": "user | admin",
  "created_at": "datetime"
}
```

### Product DB (MongoDB)

```json
{
  "_id": "ObjectId",
  "name": "string",
  "description": "string",
  "price": "float (> 0)",
  "stock": "int (>= 0)",
  "category": "string",
  "image_url": "string | null",
  "created_at": "datetime",
  "updated_at": "datetime | null"
}
```

### Order DB (MongoDB)

```json
{
  "_id": "ObjectId",
  "user_id": "string",
  "items": [
    {
      "product_id": "string",
      "quantity": "int (> 0)",
      "price_at_order": "float"
    }
  ],
  "total_price": "float",
  "status": "pending | completed | cancelled | shipped",
  "shipping_address": "string",
  "created_at": "datetime",
  "updated_at": "datetime | null"
}
```

---

## 🐳 Docker & Orkestrasyon

### Konteyner Yapısı

```
10 container:
├── dispatcher         (FastAPI — Gateway)
├── auth-service       (FastAPI — Auth)
├── product-service    (FastAPI — Product)
├── order-service      (FastAPI — Order)
├── dispatcher-redis   (Redis 7)
├── auth-mongo         (MongoDB 7)
├── product-mongo      (MongoDB 7)
├── order-mongo        (MongoDB 7)
├── prometheus         (Prometheus)
└── grafana            (Grafana)
```

### Network İzolasyonu

| Network | Tip | Servisler | Dış Erişim |
|---------|-----|-----------|------------|
| `frontend` | bridge | Dispatcher, Grafana, Prometheus | ✅ Açık |
| `backend` | bridge (internal) | Auth, Product, Order, DB'ler | ❌ Kapalı |

### Çalıştırma

```bash
# Tüm sistemi başlat
docker compose up --build -d

# Logları izle
docker compose logs -f dispatcher

# Sistemi durdur
docker compose down

# Volumes ile birlikte temizle
docker compose down -v
```

---

## 🧪 Test Stratejisi

### TDD (Test-Driven Development)

Dispatcher servisi için **57 test** TDD yaklaşımıyla geliştirilmiştir:

1. **RED:** Önce başarısız testler yazıldı
2. **GREEN:** Testleri geçirecek minimum kod yazıldı
3. **REFACTOR:** SOLID prensiplerine uygun refactoring yapıldı

### Test Kategorileri

| Kategori | Dosya | Test Sayısı |
|----------|-------|-------------|
| Routing | `test_routing.py` | 12 |
| Auth Middleware | `test_auth_middleware.py` | 15 |
| Error Handling | `test_error_handling.py` | 8 |
| Logging | `test_logging.py` | 10 |
| Rate Limiting | `test_rate_limiting.py` | 12 |
| Edge Cases | `test_edge_cases.py` | 15 |
| Product Models | `test_product.py` | 8 |
| Order Models | `test_order.py` | 6 |
| Auth Service | `test_auth.py` | 5 |

### Test Çalıştırma

```bash
# Dispatcher testleri
cd dispatcher && pytest tests/ -v --tb=short

# Auth Service testleri
cd auth-service && pytest tests/ -v

# Product Service testleri
cd product-service && pytest tests/ -v

# Order Service testleri
cd order-service && pytest tests/ -v
```

---

## 📊 Performans Testleri

Locust ile 4 farklı yoğunluk seviyesinde yük testi yapılmıştır:

| Senaryo | Concurrent User | Avg Yanıt | p95 Yanıt | Hata Oranı |
|---------|----------------|-----------|-----------|------------|
| Düşük | 50 | <50ms | <100ms | ~0% |
| Orta | 100 | <80ms | <200ms | <1% |
| Yüksek | 200 | <150ms | <500ms | <2% |
| Stres | 500 | <300ms | <1000ms | <5% |

```bash
# Yük testi çalıştırma
locust -f locust/locustfile.py --headless -u 100 -r 20 --run-time 60s
```

---

## 🛡 Network Isolation

Mikroservislere dışarıdan doğrudan erişim **engellenmiştir**:

```bash
# Doğrulama
curl http://localhost:8001/health  # ❌ Timeout (izole)
curl http://localhost:8002/health  # ❌ Timeout (izole)
curl http://localhost:8003/health  # ❌ Timeout (izole)
curl http://localhost:8080/health  # ✅ 200 OK (gateway)
```

Tüm servisler yalnızca **Dispatcher (API Gateway)** üzerinden erişilebilirdir.

---

## 🎯 Sonuç ve Tartışma

### Başarılar

- ✅ **4 bağımsız mikroservis** başarıyla geliştirildi ve orkestre edildi
- ✅ **TDD ile 57+ test** yazılarak yazılım güvenilirliği sağlandı
- ✅ **Docker Compose** ile tek komutla tüm sistem ayağa kalkıyor
- ✅ **Network isolation** ile güvenlik katmanı oluşturuldu
- ✅ **Prometheus + Grafana** ile gerçek zamanlı izleme altyapısı kuruldu
- ✅ **Rate Limiting + Circuit Breaker** ile sistem dayanıklılığı artırıldı
- ✅ **Inter-service communication** (Order → Product stok kontrolü) çalışıyor

### Zorluklar ve Çözümler

| Zorluk | Çözüm |
|--------|-------|
| motor/pymongo versiyon çakışması | Sürüm pinleme (motor==3.6.0, pymongo==4.9.2) |
| passlib/bcrypt uyumsuzluğu | bcrypt==4.0.1 olarak sabitlendi |
| Route forwarding hatası | `/api` prefix stripping mantığı düzeltildi |
| Docker network isolation | `internal: true` ile backend ağı izole edildi |

### Gelecek İyileştirmeler

- Redis tabanlı distributed rate limiting
- API versioning (v1, v2)
- Message queue (RabbitMQ/Kafka) ile asenkron iletişim
- Kubernetes ile container orchestration
- CI/CD pipeline (GitHub Actions)

---

## 🛠 Teknoloji Yığını

| Bileşen | Teknoloji |
|---------|-----------|
| Programlama Dili | Python 3.11 |
| Web Framework | FastAPI |
| Test Framework | pytest + httpx |
| Dispatcher DB | Redis 7 |
| Servis DB'leri | MongoDB 7 |
| Konteyner | Docker + Docker Compose |
| Monitoring | Prometheus + Grafana |
| Yük Testi | Locust |
| Güvenlik | JWT (python-jose) + bcrypt (passlib) |

---

## 🚀 Hızlı Başlangıç

```bash
# 1. Projeyi klonla
git clone https://github.com/atakancetli/microservice-ecommerce-.git
cd microservice-ecommerce

# 2. Tüm sistemi ayağa kaldır
docker compose up --build -d

# 3. Test et
curl http://localhost:8080/health

# 4. Kullanıcı kaydı
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","email":"demo@test.com","password":"demo123456"}'

# 5. Giriş yap
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@test.com","password":"demo123456"}'
```

### Erişim Noktaları

| Servis | URL |
|--------|-----|
| API Gateway (Swagger) | http://localhost:8080/docs |
| Grafana Dashboard | http://localhost:3000 (admin/admin) |
| Prometheus | http://localhost:9090 |

---

*Kocaeli Üniversitesi — Bilişim Sistemleri Mühendisliği — Mart 2026*
