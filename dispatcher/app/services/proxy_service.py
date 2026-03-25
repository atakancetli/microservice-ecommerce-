"""
ProxyServiceImpl — İstek iletme (proxy) servisi.
IProxyService arayüzünün somut implementasyonu.
SOLID: Single Responsibility — yalnızca istek proxy'leme.
"""
from typing import Any, Dict, Optional

import httpx

from app.models.interfaces import IProxyService, ServiceInfo


class ProxyServiceImpl(IProxyService):
    """
    Gelen istekleri hedef mikroservise iletir ve yanıtı döner.
    httpx AsyncClient kullanarak async HTTP çağrıları yapar.
    """

    DEFAULT_TIMEOUT = 10.0  # saniye

    async def forward_request(
        self,
        method: str,
        target_url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Any] = None,
        query_params: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        İsteği hedef URL'ye iletir.

        Returns:
            {
                "status_code": int,
                "body": Any,
                "headers": dict
            }
        """
        # Proxy'ye özgü olmayan header'ları temizle
        clean_headers = self._clean_headers(headers)

        try:
            async with httpx.AsyncClient(
                timeout=self.DEFAULT_TIMEOUT
            ) as client:
                response = await client.request(
                    method=method,
                    url=target_url,
                    headers=clean_headers,
                    json=body if body else None,
                    params=query_params,
                )

                # Yanıt body'sini parse et
                try:
                    response_body = response.json()
                except Exception:
                    response_body = response.text

                return {
                    "status_code": response.status_code,
                    "body": response_body,
                    "headers": dict(response.headers),
                }

        except httpx.TimeoutException:
            return {
                "status_code": 504,
                "body": {"detail": "Gateway Timeout: Target service did not respond in time"},
                "headers": {},
            }
        except httpx.ConnectError:
            return {
                "status_code": 503,
                "body": {"detail": "Service Unavailable: Cannot connect to target service"},
                "headers": {},
            }
        except Exception as e:
            return {
                "status_code": 502,
                "body": {"detail": f"Bad Gateway: {str(e)}"},
                "headers": {},
            }

    async def health_check(self, service: ServiceInfo) -> bool:
        """
        Bir servisin sağlık durumunu kontrol eder.
        /health endpoint'ine GET isteği gönderir.
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                url = f"{service.base_url}{service.health_endpoint}"
                response = await client.get(url)
                return response.status_code == 200
        except Exception:
            return False

    @staticmethod
    def _clean_headers(
        headers: Optional[Dict[str, str]],
    ) -> Optional[Dict[str, str]]:
        """Proxy'ye özgü olmayan header'ları temizler."""
        if not headers:
            return None

        # Hop-by-hop header'ları çıkar
        skip_headers = {
            "host", "content-length", "transfer-encoding",
            "connection", "keep-alive",
        }
        return {
            k: v for k, v in headers.items()
            if k.lower() not in skip_headers
        }
