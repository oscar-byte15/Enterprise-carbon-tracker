from __future__ import annotations

from typing import Any
from pymongo.collection import Collection

from app.activities.mongo_repository import activity_repository
from .schemas import (
    AnalyticsSummaryResponse,
    AnalyticsTrendsResponse,
    CategoryBreakdownItem,
    MonthlyTrendItem,
)


class AnalyticsService:
    def __init__(self, collection: Collection | None = None) -> None:
        self._collection = collection

    @property
    def collection(self) -> Collection:
        if self._collection is not None:
            return self._collection
        return activity_repository.collection

    def get_summary(
        self, enterprise_id: str, period: str | None = None
    ) -> AnalyticsSummaryResponse:
        match_filter: dict[str, Any] = {"enterprise_id": enterprise_id}
        if period:
            match_filter["period"] = period

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

        results = list(self.collection.aggregate(pipeline))

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
            enterprise_id=enterprise_id,
            period=period,
            total_co2e_kg=round(float(total_co2e), 2),
            total_activities=total_activities,
            top_category=top_category,
            top_category_percentage=top_category_percentage,
            category_breakdown=category_breakdown,
        )

    def get_trends(
        self, enterprise_id: str, year: int | None = None
    ) -> AnalyticsTrendsResponse:
        match_filter: dict[str, Any] = {"enterprise_id": enterprise_id}
        if year is not None:
            match_filter["period"] = {"$regex": f"^{year}-"}

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

        results = list(self.collection.aggregate(pipeline))

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

        return AnalyticsTrendsResponse(
            enterprise_id=enterprise_id,
            year=year,
            trends=trends,
        )


analytics_service = AnalyticsService()
