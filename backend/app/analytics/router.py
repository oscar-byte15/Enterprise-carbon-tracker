from fastapi import APIRouter, Depends, Query

from app.dependencies import get_current_enterprise_id
from .schemas import AnalyticsSummaryResponse, AnalyticsTrendsResponse
from .service import analytics_service

router = APIRouter(
    prefix="/analytics",
    tags=["Subsystem 3 - Analytics & Dashboard"],
)


@router.get("/summary", response_model=AnalyticsSummaryResponse)
def get_analytics_summary(
    period: str | None = Query(
        default=None,
        pattern=r"^\d{4}-\d{2}$",
        description="Optional period filter in YYYY-MM format",
    ),
    enterprise_id: str = Depends(get_current_enterprise_id),
):
    """
    Get aggregated carbon footprint metrics for the authenticated enterprise.
    Supports filtering by specific period (YYYY-MM) or retrieving all-time totals.
    """
    return analytics_service.get_summary(
        enterprise_id=enterprise_id,
        period=period,
    )


@router.get("/trends", response_model=AnalyticsTrendsResponse)
def get_analytics_trends(
    year: int | None = Query(
        default=None,
        ge=2000,
        le=2100,
        description="Optional 4-digit year filter (e.g. 2026)",
    ),
    enterprise_id: str = Depends(get_current_enterprise_id),
):
    """
    Get month-over-month carbon emission trends for the authenticated enterprise.
    Optionally filter by calendar year.
    """
    return analytics_service.get_trends(
        enterprise_id=enterprise_id,
        year=year,
    )
