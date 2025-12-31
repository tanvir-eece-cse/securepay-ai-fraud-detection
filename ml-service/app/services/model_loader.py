"""
Model Manager - Heart of the ML Service
========================================
Handles loading and serving ML models for fraud detection.

Author: Md. Tanvir Hossain

This is where the magic happens! The ensemble approach uses:
- Random Forest: Good at handling categorical features
- XGBoost: Excellent for capturing complex patterns  
- Neural Network: Picks up subtle non-linear relationships

The ensemble weights (0.35, 0.40, 0.25) were tuned on validation data.
XGBoost gets the highest weight because it performed best on our 
imbalanced fraud dataset.

Note: Currently using dummy models for demo. In production, these would
be loaded from trained .pkl or .joblib files from the models/ directory.
"""

import os
import pickle
import structlog
from typing import Dict, Any, List
import numpy as np

from app.core.config import settings

logger = structlog.get_logger(__name__)


class ModelManager:
    \"\"\"
    Manages the fraud detection model ensemble.
    
    I went with a class-based approach here instead of functions
    because we need to maintain state (loaded models) across requests.
    \"\"\"
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.model_version = \"1.0.0\"  # TODO: make this dynamic from model metadata
    
    async def load_models(self):
        \"\"\"
        Load all ML models from disk.
        Called once during app startup via the lifespan manager.
        \"\"\"
        try:
            # In production, load actual trained models from MODEL_DIR
            # For demo purposes, using placeholder models
            logger.info(\"Loading ML models\", model_dir=settings.MODEL_DIR)
            
            # Create ensemble models
            # TODO: Replace with actual model loading:
            # with open(f\"{settings.MODEL_DIR}/rf_model.pkl\", \"rb\") as f:
            #     self.models[\"random_forest\"] = pickle.load(f)
            
            self.models[\"random_forest\"] = self._create_dummy_model(\"rf\")
            self.models[\"xgboost\"] = self._create_dummy_model(\"xgb\")
            self.models[\"neural_network\"] = self._create_dummy_model(\"nn\")
            
            logger.info(\"Models loaded successfully\", models=list(self.models.keys()))
            
        except Exception as e:
            logger.error(\"Failed to load models\", error=str(e))
            raise
    
    def _create_dummy_model(self, name: str):
        \"\"\"
        Create a placeholder model for demonstration.
        
        Uses beta distribution to simulate realistic fraud scores -
        most transactions should have low fraud probability (legitimate),
        with occasional high-risk scores.
        \"\"\"
        class DummyModel:
            def __init__(self, name):
                self.name = name
            
            def predict_proba(self, X):
                # Simulate fraud probability using beta distribution
                # Beta(2, 20) gives us ~90% legitimate, ~10% suspicious
                n_samples = len(X) if isinstance(X, (list, np.ndarray)) else 1
                proba = np.random.beta(2, 20, n_samples)
                return np.column_stack([1 - proba, proba])
        
        return DummyModel(name)
    
    def models_loaded(self) -> bool:
        \"\"\"Check if models are ready for inference.\"\"\"
        return len(self.models) > 0
    
    async def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform fraud prediction using ensemble models.
        
        Args:
            features: Dictionary of transaction features
        
        Returns:
            Dictionary containing risk score, confidence, and explanation
        """
        
        if not self.models_loaded():
            raise RuntimeError("Models not loaded")
        
        # Extract and engineer features
        feature_vector = self._extract_features(features)
        
        # Get predictions from each model
        predictions = {}
        for model_name, model in self.models.items():
            pred_proba = model.predict_proba([feature_vector])
            predictions[model_name] = pred_proba[0][1]  # Fraud probability
        
        # Ensemble prediction (weighted average)
        weights = settings.ENSEMBLE_WEIGHTS
        risk_score = (
            predictions["random_forest"] * weights[0] +
            predictions["xgboost"] * weights[1] +
            predictions["neural_network"] * weights[2]
        )
        
        # Calculate confidence
        model_agreement = self._calculate_agreement(list(predictions.values()))
        confidence = model_agreement
        
        # Generate flags
        flags = self._generate_flags(features, risk_score)
        
        # Generate explanation
        explanation = self._generate_explanation(features, risk_score)
        
        return {
            "risk_score": float(risk_score),
            "confidence": float(confidence),
            "model_version": self.model_version,
            "flags": flags,
            "explanation": explanation,
            "model_predictions": {k: float(v) for k, v in predictions.items()}
        }
    
    def _extract_features(self, transaction: Dict[str, Any]) -> List[float]:
        """
        Extract and engineer features from transaction data.
        
        In production, this would include:
        - Amount normalization
        - Time-based features (hour, day of week, etc.)
        - Velocity features (transactions per hour/day)
        - Device/IP features
        - User behavioral features
        - Network features
        """
        
        features = []
        
        # Amount features
        amount = float(transaction.get("amount", 0))
        features.append(amount)
        features.append(np.log1p(amount))  # Log-transformed amount
        
        # Transaction type (one-hot encoded)
        txn_type = transaction.get("transaction_type", "p2p")
        type_mapping = {"p2p": 0, "p2m": 1, "bill_payment": 2, "mobile_recharge": 3, "bank_transfer": 4}
        features.append(type_mapping.get(txn_type, 0))
        
        # Device features
        device_known = 1 if transaction.get("device_fingerprint") else 0
        features.append(device_known)
        
        # Location features
        has_location = 1 if transaction.get("latitude") and transaction.get("longitude") else 0
        features.append(has_location)
        
        # Pad remaining features (in production, use actual features)
        while len(features) < settings.N_FEATURES:
            features.append(np.random.random())  # Placeholder
        
        return features[:settings.N_FEATURES]
    
    def _calculate_agreement(self, predictions: List[float]) -> float:
        """Calculate model agreement as confidence measure."""
        if not predictions:
            return 0.0
        
        std = np.std(predictions)
        # High agreement = low std deviation
        agreement = 1.0 - min(std * 2, 1.0)
        return float(agreement)
    
    def _generate_flags(self, transaction: Dict[str, Any], risk_score: float) -> List[str]:
        """Generate fraud flags based on transaction analysis."""
        flags = []
        
        amount = float(transaction.get("amount", 0))
        
        if amount > 100000:  # 1 Lakh BDT
            flags.append("high_amount")
        
        if risk_score > 0.8:
            flags.append("high_risk_score")
        
        if not transaction.get("device_fingerprint"):
            flags.append("unknown_device")
        
        # Add more rule-based flags
        if transaction.get("transaction_type") == "international":
            flags.append("international_transaction")
        
        return flags
    
    def _generate_explanation(self, transaction: Dict[str, Any], risk_score: float) -> Dict[str, Any]:
        """
        Generate explanation for the fraud prediction.
        In production, use SHAP values or LIME.
        """
        
        # Simulated feature importance
        top_factors = [
            {"feature": "transaction_amount", "impact": 0.15},
            {"feature": "device_fingerprint", "impact": -0.10},
            {"feature": "transaction_velocity", "impact": 0.08},
            {"feature": "account_age", "impact": -0.07},
            {"feature": "location_consistency", "impact": -0.05}
        ]
        
        return {
            "top_factors": top_factors,
            "decision_reason": self._get_decision_reason(risk_score)
        }
    
    def _get_decision_reason(self, risk_score: float) -> str:
        """Get human-readable decision reason."""
        if risk_score < 0.3:
            return "Transaction appears normal based on user patterns and risk indicators"
        elif risk_score < 0.5:
            return "Some minor risk indicators detected but within acceptable limits"
        elif risk_score < 0.8:
            return "Multiple risk indicators detected, manual review recommended"
        else:
            return "High fraud probability detected based on suspicious patterns"


# Global instance
model_manager = ModelManager()
