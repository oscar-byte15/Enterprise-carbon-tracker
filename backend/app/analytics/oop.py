"""Hometask 1: OOP implementation of Subsystem 3.

Domain objects modeling Analytics Engine and Sustainability Advisor.
Following established capstone OOP conventions with full encapsulation,
Decimal calculation safety, validation in setters, and clean relationships.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from .exceptions import (
    AIAdvisorError,
    AnalyticsAggregationError,
    InvalidMetricError,
)


class EmissionMetric:
    """Represents an aggregated emission metric used by the Analytics Dashboard."""

    def __init__(
        self,
        category: str,
        co2e_kg: float | int | Decimal,
        percentage: float | int | Decimal = 0.0,
        activity_count: int = 0,
    ) -> None:
        self.set_category(category)
        self.set_co2e_kg(co2e_kg)
        self.set_percentage(percentage)
        self.set_activity_count(activity_count)

    def get_category(self) -> str:
        return self._category

    def set_category(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise InvalidMetricError("Category is required and cannot be empty")
        self._category = value.strip()

    def get_co2e_kg(self) -> float:
        return float(self._co2e_kg)

    def set_co2e_kg(self, value: float | int | Decimal) -> None:
        try:
            val = Decimal(str(value))
        except Exception as exc:
            raise InvalidMetricError("CO2e emissions must be numeric") from exc
        if not val.is_finite() or val < 0:
            raise InvalidMetricError("CO2e emissions cannot be negative")
        self._co2e_kg = val

    def get_percentage(self) -> float:
        return float(self._percentage)

    def set_percentage(self, value: float | int | Decimal) -> None:
        try:
            val = Decimal(str(value))
        except Exception as exc:
            raise InvalidMetricError("Percentage must be numeric") from exc
        if not val.is_finite() or val < 0 or val > 100:
            raise InvalidMetricError("Percentage must be between 0 and 100")
        self._percentage = val

    def get_activity_count(self) -> int:
        return self._activity_count

    def set_activity_count(self, value: int) -> None:
        if not isinstance(value, int) or isinstance(value, bool):
            raise InvalidMetricError("Activity count must be an integer")
        if value < 0:
            raise InvalidMetricError("Activity count cannot be negative")
        self._activity_count = value

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.get_category(),
            "co2e_kg": self.get_co2e_kg(),
            "percentage": self.get_percentage(),
            "activity_count": self.get_activity_count(),
        }


class AnalyticsEngine:
    """Acts as the analytics processor behind the enterprise dashboard.

    Owns multiple EmissionMetric instances via composition.
    """

    def __init__(
        self,
        enterprise_id: str,
        raw_activities: list[dict[str, Any]] | None = None,
    ) -> None:
        self.initialize_metrics()
        self.set_enterprise_id(enterprise_id)
        if raw_activities:
            for item in raw_activities:
                cat = item.get("category", "")
                amt = item.get("co2e_kg", 0.0)
                count = item.get("count", 1)
                self.add_metric(cat, amt, count)

    def initialize_metrics(self) -> None:
        """Reset internal metrics dictionary and totals."""
        self._metrics: dict[str, EmissionMetric] = {}
        self._total_co2e_kg: Decimal = Decimal("0.00")

    def get_enterprise_id(self) -> str:
        return self._enterprise_id

    def set_enterprise_id(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise AnalyticsAggregationError("Enterprise ID is required and cannot be empty")
        self._enterprise_id = value.strip()

    def get_total_co2e_kg(self) -> float:
        return float(self._total_co2e_kg.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    def get_metrics(self) -> dict[str, EmissionMetric]:
        """Defensive copy of owned EmissionMetric instances."""
        return dict(self._metrics)

    def set_metrics(self, metrics: dict[str, Any]) -> None:
        if not isinstance(metrics, dict):
            raise AnalyticsAggregationError("Metrics must be a dictionary")
        self.initialize_metrics()
        for cat, metric in metrics.items():
            if isinstance(metric, EmissionMetric):
                self._metrics[cat] = metric
                self._total_co2e_kg += metric._co2e_kg
            elif isinstance(metric, dict):
                amt = metric.get("co2e_kg", 0.0)
                pct = metric.get("percentage", 0.0)
                count = metric.get("activity_count", 1)
                self._metrics[cat] = EmissionMetric(cat, amt, pct, count)
                self._total_co2e_kg += self._metrics[cat]._co2e_kg
            else:
                raise AnalyticsAggregationError("Metric entries must be EmissionMetric or dict instances")
        self.recalculate_percentages()

    def add_metric(
        self,
        category: str,
        co2e_kg: float | int | Decimal,
        count: int = 1,
    ) -> None:
        """Add emissions to a category, creating or updating an owned EmissionMetric."""
        if not isinstance(category, str) or not category.strip():
            raise InvalidMetricError("Category is required")
        try:
            amt = Decimal(str(co2e_kg))
        except Exception as exc:
            raise InvalidMetricError("CO2e emissions must be numeric") from exc
        if not amt.is_finite() or amt < 0:
            raise InvalidMetricError("CO2e emissions cannot be negative")
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise InvalidMetricError("Activity count must be a non-negative integer")

        cat_clean = category.strip()
        if cat_clean in self._metrics:
            existing = self._metrics[cat_clean]
            existing.set_co2e_kg(existing._co2e_kg + amt)
            existing.set_activity_count(existing.get_activity_count() + count)
        else:
            # Composition: AnalyticsEngine instantiates and owns EmissionMetric
            self._metrics[cat_clean] = EmissionMetric(cat_clean, amt, 0.0, count)

        self._total_co2e_kg += amt
        self.recalculate_percentages()

    def recalculate_percentages(self) -> None:
        """Recalculate percentage shares across all category metrics."""
        if self._total_co2e_kg > 0:
            for metric in self._metrics.values():
                pct = (metric._co2e_kg / self._total_co2e_kg * Decimal("100")).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
                metric.set_percentage(pct)
        else:
            for metric in self._metrics.values():
                metric.set_percentage(Decimal("0.00"))

    def get_top_category(self) -> str | None:
        """Identify the highest emitting category driver."""
        if not self._metrics:
            return None
        top_metric = max(self._metrics.values(), key=lambda m: m._co2e_kg)
        return top_metric.get_category() if top_metric._co2e_kg > 0 else None

    def generate_summary(self) -> dict[str, Any]:
        """Generate high-level analytics summary dictionary for the dashboard."""
        top_cat = self.get_top_category()
        top_pct = 0.0
        if top_cat and top_cat in self._metrics:
            top_pct = self._metrics[top_cat].get_percentage()

        total_activities = sum(m.get_activity_count() for m in self._metrics.values())
        return {
            "enterprise_id": self.get_enterprise_id(),
            "total_co2e_kg": self.get_total_co2e_kg(),
            "total_activities": total_activities,
            "top_category": top_cat,
            "top_category_percentage": top_pct,
            "category_breakdown": [m.to_dict() for m in self._metrics.values()],
        }


class SustainabilityAdvisor:
    """Analyzes analytics results and generates sustainability recommendations.

    Depends on AnalyticsEngine (dependency relationship) without owning it.
    """

    def __init__(
        self,
        advisor_mode: str = "rules",
        catalog: dict[str, list[dict[str, str]]] | None = None,
    ) -> None:
        self.set_advisor_mode(advisor_mode)
        self.set_catalog(catalog)

    def initialize_catalog(self) -> None:
        """Initialize the default benchmark recommendation strategy catalog."""
        self._catalog = {
            "electricity": [
                {
                    "category": "electricity",
                    "priority": "High",
                    "title": "Retrofit Facility LED Lighting",
                    "description": "Upgrade warehouse and office fixtures to smart sensor-controlled LEDs to cut lighting demand by 40-50%.",
                },
                {
                    "category": "electricity",
                    "priority": "Medium",
                    "title": "Shift Peak Operating Loads",
                    "description": "Reschedule high-power equipment runs and charging outside peak carbon-intensity grid hours.",
                },
                {
                    "category": "electricity",
                    "priority": "High",
                    "title": "Contract Renewable Energy Tariffs",
                    "description": "Procure green power guarantees of origin (GOs) or assess rooftop solar installation.",
                },
            ],
            "heating": [
                {
                    "category": "heating",
                    "priority": "High",
                    "title": "Programmable Night Thermostat Setbacks",
                    "description": "Lower facility setpoints by 3°C during unoccupied hours to reduce natural gas burn by 15%.",
                },
                {
                    "category": "heating",
                    "priority": "Medium",
                    "title": "Zoned Radiator Heating Valves",
                    "description": "Isolate heating in active workspaces from storage areas to eliminate wasted energy.",
                },
                {
                    "category": "heating",
                    "priority": "High",
                    "title": "Commercial Heat Pump Feasibility",
                    "description": "Assess transitioning aging fossil fuel boilers to high-efficiency industrial heat pumps.",
                },
            ],
            "transport": [
                {
                    "category": "transport",
                    "priority": "High",
                    "title": "Telematics Fleet Route Optimization",
                    "description": "Deploy GPS route scheduling to eliminate empty return miles and idle engine time.",
                },
                {
                    "category": "transport",
                    "priority": "Medium",
                    "title": "Pilot Electric Commercial Vans",
                    "description": "Transition fixed-route urban delivery vehicles to electric vans with depot charging.",
                },
                {
                    "category": "transport",
                    "priority": "Low",
                    "title": "Subsidize Public Commuter Passes",
                    "description": "Provide monthly transit subsidies to disincentivize single-occupancy employee car travel.",
                },
            ],
            "waste": [
                {
                    "category": "waste",
                    "priority": "High",
                    "title": "Enforce Strict Source Separation",
                    "description": "Implement multi-stream sorting stations to divert recyclable plastics and organics from landfills.",
                },
                {
                    "category": "waste",
                    "priority": "Medium",
                    "title": "Supplier Packaging Takeback",
                    "description": "Require vendor shipments to utilize returnable corrugated crates rather than disposable wrap.",
                },
                {
                    "category": "waste",
                    "priority": "Low",
                    "title": "Industrial Scrap Material Recovery",
                    "description": "Partner with accredited regional recyclers for closed-loop secondary material processing.",
                },
            ],
            "general": [
                {
                    "category": "general",
                    "priority": "High",
                    "title": "Establish Comprehensive Baseline",
                    "description": "Log activities across electricity, heating, transport, and waste to discover key hotspots.",
                }
            ],
        }

    def get_advisor_mode(self) -> str:
        return self._advisor_mode

    def set_advisor_mode(self, mode: str) -> None:
        if not isinstance(mode, str) or not mode.strip():
            raise AIAdvisorError("Advisor mode is required")
        clean_mode = mode.strip().lower()
        if clean_mode not in ("rules", "ai"):
            raise AIAdvisorError("Advisor mode must be 'rules' or 'ai'")
        self._advisor_mode = clean_mode

    def get_catalog(self) -> dict[str, list[dict[str, str]]]:
        """Return a defensive copy of the recommendation catalog."""
        return {k: [dict(item) for item in v] for k, v in self._catalog.items()}

    def set_catalog(
        self,
        catalog: dict[str, list[dict[str, str]]] | None,
    ) -> None:
        if catalog is None:
            self.initialize_catalog()
        elif not isinstance(catalog, dict):
            raise AIAdvisorError("Catalog must be a dictionary")
        else:
            self._catalog = {k: [dict(item) for item in v] for k, v in catalog.items()}

    def generate_recommendations(
        self,
        analytics: AnalyticsEngine,
    ) -> list[dict[str, str]]:
        """Generate targeted recommendations based on top emitting category from analytics."""
        if not isinstance(analytics, AnalyticsEngine):
            raise AIAdvisorError("analytics must be an instance of AnalyticsEngine")

        top_cat = analytics.get_top_category()
        key = (top_cat or "general").lower()

        templates = self._catalog.get(key)
        if not templates:
            templates = self._catalog.get("general", [])

        return [dict(rec) for rec in templates[:3]]
