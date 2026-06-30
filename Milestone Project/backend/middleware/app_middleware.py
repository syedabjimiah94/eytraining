import os
import time
import uuid
import logging

from starlette.middleware.base import BaseHTTPMiddleware


# -------------------------------
# Create logs directory
# -------------------------------
os.makedirs("logs", exist_ok=True)


# -------------------------------
# Configure Logger
# -------------------------------
logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("AutoHealAI")


# -------------------------------
# App Middleware
# -------------------------------
class AppMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):

        # Generate Request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        start_time = time.time()

        logger.info("=" * 70)
        logger.info(f"Request ID  : {request_id}")
        logger.info(f"Method      : {request.method}")
        logger.info(f"URL         : {request.url.path}")
        logger.info(f"Client IP   : {request.client.host}")

        try:

            response = await call_next(request)

        except Exception as e:

            logger.exception(f"Unhandled Exception : {str(e)}")
            raise

        process_time = time.time() - start_time

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.4f}"

        logger.info(f"Status Code : {response.status_code}")
        logger.info(f"Time Taken  : {process_time:.4f} sec")
        logger.info("=" * 70)

        # print("=" * 70)
        # print(f"Request ID  : {request_id}")
        # print(f"URL         : {request.url.path}")
        # print(f"Status      : {response.status_code}")
        # print(f"Time Taken  : {process_time:.4f} sec")
        # print("=" * 70)

        return response