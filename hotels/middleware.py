import time
import logging

logger = logging.getLogger(__name__)


class RequestTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        start = time.monotonic()

        response = self.get_response(request)

        elapsed = time.monotonic() - start

        logger.info(
            "%s %s %s %.2f ms",
            request.method,
            request.path,
            response.status_code,
            elapsed * 1000
        )

        return response