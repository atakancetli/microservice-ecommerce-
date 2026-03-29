#!/bin/bash
# ============================================================
# Full System Integration Test — Microservice E-Commerce
# Docker Compose üzerindeki tüm servislerin uçtan uca testi.
# ============================================================

BASE_URL="http://localhost:8080"
PASS=0
FAIL=0

check() {
    local name="$1"
    local expected="$2"
    local actual="$3"
    
    if [ "$actual" == "$expected" ]; then
        echo "  ✅ $name (HTTP $actual)"
        PASS=$((PASS + 1))
    else
        echo "  ❌ $name (Expected $expected, Got $actual)"
        FAIL=$((FAIL + 1))
    fi
}

echo "🚀 Full System Integration Test"
echo "================================"
echo ""

# 1. HEALTH CHECK
echo "📡 1. Health Check"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/health)
check "Gateway Health" "200" "$STATUS"
echo ""

# 2. PROMETHEUS METRICS
echo "📊 2. Prometheus Metrics"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/metrics)
check "Metrics Endpoint" "200" "$STATUS"
echo ""

# 3. AUTH FLOW
echo "🔐 3. Authentication Flow"
# Register
REGISTER=$(curl -s -X POST $BASE_URL/api/auth/register \
    -H "Content-Type: application/json" \
    -d '{"username":"systemtest","email":"system@test.com","password":"password123"}' \
    -w "\n%{http_code}")
REG_STATUS=$(echo "$REGISTER" | tail -1)
check "Register User" "201" "$REG_STATUS"

# Login
LOGIN=$(curl -s -X POST $BASE_URL/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"system@test.com","password":"password123"}')
TOKEN=$(echo "$LOGIN" | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null)
if [ -n "$TOKEN" ]; then
    echo "  ✅ Login + Token Acquired"
    PASS=$((PASS + 1))
else
    echo "  ❌ Login Failed"
    FAIL=$((FAIL + 1))
fi
echo ""

# 4. PRODUCT CRUD
echo "📦 4. Product Service CRUD"
# Create Product (with auth)
PROD=$(curl -s -X POST $BASE_URL/api/products \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"name":"Test Laptop","description":"Gaming laptop","price":15999.99,"stock":10,"category":"electronics"}' \
    -w "\n%{http_code}")
PROD_STATUS=$(echo "$PROD" | tail -1)
check "Create Product" "201" "$PROD_STATUS"

PROD_ID=$(echo "$PROD" | head -1 | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))" 2>/dev/null)

# List Products
LIST_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer $TOKEN" \
    $BASE_URL/api/products)
check "List Products" "200" "$LIST_STATUS"

# Get Product by ID
if [ -n "$PROD_ID" ]; then
    GET_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Authorization: Bearer $TOKEN" \
        $BASE_URL/api/products/$PROD_ID)
    check "Get Product by ID" "200" "$GET_STATUS"
fi

# Search Products
SEARCH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer $TOKEN" \
    "$BASE_URL/api/products/search?q=laptop")
check "Search Products" "200" "$SEARCH_STATUS"
echo ""

# 5. AUTH PROTECTION
echo "🛡️ 5. Auth Protection"
NO_AUTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/api/products)
check "Products without token → 401" "401" "$NO_AUTH_STATUS"

UNKNOWN_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/api/unknown)
check "Unknown route → 404" "404" "$UNKNOWN_STATUS"
echo ""

# 6. NETWORK ISOLATION
echo "🏗️ 6. Network Isolation"
AUTH_DIRECT=$(curl -s --connect-timeout 2 -o /dev/null -w "%{http_code}" http://localhost:8001/health 2>/dev/null)
if [ "$AUTH_DIRECT" == "000" ]; then
    echo "  ✅ Auth Service: İzole (dışarıdan erişilemez)"
    PASS=$((PASS + 1))
else
    echo "  ❌ Auth Service: Erişilebilir ($AUTH_DIRECT)"
    FAIL=$((FAIL + 1))
fi
PROD_DIRECT=$(curl -s --connect-timeout 2 -o /dev/null -w "%{http_code}" http://localhost:8002/health 2>/dev/null)
if [ "$PROD_DIRECT" == "000" ]; then
    echo "  ✅ Product Service: İzole (dışarıdan erişilemez)"
    PASS=$((PASS + 1))
else
    echo "  ❌ Product Service: Erişilebilir ($PROD_DIRECT)"
    FAIL=$((FAIL + 1))
fi
echo ""

# 7. MONITORING
echo "📊 7. Monitoring"
PROM_STATUS=$(curl -s --connect-timeout 2 -o /dev/null -w "%{http_code}" http://localhost:9090/-/healthy 2>/dev/null)
check "Prometheus Healthy" "200" "$PROM_STATUS"
GRAFANA_STATUS=$(curl -s --connect-timeout 2 -o /dev/null -w "%{http_code}" http://localhost:3000/api/health 2>/dev/null)
check "Grafana Healthy" "200" "$GRAFANA_STATUS"
echo ""

# SONUÇ
echo "================================"
echo "📋 Sonuç: $PASS Geçti, $FAIL Başarısız"
echo "================================"
