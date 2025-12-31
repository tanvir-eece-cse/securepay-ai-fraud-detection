"""
ML Service Test Configuration
Pytest fixtures and configuration for ML service tests.
"""

import pytest
import numpy as np
from typing import Dict, Any
from unittest.mock import MagicMock


@pytest.fixture
def sample_transaction_features() -> Dict[str, Any]:
    """Sample transaction features for ML prediction."""
    return {
        "amount": 5000.0,
        "hour_of_day": 14,
        "day_of_week": 2,
        "is_weekend": False,
        "transaction_type": "transfer",
        "channel": "mobile_app",
        "sender_age_days": 365,
        "sender_transaction_count": 150,
        "sender_avg_amount": 3500.0,
        "sender_max_amount": 25000.0,
        "receiver_age_days": 180,
        "receiver_transaction_count": 50,
        "is_new_receiver": False,
        "distance_from_usual_location": 0.5,
        "device_risk_score": 0.1,
        "ip_risk_score": 0.05,
        "velocity_1h": 2,
        "velocity_24h": 5,
        "amount_deviation": 0.5
    }


@pytest.fixture
def high_risk_transaction_features() -> Dict[str, Any]:
    """High risk transaction features for testing."""
    return {
        "amount": 450000.0,
        "hour_of_day": 3,
        "day_of_week": 6,
        "is_weekend": True,
        "transaction_type": "transfer",
        "channel": "web",
        "sender_age_days": 7,
        "sender_transaction_count": 2,
        "sender_avg_amount": 1000.0,
        "sender_max_amount": 5000.0,
        "receiver_age_days": 1,
        "receiver_transaction_count": 0,
        "is_new_receiver": True,
        "distance_from_usual_location": 500.0,
        "device_risk_score": 0.8,
        "ip_risk_score": 0.9,
        "velocity_1h": 15,
        "velocity_24h": 50,
        "amount_deviation": 10.5
    }


@pytest.fixture
def mock_model():
    """Mock ML model for testing."""
    model = MagicMock()
    model.predict = MagicMock(return_value=np.array([0.25]))
    model.predict_proba = MagicMock(return_value=np.array([[0.75, 0.25]]))
    return model


@pytest.fixture
def feature_names():
    """Feature names used by the ML model."""
    return [
        "amount", "hour_of_day", "day_of_week", "is_weekend",
        "transaction_type_encoded", "channel_encoded",
        "sender_age_days", "sender_transaction_count",
        "sender_avg_amount", "sender_max_amount",
        "receiver_age_days", "receiver_transaction_count",
        "is_new_receiver", "distance_from_usual_location",
        "device_risk_score", "ip_risk_score",
        "velocity_1h", "velocity_24h", "amount_deviation"
    ]
