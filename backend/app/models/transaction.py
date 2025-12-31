"""
Transaction Model
SQLAlchemy model for financial transactions and fraud detection.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, String, Float, Boolean, DateTime, Text, JSON,
    Integer, ForeignKey, Index, Enum as SQLEnum, Numeric
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from app.core.database import Base


class TransactionType(str, enum.Enum):
    """Transaction type enumeration."""
    P2P = "p2p"  # Person to Person
    P2M = "p2m"  # Person to Merchant
    BILL_PAYMENT = "bill_payment"
    MOBILE_RECHARGE = "mobile_recharge"
    BANK_TRANSFER = "bank_transfer"
    CASH_IN = "cash_in"
    CASH_OUT = "cash_out"
    INTERNATIONAL = "international"
    SALARY = "salary"
    REFUND = "refund"


class TransactionStatus(str, enum.Enum):
    """Transaction status enumeration."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    UNDER_REVIEW = "under_review"
    COMPLETED = "completed"
    FAILED = "failed"
    REVERSED = "reversed"


class RiskLevel(str, enum.Enum):
    """Risk level classification."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Transaction(Base):
    """Transaction model for payment processing and fraud detection."""
    
    __tablename__ = "transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_ref = Column(String(50), unique=True, nullable=False, index=True)
    
    # Transaction Details
    amount = Column(Numeric(precision=15, scale=2), nullable=False)
    currency = Column(String(3), default="BDT", nullable=False)
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    
    # Sender Information
    sender_account = Column(String(50), nullable=False, index=True)
    sender_name = Column(String(255), nullable=True)
    sender_bank = Column(String(100), nullable=True)
    sender_type = Column(String(50), nullable=True)  # individual, business
    
    # Receiver Information
    receiver_account = Column(String(50), nullable=False, index=True)
    receiver_name = Column(String(255), nullable=True)
    receiver_bank = Column(String(100), nullable=True)
    receiver_type = Column(String(50), nullable=True)
    
    # Device & Location Information
    device_id = Column(String(255), nullable=True)
    device_type = Column(String(50), nullable=True)  # mobile, web, api
    device_fingerprint = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    ip_country = Column(String(2), nullable=True)
    ip_city = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Status & Processing
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING)
    processing_time_ms = Column(Integer, nullable=True)
    failure_reason = Column(Text, nullable=True)
    
    # Fraud Detection Results
    risk_score = Column(Float, nullable=True)  # 0.0 to 1.0
    risk_level = Column(SQLEnum(RiskLevel), nullable=True)
    fraud_flags = Column(JSON, nullable=True)  # List of triggered flags
    ml_model_version = Column(String(50), nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    # Decision
    decision = Column(String(20), nullable=True)  # APPROVE, REJECT, REVIEW
    decision_reason = Column(Text, nullable=True)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    
    # Additional Data
    description = Column(Text, nullable=True)
    reference_id = Column(String(100), nullable=True)  # External reference
    metadata_ = Column("metadata", JSON, nullable=True)
    
    # Feature Store (for ML)
    ml_features = Column(JSON, nullable=True)
    
    # Timestamps
    initiated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    alerts = relationship("Alert", back_populates="transaction", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_transactions_sender', 'sender_account'),
        Index('idx_transactions_receiver', 'receiver_account'),
        Index('idx_transactions_status', 'status'),
        Index('idx_transactions_risk_level', 'risk_level'),
        Index('idx_transactions_initiated_at', 'initiated_at'),
        Index('idx_transactions_amount', 'amount'),
        Index('idx_transactions_type_status', 'transaction_type', 'status'),
    )
    
    def __repr__(self):
        return f"<Transaction {self.transaction_ref}>"
    
    @property
    def is_high_risk(self) -> bool:
        """Check if transaction is high risk."""
        return self.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
    
    @property
    def requires_review(self) -> bool:
        """Check if transaction requires manual review."""
        return self.status == TransactionStatus.UNDER_REVIEW


class Alert(Base):
    """Alert model for fraud detection notifications."""
    
    __tablename__ = "alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=False)
    
    alert_type = Column(String(50), nullable=False)  # fraud, velocity, pattern, etc.
    alert_code = Column(String(20), nullable=False)
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Alert details
    triggered_rules = Column(JSON, nullable=True)
    evidence = Column(JSON, nullable=True)
    
    # Status
    status = Column(String(20), default="open")  # open, acknowledged, resolved, false_positive
    acknowledged_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transaction = relationship("Transaction", back_populates="alerts")
    
    __table_args__ = (
        Index('idx_alerts_transaction_id', 'transaction_id'),
        Index('idx_alerts_status', 'status'),
        Index('idx_alerts_severity', 'severity'),
        Index('idx_alerts_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Alert {self.alert_code} for {self.transaction_id}>"


class TransactionPattern(Base):
    """Model for storing user transaction patterns for ML."""
    
    __tablename__ = "transaction_patterns"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(String(50), nullable=False, index=True)
    
    # Statistical patterns
    avg_transaction_amount = Column(Float, nullable=True)
    std_transaction_amount = Column(Float, nullable=True)
    max_transaction_amount = Column(Float, nullable=True)
    min_transaction_amount = Column(Float, nullable=True)
    
    # Frequency patterns
    avg_daily_transactions = Column(Float, nullable=True)
    avg_weekly_transactions = Column(Float, nullable=True)
    avg_monthly_transactions = Column(Float, nullable=True)
    
    # Time patterns
    typical_hours = Column(JSON, nullable=True)  # List of typical transaction hours
    typical_days = Column(JSON, nullable=True)  # List of typical transaction days
    
    # Device patterns
    known_devices = Column(JSON, nullable=True)
    known_ips = Column(JSON, nullable=True)
    known_locations = Column(JSON, nullable=True)
    
    # Receiver patterns
    frequent_receivers = Column(JSON, nullable=True)
    
    # Risk indicators
    historical_fraud_count = Column(Integer, default=0)
    chargeback_count = Column(Integer, default=0)
    
    # Update tracking
    last_transaction_at = Column(DateTime, nullable=True)
    pattern_updated_at = Column(DateTime, default=datetime.utcnow)
    total_transactions = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_patterns_account_id', 'account_id'),
        Index('idx_patterns_updated_at', 'pattern_updated_at'),
    )
    
    def __repr__(self):
        return f"<TransactionPattern for {self.account_id}>"
