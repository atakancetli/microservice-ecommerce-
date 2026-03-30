"""
CORS Middleware — Dispatcher.
Cross-Origin Resource Sharing yapılandırması.
Frontend uygulamaların API Gateway'e erişmesini sağlar.
"""
from fastapi.middleware.cors import CORSMiddleware


def setup_cors(app):
    """
    CORS middleware'ini yapılandırır.
    Development: tüm originler açık.
    Production: belirli domainlere kısıtlanmalı.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",      # Frontend dev server
            "http://localhost:5173",      # Vite dev server
            "http://localhost:8080",      # Gateway self
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "X-Request-ID",
            "X-User-Id",
        ],
        expose_headers=[
            "X-RateLimit-Remaining",
            "X-Request-ID",
        ],
        max_age=600,  # Preflight cache: 10 dakika
    )
