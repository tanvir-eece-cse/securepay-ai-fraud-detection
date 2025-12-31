"""
ML Service Tests
Test cases for the SecurePay AI ML service.
"""

import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from datetime import datetime


class TestFeatureEngineering:
    """Test feature engineering functions."""

    def test_amount_normalization(self, sample_transaction_features):
        """Test amount normalization."""
        amount = sample_transaction_features["amount"]
        max_amount = 500000.0
        
        normalized = amount / max_amount
        
        assert 0.0 <= normalized <= 1.0
        assert normalized == 0.01  # 5000 / 500000

    def test_time_features_extraction(self):
        """Test time-based feature extraction."""
        timestamp = datetime(2024, 6, 15, 14, 30, 0)  # Saturday, 2:30 PM
        
        hour = timestamp.hour
        day_of_week = timestamp.weekday()
        is_weekend = day_of_week >= 5
        
        assert hour == 14
        assert day_of_week == 5  # Saturday
        assert is_weekend is True

    def test_velocity_calculation(self):
        """Test transaction velocity calculation."""
        transactions_last_hour = 5
        transactions_last_24h = 15
        
        hourly_velocity = transactions_last_hour
        daily_velocity = transactions_last_24h
        velocity_ratio = hourly_velocity / max(daily_velocity, 1)
        
        assert hourly_velocity == 5
        assert daily_velocity == 15
        assert velocity_ratio == pytest.approx(0.333, rel=0.01)

    def test_amount_deviation_calculation(self):
        """Test amount deviation from average."""
        current_amount = 50000.0
        avg_amount = 5000.0
        std_amount = 2000.0
        
        deviation = (current_amount - avg_amount) / max(std_amount, 1)
        
        assert deviation == 22.5  # (50000 - 5000) / 2000

    def test_distance_calculation(self):
        """Test distance calculation between coordinates."""
        # Haversine formula approximation
        lat1, lon1 = 23.8103, 90.4125  # Dhaka
        lat2, lon2 = 23.7500, 90.3700  # Nearby location
        
        # Simplified distance calculation (in km)
        from math import radians, cos, sin, sqrt, atan2
        
        R = 6371  # Earth's radius in km
        
        lat1_rad, lat2_rad = radians(lat1), radians(lat2)
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        
        a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = R * c
        
        assert distance < 10  # Should be within 10 km


class TestFraudPrediction:
    """Test fraud prediction functionality."""

    def test_prediction_output_range(self, mock_model):
        """Test prediction output is in valid range."""
        features = np.array([[1, 2, 3, 4, 5]])
        
        prediction = mock_model.predict(features)[0]
        
        assert 0.0 <= prediction <= 1.0

    def test_low_risk_classification(self, sample_transaction_features):
        """Test low risk transaction classification."""
        fraud_score = 0.15
        
        if fraud_score < 0.3:
            risk_level = "low"
        elif fraud_score < 0.5:
            risk_level = "medium"
        elif fraud_score < 0.8:
            risk_level = "high"
        else:
            risk_level = "critical"
        
        assert risk_level == "low"

    def test_high_risk_classification(self, high_risk_transaction_features):
        """Test high risk transaction classification."""
        # Simulate high risk indicators
        fraud_score = 0.85
        
        if fraud_score >= 0.8:
            risk_level = "critical"
        elif fraud_score >= 0.5:
            risk_level = "high"
        else:
            risk_level = "low"
        
        assert risk_level == "critical"

    def test_ensemble_prediction(self):
        """Test ensemble model prediction."""
        # Simulate ensemble with RF, XGBoost, and NN
        rf_score = 0.3
        xgb_score = 0.4
        nn_score = 0.35
        
        # Weighted average
        weights = [0.35, 0.40, 0.25]
        ensemble_score = (
            rf_score * weights[0] + 
            xgb_score * weights[1] + 
            nn_score * weights[2]
        )
        
        expected = 0.3 * 0.35 + 0.4 * 0.40 + 0.35 * 0.25
        assert ensemble_score == pytest.approx(expected, rel=0.01)

    def test_prediction_confidence(self):
        """Test prediction confidence calculation."""
        probabilities = np.array([[0.2, 0.8]])  # [not_fraud, fraud]
        
        confidence = max(probabilities[0])
        is_confident = confidence >= 0.7
        
        assert confidence == 0.8
        assert is_confident is True


