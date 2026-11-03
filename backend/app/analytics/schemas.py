from pydantic import BaseModel, Field


class CategoryBreakdownItem(BaseModel):
    category: str
    co2e_kg: float
    percentage: float
    activity_count: int


class AnalyticsSummaryResponse(BaseModel):
    enterprise_id: str
    period: str | None = None
    total_co2e_kg: float
    total_activities: int
    top_category: str | None = None
    top_category_percentage: float = 0.0
    category_breakdown: list[CategoryBreakdownItem] = Field(default_factory=list)


class MonthlyTrendItem(BaseModel):
    period: str
    total_co2e_kg: float
    activity_count: int
    by_category: dict[str, float] = Field(default_factory=dict)


class AnalyticsTrendsResponse(BaseModel):
    enterprise_id: str
    year: int | None = None
    trends: list[MonthlyTrendItem] = Field(default_factory=list)
