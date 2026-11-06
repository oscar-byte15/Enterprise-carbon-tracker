from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies import get_current_enterprise_id
from .ai_advisor import ai_advisor_service
from .ai_schemas import AIRecommendationsResponse
from .exceptions import (
    AIAdvisorError,
    AnalyticsAggregationError,
    InsufficientDataError,
    InvalidDatePeriodError,
    InvalidMetricError,
    Subsystem3Error,
)

router = APIRouter(
    prefix="/ai",
    tags=["Subsystem 3 - AI Sustainability Advisor"],
)


@router.post("/recommendations", response_model=AIRecommendationsResponse)
def get_ai_recommendations(
    require_data: bool = Query(
        default=False,
        description="Whether to require at least one logged activity record before generating recommendations",
    ),
    enterprise_id: str = Depends(get_current_enterprise_id),
):
    """
    Generate tailored, data-driven carbon reduction recommendations for the enterprise.
    Utilizes live OpenAI generation if configured, or falls back seamlessly to rule-based strategies.
    Strictly isolated by enterprise_id derived from the authenticated JWT.
    """
    try:
        return ai_advisor_service.generate_recommendations(
            enterprise_id=enterprise_id,
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
