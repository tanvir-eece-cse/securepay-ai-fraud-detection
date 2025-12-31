"""
Pydantic Schemas for Transaction Operations
Request and Response schemas for transaction processing and fraud detection.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from uuid import UUID
from decimal import Decimal
from enum import Enum


class TransactionTypeEnum(str, Enum):
    """Transaction type enumeration."""
    P2P = "p2p"
    P2M = "p2m"
    BILL_PAYMENT = "bill_payment"
    MOBILE_RECHARGE = "mobile_recharge"
    BANK_TRANSFER = "bank_transfer"
    CASH_IN = "cash_in"
    CASH_OUT = "cash_out"
    INTERNATIONAL = "international"
    SALARY = "salary"
    REFUND = "refund"


class RiskLevelEnum(str, Enum):
    """Risk level classification."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DecisionEnum(str, Enum):
    """Fraud detection decision."""
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    REVIEW = "REVIEW"


# ============== Transaction Analysis Schemas ==============

class TransactionAnalyzeRequest(BaseModel):
    """Schema for transaction fraud analysis request."""
    transaction_id: str = Field(..., min_length=5, max_length=50)
    amount: Decimal = Field(..., gt=0, le=500000)  # Max 5 Lakh BDT
    currency: str = Field(default="BDT", max_length=3)
    transaction_type: TransactionTypeEnum
    
    # Sender details
    sender_account: str = Field(..., min_length=5, max_length=50)
    sender_name: Optional[str] = Field(None, max_length=255)
    sender_bank: Optional[str] = Field(None, max_length=100)
    
    # Receiver details
    receiver_account: str = Field(..., min_length=5, max_length=50)
    receiver_name: Optional[str] = Field(None, max_length=255)
    receiver_bank: Optional[str] = Field(None, max_length=100)
    
    # Device information
    device_fingerprint: Optional[str] = None
    device_type: Optional[str] = Field(None, max_length=50)
    ip_address: Optional[str] = None
    
    # Location
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    
    # Additional context
    timestamp: Optional[datetime] = None
    description: Optional[str] = Field(None, max_length=500)
    reference_id: Optional[str] = Field(None, max_length=100)
    metadata: Optional[Dict[str, Any]] = None
    
    @validator("sender_account", "receiver_account")
    def validate_account(cls, v):
        """Basic account validation."""
        # Remove spaces and validate
        v = v.replace(" ", "")
        return v


class FraudExplanation(BaseModel):
    """Schema for fraud detection explanation."""
    top_factors: List[Dict[str, Any]]
    rule_matches: Optional[List[str]] = None
    anomaly_details: Optional[Dict[str, Any]] = None


class TransactionAnalyzeResponse(BaseModel):
    """Schema for transaction fraud analysis response."""
    transaction_id: str
    risk_score: float = Field(..., ge=0, le=1)
    risk_level: RiskLevelEnum
    decision: DecisionEnum
    confidence: float = Field(..., ge=0, le=1)
    flags: List[str] = []
    explanation: FraudExplanation
    processing_time_ms: int
    model_version: str
    
    class Config:
        from_attributes = True


# ============== Transaction CRUD Schemas ==============

class TransactionCreate(BaseModel):
    """Schema for creating a transaction record."""
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(default="BDT")
    transaction_type: TransactionTypeEnum
    sender_account: str
    receiver_account: str
    description: Optional[str] = None
    reference_id: Optional[str] = None


class TransactionResponse(BaseModel):
    """Schema for transaction response."""
    id: UUID
    transaction_ref: str
    amount: float
    currency: str
    transaction_type: str
    sender_account: str  # Will be masked
    receiver_account: str  # Will be masked
    status: str
    risk_score: Optional[float]
    risk_level: Optional[str]
    decision: Optional[str]
    initiated_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class TransactionDetail(TransactionResponse):
    """Detailed transaction response."""
    sender_name: Optional[str]
    receiver_name: Optional[str]
    device_type: Optional[str]
    ip_address: Optional[str]  # Will be partially masked
    fraud_flags: Optional[List[str]]
    decision_reason: Optional[str]
    reviewed_by: Optional[UUID]
    reviewed_at: Optional[datetime]
    processing_time_ms: Optional[int]
    created_at: datetime


class TransactionListResponse(BaseModel):
    """Schema for paginated transaction list."""
    transactions: List[TransactionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class TransactionReview(BaseModel):
    """Schema for manual transaction review."""
    decision: DecisionEnum
    reason: str = Field(..., min_length=10, max_length=1000)
    notes: Optional[str] = None


# ============== Alert Schemas ==============

class AlertResponse(BaseModel):
    """Schema for alert response."""
    id: UUID
    transaction_id: UUID
    alert_type: str
    alert_code: str
    severity: str
    title: str
    description: Optional[str]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class AlertDetail(AlertResponse):
    """Detailed alert response."""
    triggered_rules: Optional[List[str]]
    evidence: Optional[Dict[str, Any]]
    acknowledged_by: Optional[UUID]
    acknowledged_at: Optional[datetime]
    resolved_by: Optional[UUID]
    resolved_at: Optional[datetime]
    resolution_notes: Optional[str]


class AlertUpdate(BaseModel):
    """Schema for alert status update."""
    status: str = Field(..., pattern="^(acknowledged|resolved|false_positive)$")
    notes: Optional[str] = Field(None, max_length=1000)


class AlertListResponse(BaseModel):
    """Schema for paginated alert list."""
    alerts: List[AlertResponse]
    total: int
    page: int
    page_size: int


# ============== Analytics Schemas ==============

class TransactionStats(BaseModel):
    """Transaction statistics schema."""
    total_transactions: int
    total_amount: float
    avg_amount: float
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    approved_count: int
    rejected_count: int
    review_count: int


class DailyStats(BaseModel):
    """Daily statistics schema."""
    date: str
    transaction_count: int
    total_amount: float
    fraud_detected: int
    avg_risk_score: float


class AnalyticsResponse(BaseModel):
    """Analytics dashboard response."""
    period: str  # "day", "week", "month"
    summary: TransactionStats
    daily_breakdown: List[DailyStats]
    top_risk_factors: List[Dict[str, Any]]
    trend_comparison: Dict[str, Any]


# ============== Batch Processing Schemas ==============

class BatchTransactionRequest(BaseModel):
    """Schema for batch transaction analysis."""
    transactions: List[TransactionAnalyzeRequest] = Field(..., max_items=100)


class BatchTransactionResponse(BaseModel):
    """Schema for batch analysis response."""
    results: List[TransactionAnalyzeResponse]
    total_processed: int
    total_approved: int
    total_rejected: int
    total_review: int
    processing_time_ms: int
