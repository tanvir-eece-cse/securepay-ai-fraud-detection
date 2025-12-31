"""
Application Configuration
=========================
Centralized config using Pydantic Settings.

Author: Md. Tanvir Hossain

I prefer Pydantic Settings over python-dotenv because it gives us
type validation out of the box. All sensitive values default to 
securely generated tokens but can be overridden via env vars.

Tip: Never commit real secrets - use environment variables in production!
"""

from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator
import secrets


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    APP_NAME: str = "SecurePay AI"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    WORKERS: int = Field(default=4, env="WORKERS")
    
    # Server
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # Security
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(64), env="SECRET_KEY")
    ENCRYPTION_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32), env="ENCRYPTION_KEY")
    
    # JWT Configuration
    JWT_SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(64), env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:password@localhost:5432/securepay",
        env="DATABASE_URL"
    )
    DATABASE_POOL_SIZE: int = Field(default=20, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=10, env="DATABASE_MAX_OVERFLOW")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=100, env="RATE_LIMIT_PER_MINUTE")
    RATE_LIMIT_PER_HOUR: int = Field(default=1000, env="RATE_LIMIT_PER_HOUR")
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="CORS_ORIGINS"
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "securepay.com.bd"],
        env="ALLOWED_HOSTS"
    )
    
    # ML Service
    ML_SERVICE_URL: str = Field(
        default="http://localhost:8001",
        env="ML_SERVICE_URL"
    )
    ML_SERVICE_TIMEOUT: int = Field(default=30, env="ML_SERVICE_TIMEOUT")
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = Field(
        default="localhost:9092",
        env="KAFKA_BOOTSTRAP_SERVERS"
    )
    KAFKA_TOPIC_TRANSACTIONS: str = "transactions"
    KAFKA_TOPIC_ALERTS: str = "alerts"
    
    # Email
    SMTP_HOST: str = Field(default="smtp.gmail.com", env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USER: Optional[str] = Field(default=None, env="SMTP_USER")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    
    # SMS (for Bangladesh - using SSL Wireless or similar)
    SMS_API_URL: str = Field(default="", env="SMS_API_URL")
    SMS_API_KEY: Optional[str] = Field(default=None, env="SMS_API_KEY")
    
    # Audit & Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    AUDIT_LOG_ENABLED: bool = Field(default=True, env="AUDIT_LOG_ENABLED")
    
    # MFA
    MFA_ISSUER: str = "SecurePay AI"
    MFA_VALID_WINDOW: int = 1  # Number of 30-second windows to allow
    
    # Transaction Limits (in BDT)
    MAX_TRANSACTION_AMOUNT: float = 500000.0  # 5 Lakh BDT
    DAILY_TRANSACTION_LIMIT: float = 1000000.0  # 10 Lakh BDT
    
    # Fraud Detection Thresholds
    FRAUD_SCORE_THRESHOLD_HIGH: float = 0.8
    FRAUD_SCORE_THRESHOLD_MEDIUM: float = 0.5
    FRAUD_SCORE_THRESHOLD_LOW: float = 0.3
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
