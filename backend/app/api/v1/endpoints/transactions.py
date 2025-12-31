"""
Transaction Endpoints  
Fraud detection, transaction management, and review endpoints.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from uuid import UUID
import httpx
import structlog

from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_current_active_user, require_roles, encryption_service
from app.core.logging import audit_logger
from app.models.transaction import Transaction, TransactionStatus, Alert, RiskLevel
from app.models.user import User
from app.schemas.transaction import (
    TransactionAnalyzeRequest, TransactionAnalyzeResponse,
    TransactionResponse, TransactionDetail, TransactionListResponse,
    TransactionReview, BatchTransactionRequest, BatchTransactionResponse
)

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.post("/analyze", response_model=TransactionAnalyzeResponse)
async def analyze_transaction(
    transaction_data: TransactionAnalyzeRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze a transaction for fraud in real-time.
    
    Uses machine learning models to calculate risk score and make decisions.
    Response time target: <100ms
    """
    
    start_time = datetime.utcnow()
    
    try:
        # Call ML service for prediction
        async with httpx.AsyncClient() as client:
            ml_response = await client.post(
                f"{settings.ML_SERVICE_URL}/api/v1/ml/predict",
                json=transaction_data.dict(),
                timeout=settings.ML_SERVICE_TIMEOUT
            )
            
            if ml_response.status_code != 200:
                logger.error(
                    "ML service error",
                    status_code=ml_response.status_code,
                    response=ml_response.text
                )
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Fraud detection service unavailable"
                )
            
            ml_result = ml_response.json()
        
        # Determine decision based on risk score
        risk_score = ml_result["risk_score"]
        
        if risk_score >= settings.FRAUD_SCORE_THRESHOLD_HIGH:
            decision = "REJECT"
            risk_level = RiskLevel.CRITICAL if risk_score >= 0.9 else RiskLevel.HIGH
        elif risk_score >= settings.FRAUD_SCORE_THRESHOLD_MEDIUM:
            decision = "REVIEW"
            risk_level = RiskLevel.MEDIUM
        else:
            decision = "APPROVE"
            risk_level = RiskLevel.LOW
        
        # Save transaction to database
        transaction = Transaction(
            transaction_ref=transaction_data.transaction_id,
            amount=transaction_data.amount,
            currency=transaction_data.currency,
            transaction_type=transaction_data.transaction_type,
            sender_account=encryption_service.hash_data(transaction_data.sender_account),
            sender_name=transaction_data.sender_name,
            receiver_account=encryption_service.hash_data(transaction_data.receiver_account),
            receiver_name=transaction_data.receiver_name,
            device_fingerprint=transaction_data.device_fingerprint,
            device_type=transaction_data.device_type,
            ip_address=transaction_data.ip_address,
            latitude=transaction_data.latitude,
            longitude=transaction_data.longitude,
            risk_score=risk_score,
            risk_level=risk_level,
            fraud_flags=ml_result.get("flags", []),
            ml_model_version=ml_result.get("model_version"),
            confidence_score=ml_result.get("confidence"),
            decision=decision,
            decision_reason=ml_result.get("decision_reason"),
            status=TransactionStatus.APPROVED if decision == "APPROVE" 
                   else TransactionStatus.REJECTED if decision == "REJECT"
                   else TransactionStatus.UNDER_REVIEW,
            ml_features=ml_result.get("features"),
            metadata_=transaction_data.metadata,
            initiated_at=transaction_data.timestamp or datetime.utcnow()
        )
        
        db.add(transaction)
        
        # Create alert if high risk
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            alert = Alert(
                transaction_id=transaction.id,
                alert_type="fraud",
                alert_code=f"FRAUD_{risk_level.value.upper()}",
                severity=risk_level.value,
                title=f"High Risk Transaction Detected",
                description=f"Transaction {transaction_data.transaction_id} flagged as {risk_level.value} risk",
                triggered_rules=ml_result.get("flags", []),
                evidence=ml_result.get("explanation", {})
            )
            db.add(alert)
        
        await db.commit()
        await db.refresh(transaction)
        
        # Calculate processing time
        processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        # Audit log
        audit_logger.log_transaction(
            transaction_id=transaction_data.transaction_id,
            user_id=current_user.get("sub"),
            action="analyze",
            amount=float(transaction_data.amount),
            currency=transaction_data.currency,
            risk_score=risk_score,
            decision=decision
        )
        
        logger.info(
            "Transaction analyzed",
            transaction_id=transaction_data.transaction_id,
            risk_score=risk_score,
            decision=decision,
            processing_time_ms=processing_time_ms
        )
        
        return TransactionAnalyzeResponse(
            transaction_id=transaction_data.transaction_id,
            risk_score=risk_score,
            risk_level=risk_level,
            decision=decision,
            confidence=ml_result.get("confidence", 0.0),
            flags=ml_result.get("flags", []),
            explanation=ml_result.get("explanation", {}),
            processing_time_ms=processing_time_ms,
            model_version=ml_result.get("model_version", "1.0.0")
        )
        
    except httpx.TimeoutException:
        logger.error("ML service timeout", transaction_id=transaction_data.transaction_id)
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Fraud detection service timeout"
        )
    except Exception as e:
        logger.error(
            "Transaction analysis failed",
            transaction_id=transaction_data.transaction_id,
            error=str(e),
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transaction analysis failed"
        )


