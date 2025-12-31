"""Analytics and reporting endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.transaction import Transaction, RiskLevel, TransactionStatus
from app.schemas.transaction import TransactionStats, DailyStats, AnalyticsResponse

router = APIRouter()


@router.get("/dashboard", response_model=AnalyticsResponse)
async def get_dashboard_analytics(
    period: str = Query("week", regex="^(day|week|month)$"),
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics dashboard data."""
    
    # Calculate date range
    now = datetime.utcnow()
    if period == "day":
        start_date = now - timedelta(days=1)
    elif period == "week":
        start_date = now - timedelta(days=7)
    else:  # month
        start_date = now - timedelta(days=30)
    
    # Overall statistics
    stats_query = select(
        func.count(Transaction.id).label("total"),
        func.sum(Transaction.amount).label("total_amount"),
        func.avg(Transaction.amount).label("avg_amount"),
    ).where(Transaction.initiated_at >= start_date)
    
    stats_result = await db.execute(stats_query)
    stats_row = stats_result.first()
    
    # Risk level counts
    risk_counts = {}
    for risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]:
        count_result = await db.execute(
            select(func.count())
            .select_from(Transaction)
            .where(and_(
                Transaction.initiated_at >= start_date,
                Transaction.risk_level == risk_level
            ))
        )
        risk_counts[risk_level.value] = count_result.scalar()
    
    # Decision counts
    decision_counts = {}
    for status in [TransactionStatus.APPROVED, TransactionStatus.REJECTED, TransactionStatus.UNDER_REVIEW]:
        count_result = await db.execute(
            select(func.count())
            .select_from(Transaction)
            .where(and_(
                Transaction.initiated_at >= start_date,
                Transaction.status == status
            ))
        )
        decision_counts[status.value] = count_result.scalar()
    
    summary = TransactionStats(
        total_transactions=stats_row.total or 0,
        total_amount=float(stats_row.total_amount or 0),
        avg_amount=float(stats_row.avg_amount or 0),
        high_risk_count=risk_counts.get("high", 0) + risk_counts.get("critical", 0),
        medium_risk_count=risk_counts.get("medium", 0),
        low_risk_count=risk_counts.get("low", 0),
        approved_count=decision_counts.get("approved", 0),
        rejected_count=decision_counts.get("rejected", 0),
        review_count=decision_counts.get("under_review", 0)
    )
    
    return AnalyticsResponse(
        period=period,
        summary=summary,
        daily_breakdown=[],
        top_risk_factors=[],
        trend_comparison={}
    )
