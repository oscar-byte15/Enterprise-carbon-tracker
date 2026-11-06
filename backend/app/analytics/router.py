from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies import get_current_enterprise_id
from .exceptions import (
    AIAdvisorError,
    AnalyticsAggregationError,
    InsufficientDataError,
    InvalidDatePeriodError,
    InvalidMetricError,
    Subsystem3Error,
)
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
        description="Optional period filter in YYYY-MM format",
    ),
    require_data: bool = Query(
        default=False,
        description="Optional flag to require existing activities (raises 404 if empty)",
    ),
    enterprise_id: str = Depends(get_current_enterprise_id),
):
    """
    Get aggregated carbon footprint metrics for the authenticated enterprise.
    Supports filtering by specific period (YYYY-MM) or retrieving all-time totals.
    """
    try:
        return analytics_service.get_summary(
            enterprise_id=enterprise_id,
            period=period,
            require_data=require_data,
        )
    except (InvalidMetricError, InvalidDatePeriodError) as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error
    except InsufficientDataError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except (AnalyticsAggregationError, AIAdvisorError) as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error
    except Subsystem3Error as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get("/trends", response_model=AnalyticsTrendsResponse)
def get_analytics_trends(
    year: int | None = Query(
        default=None,
        description="Optional 4-digit year filter (e.g. 2026)",
    ),
    require_data: bool = Query(
        default=False,
        description="Optional flag to require existing trend data (raises 404 if empty)",
    ),
    enterprise_id: str = Depends(get_current_enterprise_id),
):
    """
    Get month-over-month carbon emission trends for the authenticated enterprise.
    Optionally filter by calendar year.
    """
    try:
        return analytics_service.get_trends(
            enterprise_id=enterprise_id,
            year=year,
            require_data=require_data,
        )
    except (InvalidMetricError, InvalidDatePeriodError) as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error
    except InsufficientDataError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except (AnalyticsAggregationError, AIAdvisorError) as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error
    except Subsystem3Error as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error
