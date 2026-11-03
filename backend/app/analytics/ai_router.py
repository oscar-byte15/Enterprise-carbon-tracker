from fastapi import APIRouter, Depends

from app.dependencies import get_current_enterprise_id
from .ai_advisor import ai_advisor_service
from .ai_schemas import AIRecommendationsResponse

router = APIRouter(
    prefix="/ai",
    tags=["Subsystem 3 - AI Sustainability Advisor"],
)


@router.post("/recommendations", response_model=AIRecommendationsResponse)
def get_ai_recommendations(
    enterprise_id: str = Depends(get_current_enterprise_id),
):
    """
    Generate tailored, data-driven carbon reduction recommendations for the enterprise.
    Utilizes live OpenAI generation if configured, or falls back seamlessly to rule-based strategies.
    Strictly isolated by enterprise_id derived from the authenticated JWT.
    """
    return ai_advisor_service.generate_recommendations(enterprise_id=enterprise_id)
