from __future__ import annotations

from pydantic import BaseModel, Field


class RecommendationItem(BaseModel):
    id: str
    category: str
    title: str = Field(description="Short actionable title (3-6 words)")
    action: str = Field(description="Concise action description (1-2 sentences maximum)")
    impact: str = Field(description="Impact level: High, Medium, or Low")


class AIRecommendationsResponse(BaseModel):
    enterprise_id: str
    company_name: str
    industry: str
    top_category: str | None = None
    top_category_percentage: float = 0.0
    total_co2e_kg: float = 0.0
    total_activities: int = 0
    is_fallback: bool = False
    model_used: str
    generated_at: str
    recommendations: list[RecommendationItem] = Field(
        default_factory=list,
        description="List of maximum 3 concise dashboard recommendation cards",
    )
