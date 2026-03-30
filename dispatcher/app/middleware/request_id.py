"""
Request ID Middleware — Dispatcher.
Her isteğe benzersiz bir X-Request-ID atar.
Dağıtık izleme (distributed tracing) altyapısı.
"""
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    Her gelen isteğe benzersiz bir Request ID atar.
    - İstemci X-Request-ID gönderirse onu kullanır.
    - Göndermezse UUID v4 üretir.
    - Yanıta da X-Request-ID header'ı ekler.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # İstemci kendi ID'sini gönderebilir
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Request state'e ekle (downstream servisler için)
        request.state.request_id = request_id

        response = await call_next(request)

        # Yanıta ekle
        response.headers["X-Request-ID"] = request_id
        return response
