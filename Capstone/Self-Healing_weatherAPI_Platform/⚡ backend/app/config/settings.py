from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Self Healing Weather API"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    API_VERSION: str = "v1"

    # Provider + resilience
    WEATHER_PROVIDER_MODE: str = "live"  # live | mock
    PRIMARY_RETRY_COUNT: int = 3
    PRIMARY_RETRY_DELAY_SECONDS: float = 0.5
    PRIMARY_TIMEOUT_SECONDS: float = 5.0

    # Open-Meteo endpoints. Defaults call the real API directly.
    # For demo provider-unreachable testing, point these to tools/openmeteo_gateway.py.
    OPENMETEO_GEO_URL: str = "https://geocoding-api.open-meteo.com/v1/search"
    OPENMETEO_WEATHER_URL: str = "https://api.open-meteo.com/v1/forecast"

    # Optional LLM + tracing
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    LANGCHAIN_TRACING_V2: str = "false"
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "selfHealingWeatherAPI"

    # Optional email ticket demo
    RESEND_API_KEY: str | None = None
    INCIDENT_FROM_EMAIL: str = "Self Healing Demo <onboarding@resend.dev>"
    INCIDENT_TO_EMAIL: str | None = None

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

import os

os.environ["LANGCHAIN_TRACING_V2"] = settings.LANGCHAIN_TRACING_V2
os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT
