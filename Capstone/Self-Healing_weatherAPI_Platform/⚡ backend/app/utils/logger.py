from loguru import logger
import os

os.makedirs("app/logs", exist_ok=True)

logger.add(
    "app/logs/app.log",
    rotation="5 MB",
    retention="10 days",
    level="INFO"
)