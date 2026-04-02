# Changelog — Microservice E-Commerce

Bu proje 10 günlük bir sprint süresince geliştirilmiştir.

## [1.0.0] — 2026-04-02

### 🚀 İlk Sürüm

#### Dispatcher (API Gateway)
- URL tabanlı routing (`/api/auth/*`, `/api/products/*`, `/api/orders/*`)
- JWT tabanlı merkezi authentication ve authorization
- Rate Limiting (Sliding Window — 100 req/dk)
- Circuit Breaker (CLOSED → OPEN → HALF_OPEN)
- Retry Handler (Exponential Backoff)
- Prometheus metrikleri (Counter, Histogram, Gauge)
- CORS middleware
- Request ID middleware (UUID v4)
- Centralized error handling (HTTP, Validation, General)

#### Auth Service
- Kullanıcı kaydı (bcrypt ile şifreleme)
- JWT token üretimi ve doğrulama
- Rol tabanlı yetkilendirme (user, admin)

#### Product Service
- CRUD işlemleri (Create, Read, Update, Delete)
- Ürün arama (query-based)
- Kategori filtreleme
- Pagination desteği

#### Order Service
- Sipariş oluşturma (kullanıcı bazlı)
- Stok kontrolü (Product Service ile inter-service HTTP)
- Sipariş durumu güncelleme (PENDING → COMPLETED → SHIPPED)
- Kullanıcı siparişlerini listeleme

#### Altyapı
- Docker Compose (10 konteyner)
- Network Isolation (frontend/backend)
- Prometheus + Grafana monitoring
- 9-panel Grafana dashboard
- Locust yük testleri (50-500 concurrent user)

#### Dokümantasyon
- README (Mermaid diyagramlar, RMM, DB şemaları)
- API Reference
- Architecture Decision Records (ADR)
- Middleware Pipeline
- Contributing Guide
- Load Test Results

#### Test
- 57+ unit test (TDD yaklaşımı)
- Edge case testleri
- Full system integration test script
- Network isolation verification script
