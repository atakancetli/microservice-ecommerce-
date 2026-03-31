# Mimari Kararlar Kaydı (Architecture Decision Records)

## ADR-001: FastAPI Framework Seçimi

**Durum:** Kabul Edildi  
**Tarih:** Mart 2026

### Bağlam
Mikroservisler için bir web framework gereksinimi vardı.

### Karar
**FastAPI** seçildi. Alternatifler: Flask, Django REST, Express.js

### Gerekçe
- Async/await desteği (ASGI) → yüksek concurrent performans
- Otomatik OpenAPI/Swagger dökümantasyonu
- Pydantic ile runtime tip kontrolü ve validasyon
- Python ekosistemi ile uyumluluk (pytest, httpx)

---

## ADR-002: MongoDB Veritabanı Seçimi

**Durum:** Kabul Edildi  
**Tarih:** Mart 2026

### Bağlam
Her mikroservisin bağımsız bir veritabanına ihtiyacı vardı.

### Karar
**MongoDB 7** seçildi. Alternatifler: PostgreSQL, MySQL, Redis

### Gerekçe
- Schema-less yapı → hızlı prototipleme
- Her servis için ayrı DB instance (veritabanı izolasyonu)
- Motor async driver ile FastAPI uyumluluğu
- JSON-native → REST API ile doğal uyum

---

## ADR-003: API Gateway Pattern

**Durum:** Kabul Edildi  
**Tarih:** Mart 2026

### Bağlam
Mikroservislere dışarıdan tek bir giriş noktası gerekiyordu.

### Karar
Custom **Dispatcher (API Gateway)** geliştirildi.

### Gerekçe
- Merkezi authentication/authorization
- URL tabanlı routing
- Rate limiting ve circuit breaker
- Monitoring ve logging birleştirmesi
- Öğrenme amacıyla (hazır çözüm yerine kendi implementasyon)

---

## ADR-004: Network Isolation Stratejisi

**Durum:** Kabul Edildi  
**Tarih:** Mart 2026

### Bağlam
Mikroservisler dışarıdan doğrudan erişilmemeli, sadece Gateway üzerinden erişilebilir olmalı.

### Karar
Docker Compose'da `frontend` ve `backend` olmak üzere iki ayrı network tanımlandı. Backend ağı `internal: true` olarak işaretlendi.

### Gerekçe
- Güvenlik katmanı (mikro segmentasyon)
- Database'ler dışarıdan erişilemez
- Gateway tek entry point olarak güçlendirildi
- Zero Trust Network modeli yaklaşımı

---

## ADR-005: Inter-Service Communication (Senkron HTTP)

**Durum:** Kabul Edildi  
**Tarih:** Mart 2026

### Bağlam
Order Service, sipariş oluşturmadan önce Product Service'ten stok kontrolü yapmalıydı.

### Karar
**httpx.AsyncClient** ile senkron HTTP çağrıları tercih edildi.

### Gerekçe
- Sipariş oluşturma öncesi stok doğrulaması anlık olmalı
- Asenkron mesajlaşma (RabbitMQ) bu senaryo için overkill
- Circuit breaker ile hata toleransı sağlandı
- İleride message queue'ya geçiş mümkün (ADR güncellenebilir)