@router.get("", response_model=TransactionListResponse)
async def list_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    status_filter: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List transactions with pagination and filtering.
    """
    
    # Build query
    query = select(Transaction)
    
    if status_filter:
        query = query.where(Transaction.status == status_filter)
    
    if risk_level:
        query = query.where(Transaction.risk_level == risk_level)
    
    # Get total count
    count_query = select(func.count()).select_from(Transaction)
    if status_filter:
        count_query = count_query.where(Transaction.status == status_filter)
    if risk_level:
        count_query = count_query.where(Transaction.risk_level == risk_level)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Get paginated results
    query = query.order_by(desc(Transaction.initiated_at))
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    transactions = result.scalars().all()
    
    # Mask sensitive data
    masked_transactions = []
    for txn in transactions:
        txn_dict = TransactionResponse.from_orm(txn)
        masked_transactions.append(txn_dict)
    
    total_pages = (total + page_size - 1) // page_size
    
    return TransactionListResponse(
        transactions=masked_transactions,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{transaction_id}", response_model=TransactionDetail)
async def get_transaction(
    transaction_id: UUID,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific transaction.
    """
    
    result = await db.execute(
        select(Transaction).where(Transaction.id == transaction_id)
    )
    transaction = result.scalar_one_or_none()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    # Audit log
    audit_logger.log_data_access(
        user_id=current_user.get("sub"),
        resource_type="transaction",
        resource_id=str(transaction_id),
        action="read"
    )
    
    return TransactionDetail.from_orm(transaction)


@router.put("/{transaction_id}/review")
async def review_transaction(
    transaction_id: UUID,
    review_data: TransactionReview,
    current_user: dict = Depends(require_roles("admin", "analyst")),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually review a flagged transaction.
    Requires analyst or admin role.
    """
    
    result = await db.execute(
        select(Transaction).where(Transaction.id == transaction_id)
    )
    transaction = result.scalar_one_or_none()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    if transaction.status != TransactionStatus.UNDER_REVIEW:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction is not under review"
        )
    
    # Update transaction
    transaction.decision = review_data.decision
    transaction.decision_reason = review_data.reason
    transaction.reviewed_by = UUID(current_user.get("sub"))
    transaction.reviewed_at = datetime.utcnow()
    
    if review_data.decision == "APPROVE":
        transaction.status = TransactionStatus.APPROVED
    elif review_data.decision == "REJECT":
        transaction.status = TransactionStatus.REJECTED
    
    await db.commit()
    
    # Audit log
    audit_logger.log_transaction(
        transaction_id=str(transaction_id),
        user_id=current_user.get("sub"),
        action="review",
        decision=review_data.decision
    )
    
    logger.info(
        "Transaction reviewed",
        transaction_id=str(transaction_id),
        reviewer_id=current_user.get("sub"),
        decision=review_data.decision
    )
    
    return {"message": "Transaction reviewed successfully", "decision": review_data.decision}


@router.post("/batch-analyze", response_model=BatchTransactionResponse)
async def batch_analyze(
    batch_request: BatchTransactionRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze multiple transactions in batch.
    Maximum 100 transactions per request.
    """
    
    start_time = datetime.utcnow()
    results = []
    approved = rejected = review = 0
    
    for txn_data in batch_request.transactions:
        try:
            # Call individual analyze function
            result = await analyze_transaction(txn_data, current_user, db)
            results.append(result)
            
            if result.decision == "APPROVE":
                approved += 1
            elif result.decision == "REJECT":
                rejected += 1
            else:
                review += 1
                
        except Exception as e:
            logger.error(
                "Batch transaction analysis failed",
                transaction_id=txn_data.transaction_id,
                error=str(e)
            )
            # Continue with next transaction
            continue
    
    processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
    
    return BatchTransactionResponse(
        results=results,
        total_processed=len(results),
        total_approved=approved,
        total_rejected=rejected,
        total_review=review,
        processing_time_ms=processing_time_ms
    )
