from __future__ import annotations

from typing import Any
from pymongo.collection import Collection

from app.activities.mongo_repository import activity_repository
from .exceptions import (
    AnalyticsAggregationError,
    InsufficientDataError,
    InvalidDatePeriodError,
)
from .schemas import (
    AnalyticsSummaryResponse,
    AnalyticsTrendsResponse,
    CategoryBreakdownItem,
    MonthlyTrendItem,
)


def validate_enterprise_id(enterprise_id: str) -> str:
    """Validate enterprise ID format and presence."""
    if not isinstance(enterprise_id, str) or not enterprise_id.strip():
        raise AnalyticsAggregationError("Enterprise ID is required and cannot be empty")
    return enterprise_id.strip()


def validate_period(period: str | None) -> str | None:
    """Validate period parameter in YYYY-MM format with valid month (01-12)."""
    if period is None:
        return None
    if not isinstance(period, str) or not period.strip():
        raise InvalidDatePeriodError("Period must be a non-empty string in YYYY-MM format")
    clean = period.strip()
    parts = clean.split("-")
    if len(parts) != 2 or len(parts[0]) != 4 or len(parts[1]) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
        raise InvalidDatePeriodError(f"Invalid period format '{period}': expected YYYY-MM (e.g. 2026-11)")
    month = int(parts[1])
    if month < 1 or month > 12:
        raise InvalidDatePeriodError(f"Invalid month in period '{period}': month must be between 01 and 12")
    return clean


def validate_year(year: int | None) -> int | None:
    """Validate year parameter (2000-2100)."""
    if year is None:
        return None
    if not isinstance(year, int) or isinstance(year, bool) or year < 2000 or year > 2100:
        raise InvalidDatePeriodError(f"Invalid year '{year}': must be an integer between 2000 and 2100")
    return year


class AnalyticsService:
    def __init__(self, collection: Collection | None = None) -> None:
        self._collection = collection

    @property
    def collection(self) -> Collection:
        if self._collection is not None:
            return self._collection
        return activity_repository.collection

    def get_summary(
        self,
        enterprise_id: str,
        period: str | None = None,
        require_data: bool = False,
    ) -> AnalyticsSummaryResponse:
        ent_id = validate_enterprise_id(enterprise_id)
        clean_period = validate_period(period)

        match_filter: dict[str, Any] = {"enterprise_id": ent_id}
        if clean_period:
            match_filter["period"] = clean_period

        pipeline = [
            {"$match": match_filter},
            {
                "$group": {
                    "_id": "$category",
                    "total_co2e": {"$sum": "$co2e_kg"},
                    "activity_count": {"$sum": 1},
                }
            },
            {"$sort": {"total_co2e": -1}},
        ]

        try:
            results = list(self.collection.aggregate(pipeline))
        except Exception as exc:
            raise AnalyticsAggregationError(f"Analytics aggregation failed: {exc}") from exc

        if require_data and not results:
            raise InsufficientDataError(
                f"Insufficient activity data for enterprise '{ent_id}'"
                + (f" in period '{clean_period}'" if clean_period else "")
            )

        total_co2e = sum(item.get("total_co2e", 0.0) for item in results)
        total_activities = sum(item.get("activity_count", 0) for item in results)

        category_breakdown: list[CategoryBreakdownItem] = []
        for item in results:
            cat_co2e = round(float(item.get("total_co2e", 0.0)), 2)
            pct = (
                round((cat_co2e / total_co2e) * 100, 2)
                if total_co2e > 0
                else 0.0
            )
            category_breakdown.append(
                CategoryBreakdownItem(
                    category=str(item.get("_id", "")),
                    co2e_kg=cat_co2e,
                    percentage=pct,
                    activity_count=int(item.get("activity_count", 0)),
                )
            )

        top_category = category_breakdown[0].category if category_breakdown else None
        top_category_percentage = (
            category_breakdown[0].percentage if category_breakdown else 0.0
        )

        return AnalyticsSummaryResponse(
            enterprise_id=ent_id,
            period=clean_period,
            total_co2e_kg=round(float(total_co2e), 2),
            total_activities=total_activities,
            top_category=top_category,
            top_category_percentage=top_category_percentage,
            category_breakdown=category_breakdown,
        )

    def get_trends(
        self,
        enterprise_id: str,
        year: int | None = None,
        require_data: bool = False,
    ) -> AnalyticsTrendsResponse:
        ent_id = validate_enterprise_id(enterprise_id)
        clean_year = validate_year(year)

        match_filter: dict[str, Any] = {"enterprise_id": ent_id}
        if clean_year is not None:
            match_filter["period"] = {"$regex": f"^{clean_year}-"}

        pipeline = [
            {"$match": match_filter},
            {
                "$group": {
                    "_id": {
                        "period": "$period",
                        "category": "$category",
                    },
                    "category_co2e": {"$sum": "$co2e_kg"},
                    "activity_count": {"$sum": 1},
                }
            },
            {"$sort": {"_id.period": 1}},
        ]

        try:
            results = list(self.collection.aggregate(pipeline))
        except Exception as exc:
            raise AnalyticsAggregationError(f"Analytics trend aggregation failed: {exc}") from exc

        period_data: dict[str, dict[str, Any]] = {}
        for item in results:
            group_id = item.get("_id") or {}
            p = group_id.get("period", "unknown")
            cat = group_id.get("category", "unknown")
            cat_co2e = round(float(item.get("category_co2e", 0.0)), 2)
            count = int(item.get("activity_count", 0))

            if p not in period_data:
                period_data[p] = {
                    "total_co2e": 0.0,
                    "activity_count": 0,
                    "by_category": {},
                }

            period_data[p]["total_co2e"] += cat_co2e
            period_data[p]["activity_count"] += count
            period_data[p]["by_category"][cat] = cat_co2e

        trends: list[MonthlyTrendItem] = [
            MonthlyTrendItem(
                period=p,
                total_co2e_kg=round(data["total_co2e"], 2),
                activity_count=data["activity_count"],
                by_category=data["by_category"],
            )
            for p, data in sorted(period_data.items(), key=lambda x: x[0])
        ]

        if require_data and not trends:
            raise InsufficientDataError(
                f"Insufficient activity data for enterprise '{ent_id}'"
                + (f" in year {clean_year}" if clean_year else "")
            )

        return AnalyticsTrendsResponse(
            enterprise_id=ent_id,
            year=clean_year,
            trends=trends,
        )


analytics_service = AnalyticsService()
