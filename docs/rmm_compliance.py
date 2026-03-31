"""
RMM Seviye 2 Uyumluluk Kontrol Listesi.
Her endpoint'in doğru HTTP metodu ve durum kodu kullanıp kullanmadığını doğrular.
"""

# ============================================================
# Richardson Maturity Model — Level 2 Compliance Check
# ============================================================

RMM_CHECKLIST = {
    "Auth Service": {
        "POST /auth/register": {"method": "POST", "success": 201, "errors": [400, 409]},
        "POST /auth/login": {"method": "POST", "success": 200, "errors": [401]},
        "GET /auth/users": {"method": "GET", "success": 200, "errors": [403]},
    },
    "Product Service": {
        "POST /products": {"method": "POST", "success": 201, "errors": [400, 422]},
        "GET /products": {"method": "GET", "success": 200, "errors": []},
        "GET /products/:id": {"method": "GET", "success": 200, "errors": [404]},
        "GET /products/search": {"method": "GET", "success": 200, "errors": []},
        "PUT /products/:id": {"method": "PUT", "success": 200, "errors": [404, 422]},
        "DELETE /products/:id": {"method": "DELETE", "success": 204, "errors": [404]},
    },
    "Order Service": {
        "POST /orders": {"method": "POST", "success": 201, "errors": [400]},
        "GET /orders": {"method": "GET", "success": 200, "errors": []},
        "GET /orders/:id": {"method": "GET", "success": 200, "errors": [404]},
        "PATCH /orders/:id/status": {"method": "PATCH", "success": 200, "errors": [404]},
    },
    "Dispatcher": {
        "GET /health": {"method": "GET", "success": 200, "errors": []},
        "GET /metrics": {"method": "GET", "success": 200, "errors": []},
        "GET /logs": {"method": "GET", "success": 200, "errors": []},
        "ANY /api/*": {"method": "PROXY", "success": "varies", "errors": [401, 403, 404, 429]},
    },
}


def verify_rmm_compliance():
    """RMM Level 2 uyumluluğunu kontrol eder."""
    issues = []
    for service, endpoints in RMM_CHECKLIST.items():
        for endpoint, spec in endpoints.items():
            method = spec["method"]
            success = spec["success"]

            # POST → 201 kontrolü
            if method == "POST" and success != 201:
                issues.append(f"{service}: {endpoint} should return 201, not {success}")

            # DELETE → 204 kontrolü
            if method == "DELETE" and success != 204:
                issues.append(f"{service}: {endpoint} should return 204, not {success}")

    return {
        "compliant": len(issues) == 0,
        "issues": issues,
        "total_endpoints": sum(len(v) for v in RMM_CHECKLIST.values()),
    }


if __name__ == "__main__":
    result = verify_rmm_compliance()
    print(f"RMM Level 2 Compliance: {'PASS ✅' if result['compliant'] else 'FAIL ❌'}")
    print(f"Total Endpoints: {result['total_endpoints']}")
    for issue in result["issues"]:
        print(f"  ⚠️ {issue}")
