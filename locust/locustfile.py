"""
Locust yük test dosyası — Gelişmiş versiyon.
Dispatcher (API Gateway) üzerinden tüm servisleri test eder.
Farklı yoğunluk seviyelerinde (50/100/200/500 concurrent user).
"""
import random
import string
from locust import HttpUser, task, between, events


def random_string(length=8):
    """Rastgele string üretir."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


class ECommerceUser(HttpUser):
    """
    E-Ticaret kullanıcı senaryosu.
    Gerçek kullanıcı davranışını simüle eder:
    - Ürün listeleme (en sık)
    - Ürün detayı görüntüleme
    - Ürün arama
    - Sipariş oluşturma (en nadir)
    """

    wait_time = between(0.5, 2)
    host = "http://localhost:8080"

    def on_start(self):
        """Kullanıcı kayıt ve giriş."""
        self.username = f"loadtest_{random_string()}"
        self.email = f"{self.username}@test.com"
        self.token = ""
        self.product_ids = []

        # Kayıt ol
        self.client.post("/api/auth/register", json={
            "username": self.username,
            "email": self.email,
            "password": "loadtest123456"
        }, name="/api/auth/register")

        # Giriş yap
        response = self.client.post("/api/auth/login", json={
            "email": self.email,
            "password": "loadtest123456"
        }, name="/api/auth/login")

        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token", "")

        # Test ürünü oluştur
        if self.token:
            prod_resp = self.client.post("/api/products", json={
                "name": f"LoadTest Product {random_string(4)}",
                "description": "Yük testi ürünü",
                "price": round(random.uniform(10.0, 999.0), 2),
                "stock": random.randint(1, 100),
                "category": random.choice(["electronics", "clothing", "food", "books"]),
            }, headers=self.auth_headers, name="/api/products [CREATE]")
            if prod_resp.status_code == 201:
                self.product_ids.append(prod_resp.json().get("id", ""))

    @property
    def auth_headers(self):
        """JWT token header."""
        return {"Authorization": f"Bearer {self.token}"}

    # ─── ÜRÜN İŞLEMLERİ ───

    @task(5)
    def list_products(self):
        """Ürünleri listele — en sık yapılan işlem."""
        self.client.get("/api/products", headers=self.auth_headers,
                       name="/api/products [LIST]")

    @task(3)
    def get_product_detail(self):
        """Ürün detayı getir."""
        if self.product_ids:
            pid = random.choice(self.product_ids)
            self.client.get(f"/api/products/{pid}", headers=self.auth_headers,
                          name="/api/products/:id [GET]")

    @task(2)
    def search_products(self):
        """Ürün arama."""
        query = random.choice(["laptop", "phone", "test", "product"])
        self.client.get(f"/api/products/search?q={query}", headers=self.auth_headers,
                       name="/api/products/search [SEARCH]")

    # ─── SİPARİŞ İŞLEMLERİ ───

    @task(1)
    def create_order(self):
        """Sipariş oluştur."""
        if self.product_ids:
            pid = random.choice(self.product_ids)
            self.client.post("/api/orders", json={
                "items": [{
                    "product_id": pid,
                    "quantity": random.randint(1, 3),
                    "price_at_order": round(random.uniform(10.0, 500.0), 2),
                }],
                "shipping_address": f"Test Mahallesi No:{random.randint(1,100)}, İstanbul"
            }, headers=self.auth_headers, name="/api/orders [CREATE]")

    @task(2)
    def list_orders(self):
        """Siparişleri listele."""
        self.client.get("/api/orders", headers=self.auth_headers,
                       name="/api/orders [LIST]")

    # ─── SİSTEM İŞLEMLERİ ───

    @task(1)
    def health_check(self):
        """Gateway sağlık kontrolü."""
        self.client.get("/health", name="/health")

    @task(1)
    def get_metrics(self):
        """Prometheus metrikleri."""
        self.client.get("/metrics", name="/metrics")


class UnauthenticatedUser(HttpUser):
    """
    Yetkisiz kullanıcı senaryosu.
    Auth korumalı endpoint'lere token olmadan erişmeye çalışır.
    Bu, 401 yanıtlarının düzgün çalıştığını doğrular.
    """

    wait_time = between(2, 5)
    host = "http://localhost:8080"
    weight = 1  # Az sayıda

    @task(3)
    def try_list_products_no_auth(self):
        """Token olmadan ürün listeleme (401 beklenir)."""
        with self.client.get("/api/products", catch_response=True,
                            name="/api/products [NO AUTH]") as response:
            if response.status_code == 401:
                response.success()

    @task(1)
    def try_unknown_route(self):
        """Bilinmeyen route (404 beklenir)."""
        with self.client.get("/api/nonexistent", catch_response=True,
                            name="/api/nonexistent [404]") as response:
            if response.status_code == 404:
                response.success()
