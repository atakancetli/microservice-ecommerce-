# API Endpoint Referans Kılavuzu

## Authentication

### Register
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securePassword123"
}

→ 201 Created
{
  "id": "65f...",
  "username": "johndoe",
  "email": "john@example.com",
  "role": "user"
}
```

### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "securePassword123"
}

→ 200 OK
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

---

## Products

### Create Product
```http
POST /api/products
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Gaming Laptop",
  "description": "High-end gaming laptop",
  "price": 15999.99,
  "stock": 25,
  "category": "electronics"
}

→ 201 Created
```

### List Products
```http
GET /api/products
Authorization: Bearer <token>

→ 200 OK
[
  {"id": "...", "name": "Gaming Laptop", "price": 15999.99, ...}
]
```

### Search Products
```http
GET /api/products/search?q=laptop
Authorization: Bearer <token>

→ 200 OK
```

### Get Product
```http
GET /api/products/{id}
Authorization: Bearer <token>

→ 200 OK
```

### Update Product
```http
PUT /api/products/{id}
Authorization: Bearer <token>
Content-Type: application/json

{"price": 14999.99, "stock": 20}

→ 200 OK
```

### Delete Product
```http
DELETE /api/products/{id}
Authorization: Bearer <token>

→ 204 No Content
```

---

## Orders

### Create Order
```http
POST /api/orders
Authorization: Bearer <token>
Content-Type: application/json

{
  "items": [
    {"product_id": "65f...", "quantity": 2, "price_at_order": 15999.99}
  ],
  "shipping_address": "123 Main St, Istanbul"
}

→ 201 Created
```

### List My Orders
```http
GET /api/orders
Authorization: Bearer <token>

→ 200 OK
```

### Get Order Detail
```http
GET /api/orders/{id}
Authorization: Bearer <token>

→ 200 OK
```

### Update Order Status
```http
PATCH /api/orders/{id}/status
Authorization: Bearer <token>
Content-Type: application/json

{"status": "completed"}

→ 200 OK
```

---

## Error Responses

Tüm hata yanıtları standart formattadır:

```json
{
  "error": true,
  "status_code": 401,
  "detail": "Authentication required.",
  "path": "/api/products"
}
```
