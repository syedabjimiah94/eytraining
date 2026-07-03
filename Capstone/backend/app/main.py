from fastapi import FastAPI, Request
from app.config.settings import settings
from app.routers.weather import router as weather_router
from app.routers.health import router as health_router
from app.routers.simulator import router as simulator_router
from app.routers.incidents import router as incidents_router
from app.routers.metrics import router as metrics_router
from app.utils.logger import logger
from app.database.database import init_db
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.latency_middleware import LatencyMiddleware
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.exception_handler import global_exception_handler
from app.routers.request_logs import router as request_logs_router

app = FastAPI(title=settings.APP_NAME, version=settings.API_VERSION)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(LatencyMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_exception_handler(Exception, global_exception_handler)

app.include_router(weather_router)
app.include_router(health_router)
app.include_router(simulator_router)
app.include_router(incidents_router)
app.include_router(metrics_router)
app.include_router(request_logs_router)


@app.on_event("startup")
def startup():
    init_db()
    logger.info("Application Started")


@app.get("/")
def root():
    return {
        "application": settings.APP_NAME,
        "version": settings.API_VERSION,
        "status": "Running",
        "phase": "Phase 2 - Self Healing Workflow",
    }