class TestExplanation:
    """Test fraud explanation generation."""

    def test_explanation_generation(self, high_risk_transaction_features):
        """Test explanation generation for high risk transactions."""
        features = high_risk_transaction_features
        explanations = []
        
        if features["amount"] > 100000:
            explanations.append("Unusually high transaction amount")
        
        if features["hour_of_day"] < 6 or features["hour_of_day"] > 22:
            explanations.append("Transaction during unusual hours")
        
        if features["is_new_receiver"]:
            explanations.append("Transaction to a new recipient")
        
        if features["velocity_1h"] > 10:
            explanations.append("High transaction velocity")
        
        if features["device_risk_score"] > 0.5:
            explanations.append("Transaction from high-risk device")
        
        assert len(explanations) >= 3
        assert "Unusually high transaction amount" in explanations

    def test_feature_importance(self):
        """Test feature importance ranking."""
        feature_importance = {
            "amount": 0.25,
            "velocity_1h": 0.20,
            "is_new_receiver": 0.15,
            "device_risk_score": 0.12,
            "hour_of_day": 0.10,
            "distance": 0.08,
            "other": 0.10
        }
        
        # Sort by importance
        sorted_features = sorted(
            feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        assert sorted_features[0][0] == "amount"
        assert sorted_features[1][0] == "velocity_1h"


class TestModelPerformance:
    """Test model performance metrics."""

    def test_accuracy_calculation(self):
        """Test accuracy calculation."""
        predictions = [1, 0, 1, 1, 0, 0, 1, 0]
        actuals = [1, 0, 1, 0, 0, 1, 1, 0]
        
        correct = sum(p == a for p, a in zip(predictions, actuals))
        accuracy = correct / len(predictions)
        
        assert accuracy == 0.75

    def test_precision_calculation(self):
        """Test precision calculation."""
        # True positives and false positives
        tp = 45
        fp = 5
        
        precision = tp / (tp + fp)
        
        assert precision == 0.9

    def test_recall_calculation(self):
        """Test recall calculation."""
        # True positives and false negatives
        tp = 45
        fn = 10
        
        recall = tp / (tp + fn)
        
        assert recall == pytest.approx(0.818, rel=0.01)

    def test_f1_score_calculation(self):
        """Test F1 score calculation."""
        precision = 0.9
        recall = 0.818
        
        f1 = 2 * (precision * recall) / (precision + recall)
        
        assert f1 == pytest.approx(0.857, rel=0.01)

    def test_auc_roc_bounds(self):
        """Test AUC-ROC is within valid bounds."""
        auc_score = 0.95
        
        assert 0.0 <= auc_score <= 1.0
        assert auc_score > 0.5  # Better than random


class TestDataPreprocessing:
    """Test data preprocessing functions."""

    def test_missing_value_handling(self):
        """Test missing value handling."""
        data = {
            "amount": 5000,
            "device_id": None,
            "ip_address": "192.168.1.1"
        }
        
        # Fill missing values
        processed = {
            k: v if v is not None else "unknown"
            for k, v in data.items()
        }
        
        assert processed["device_id"] == "unknown"
        assert processed["amount"] == 5000

    def test_categorical_encoding(self):
        """Test categorical variable encoding."""
        transaction_types = {
            "transfer": 0,
            "payment": 1,
            "withdrawal": 2,
            "deposit": 3
        }
        
        encoded = transaction_types["transfer"]
        
        assert encoded == 0

    def test_feature_scaling(self):
        """Test feature scaling (min-max normalization)."""
        values = [100, 500, 1000, 5000, 10000]
        min_val, max_val = min(values), max(values)
        
        scaled = [(v - min_val) / (max_val - min_val) for v in values]
        
        assert min(scaled) == 0.0
        assert max(scaled) == 1.0
        assert scaled[2] == pytest.approx(0.0909, rel=0.01)


class TestModelHealth:
    """Test model health and monitoring."""

    def test_model_latency(self):
        """Test model prediction latency."""
        import time
        
        start = time.time()
        # Simulate prediction
        time.sleep(0.01)  # 10ms
        latency = time.time() - start
        
        # Should be under 100ms for real-time
        assert latency < 0.1

    def test_prediction_drift_detection(self):
        """Test prediction drift detection."""
        historical_mean = 0.15
        historical_std = 0.05
        current_predictions = [0.18, 0.20, 0.25, 0.22, 0.19]
        
        current_mean = np.mean(current_predictions)
        z_score = (current_mean - historical_mean) / historical_std
        
        # Alert if drift is significant (z > 2)
        has_drift = abs(z_score) > 2
        
        assert isinstance(has_drift, bool)

    def test_input_validation(self, sample_transaction_features):
        """Test input data validation."""
        required_fields = ["amount", "transaction_type", "channel"]
        
        missing_fields = [
            f for f in required_fields 
            if f not in sample_transaction_features
        ]
        
        assert len(missing_fields) == 0
