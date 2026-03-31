# Contributing Guide — Microservice E-Commerce

## Geliştirme Ortamı

### Gereksinimler
- Python 3.11+
- Docker 24+ ve Docker Compose v2
- Git

### Kurulum

```bash
# Repo klonla
git clone https://github.com/atakancetli/microservice-ecommerce-.git
cd microservice-ecommerce

# Tüm servisleri başlat
docker compose up --build -d

# Logları izle
docker compose logs -f
```

## Commit Conventions

Bu projede [Conventional Commits](https://www.conventionalcommits.org/) standardı kullanılmaktadır:

```
<type>(<scope>): <description>

Örnekler:
feat(auth): implement JWT token generation
fix(dispatcher): correct route prefix stripping
test(order): add stock validation edge cases
docs: update README with sequence diagrams
infra: add Grafana datasource provisioning
chore: update dependencies
```

### Tipler

| Tip | Açıklama |
|-----|----------|
| `feat` | Yeni özellik |
| `fix` | Hata düzeltme |
| `test` | Test ekleme/düzeltme |
| `docs` | Dokümantasyon |
| `infra` | Altyapı (Docker, CI/CD) |
| `chore` | Genel bakım |
| `refactor` | Kod iyileştirme |

## Proje Yapısı

```
microservice-ecommerce/
├── dispatcher/          # API Gateway
│   ├── app/
│   │   ├── middleware/  # Auth, CORS, Metrics, ErrorHandler
│   │   ├── models/      # Interface definitions
│   │   ├── routes/      # Router, Log routes
│   │   └── services/    # Proxy, Logger, RateLimiter, CircuitBreaker
│   └── tests/           # TDD test suite
├── auth-service/        # Authentication microservice
│   ├── app/
│   │   ├── models/      # User model
│   │   ├── routes/      # Auth routes
│   │   └── services/    # Auth logic, DB
│   └── tests/
├── product-service/     # Product catalog microservice
│   ├── app/
│   │   ├── models/      # Product model
│   │   ├── routes/      # Product CRUD routes
│   │   └── services/    # Product logic, DB
│   └── tests/
├── order-service/       # Order management microservice
│   ├── app/
│   │   ├── models/      # Order model
│   │   ├── routes/      # Order routes
│   │   └── services/    # Order logic, ProductClient, DB
│   └── tests/
├── docs/                # Documentation
├── grafana/             # Grafana dashboards + provisioning
├── prometheus/          # Prometheus config
├── locust/              # Load tests
├── tests/               # Integration tests
└── docker-compose.yml   # Orchestration
```

## Test Çalıştırma

```bash
# Tüm dispatcher testlerini çalıştır
cd dispatcher && pytest tests/ -v

# Belirli test dosyası
pytest tests/test_routing.py -v

# Coverage
pytest tests/ --cov=app --cov-report=html
```
