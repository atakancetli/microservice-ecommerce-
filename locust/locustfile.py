"""
Locust yük test dosyası.
Dispatcher (API Gateway) üzerinden tüm servisleri test eder.
"""
from locust import HttpUser, task, between


class ECommerceUser(HttpUser):
    """E-Ticaret kullanıcı senaryosu."""

    wait_time = between(1, 3)
    host = "http://localhost:8080"

    def on_start(self):
        """Kullanıcı oturum açma."""
        # Önce kayıt ol
        self.client.post("/api/auth/register", json={
            "username": f"user_{self.environment.runner.user_count}",
            "email": f"user_{self.environment.runner.user_count}@test.com",
            "password": "test123456"
        })
        # Sonra giriş yap
        response = self.client.post("/api/auth/login", json={
            "email": f"user_{self.environment.runner.user_count}@test.com",
            "password": "test123456"
        })
        if response.status_code == 200:
            self.token = response.json().get("access_token", "")
        else:
            self.token = ""

    @property
    def auth_headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def list_products(self):
        """Ürünleri listele — en sık yapılan işlem."""
        self.client.get("/api/products", headers=self.auth_headers)

    @task(2)
    def get_product_detail(self):
        """Ürün detayı getir."""
        self.client.get("/api/products/1", headers=self.auth_headers)

    @task(1)
    def create_order(self):
        """Sipariş oluştur."""
        self.client.post("/api/orders", json={
            "product_id": "1",
            "quantity": 1,
        }, headers=self.auth_headers)

    @task(1)
    def list_orders(self):
        """Siparişleri listele."""
        self.client.get("/api/orders", headers=self.auth_headers)

    @task(1)
    def health_check(self):
        """Sağlık kontrolü."""
        self.client.get("/health")
