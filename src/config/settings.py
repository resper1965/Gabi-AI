"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: settings.py                                                           │
│ Developed by: Davidson Gomes                                                 │
│ Creation date: May 13, 2025                                                  │
│ Contact: contato@evolution-api.com                                           │
├──────────────────────────────────────────────────────────────────────────────┤
│ @copyright © Evolution API 2025. All rights reserved.                        │
│ Licensed under the Apache License, Version 2.0                               │
│                                                                              │
│ You may not use this file except in compliance with the License.             │
│ You may obtain a copy of the License at                                      │
│                                                                              │
│    http://www.apache.org/licenses/LICENSE-2.0                                │
│                                                                              │
│ Unless required by applicable law or agreed to in writing, software          │
│ distributed under the License is distributed on an "AS IS" BASIS,            │
│ WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.     │
│ See the License for the specific language governing permissions and          │
│ limitations under the License.                                               │
├──────────────────────────────────────────────────────────────────────────────┤
│ @important                                                                   │
│ For any future changes to the code in this file, it is recommended to        │
│ include, together with the modification, the information of the developer    │
│ who changed it and the date of modification.                                 │
└──────────────────────────────────────────────────────────────────────────────┘
"""

import os
from typing import Optional, List
from pydantic_settings import BaseSettings
import secrets
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Project settings"""

    # API settings
    API_TITLE: str = os.getenv("API_TITLE", "Evo AI API")
    API_DESCRIPTION: str = os.getenv("API_DESCRIPTION", "API for executing AI agents")
    API_VERSION: str = os.getenv("API_VERSION", "1.0.0")
    API_URL: str = os.getenv("API_URL", "http://localhost:8000")

    # Organization settings
    ORGANIZATION_NAME: str = os.getenv("ORGANIZATION_NAME", "Evo AI")
    ORGANIZATION_URL: str = os.getenv(
        "ORGANIZATION_URL", "https://evoai.evoapicloud.com"
    )

    # Database settings
    POSTGRES_CONNECTION_STRING: str = os.getenv(
        "POSTGRES_CONNECTION_STRING", "postgresql://postgres:root@localhost:5432/evo_ai"
    )

    # AI engine settings
    AI_ENGINE: str = os.getenv("AI_ENGINE", "adk")

    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR: str = "logs"

    # Redis settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    REDIS_SSL: bool = os.getenv("REDIS_SSL", "false").lower() == "true"
    REDIS_KEY_PREFIX: str = os.getenv("REDIS_KEY_PREFIX", "evoai:")
    REDIS_TTL: int = int(os.getenv("REDIS_TTL", 3600))

    # Tool cache TTL in seconds (1 hour)
    TOOLS_CACHE_TTL: int = int(os.getenv("TOOLS_CACHE_TTL", 3600))

    # JWT settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_TIME: int = int(os.getenv("JWT_EXPIRATION_TIME", 3600))

    # Encryption settings
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", secrets.token_urlsafe(32))

    # Email provider settings
    EMAIL_PROVIDER: str = os.getenv("EMAIL_PROVIDER", "sendgrid")

    # SendGrid settings
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "noreply@yourdomain.com")

    # SMTP settings
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    SMTP_USE_SSL: bool = os.getenv("SMTP_USE_SSL", "false").lower() == "true"
    SMTP_FROM: str = os.getenv("SMTP_FROM", "")

    APP_URL: str = os.getenv("APP_URL", "http://localhost:8000")

    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # CORS settings
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "*").split(",")

    # Token settings
    TOKEN_EXPIRY_HOURS: int = int(
        os.getenv("TOKEN_EXPIRY_HOURS", 24)
    )  # Verification/reset tokens

    # Security settings
    PASSWORD_MIN_LENGTH: int = int(os.getenv("PASSWORD_MIN_LENGTH", 8))
    MAX_LOGIN_ATTEMPTS: int = int(os.getenv("MAX_LOGIN_ATTEMPTS", 5))
    LOGIN_LOCKOUT_MINUTES: int = int(os.getenv("LOGIN_LOCKOUT_MINUTES", 30))

    # Seeder settings
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@evoai.com")
    ADMIN_INITIAL_PASSWORD: str = os.getenv(
        "ADMIN_INITIAL_PASSWORD", "strongpassword123"
    )
    DEMO_EMAIL: str = os.getenv("DEMO_EMAIL", "demo@example.com")
    DEMO_PASSWORD: str = os.getenv("DEMO_PASSWORD", "demo123")
    DEMO_CLIENT_NAME: str = os.getenv("DEMO_CLIENT_NAME", "Demo Client")

    # Langfuse / OpenTelemetry settings
    LANGFUSE_PUBLIC_KEY: str = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    LANGFUSE_SECRET_KEY: str = os.getenv("LANGFUSE_SECRET_KEY", "")
    OTEL_EXPORTER_OTLP_ENDPOINT: str = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


def get_settings() -> Settings:
    return Settings()


settings = get_settings()
