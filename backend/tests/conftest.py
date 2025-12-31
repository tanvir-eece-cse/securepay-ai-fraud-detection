"""
Backend Test Configuration
Pytest fixtures and configuration for backend tests.
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient
from httpx import AsyncClient

# Mock settings before importing app
import sys
from unittest.mock import patch

# Create mock settings
mock_settings = MagicMock()
mock_settings.DATABASE_URL = "postgresql+asyncpg://test:test@localhost/test"
mock_settings.REDIS_URL = "redis://localhost:6379/0"
mock_settings.SECRET_KEY = "test-secret-key-12345678901234567890"
mock_settings.JWT_SECRET_KEY = "test-jwt-secret-key"
mock_settings.JWT_ALGORITHM = "HS256"
mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
mock_settings.REFRESH_TOKEN_EXPIRE_DAYS = 7
mock_settings.CORS_ORIGINS = ["http://localhost:3000"]
mock_settings.ENVIRONMENT = "testing"
mock_settings.DEBUG = True
mock_settings.LOG_LEVEL = "DEBUG"
mock_settings.RATE_LIMIT_PER_MINUTE = 100
mock_settings.RATE_LIMIT_PER_HOUR = 1000
mock_settings.ML_SERVICE_URL = "http://localhost:8001"
mock_settings.ENCRYPTION_KEY = "dGVzdC1lbmNyeXB0aW9uLWtleS0xMjM0NQ=="


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_db():
    """Mock database session."""
    mock_session = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.close = AsyncMock()
    mock_session.execute = AsyncMock()
    mock_session.add = MagicMock()
    return mock_session


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    mock_redis_client = AsyncMock()
    mock_redis_client.get = AsyncMock(return_value=None)
    mock_redis_client.set = AsyncMock(return_value=True)
    mock_redis_client.delete = AsyncMock(return_value=True)
    mock_redis_client.incr = AsyncMock(return_value=1)
    mock_redis_client.expire = AsyncMock(return_value=True)
    return mock_redis_client


@pytest.fixture
def sample_user_data():
    """Sample user data for tests."""
    return {
        "email": "test@example.com",
        "password": "SecurePass123!",
        "full_name": "Test User",
        "phone_number": "+8801712345678"
    }


@pytest.fixture
def sample_transaction_data():
    """Sample transaction data for tests."""
    return {
        "transaction_id": "TXN-001",
        "amount": 5000.00,
        "currency": "BDT",
        "sender_account": "01712345678",
        "receiver_account": "01898765432",
        "transaction_type": "transfer",
        "channel": "mobile_app",
        "device_id": "device-123",
        "ip_address": "192.168.1.1",
        "location": {
            "lat": 23.8103,
            "lon": 90.4125,
            "city": "Dhaka"
        },
        "metadata": {
            "app_version": "2.1.0",
            "os": "Android"
        }
    }


@pytest.fixture
def auth_headers():
    """Sample authorization headers."""
    return {"Authorization": "Bearer test-token-12345"}
