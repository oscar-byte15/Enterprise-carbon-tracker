from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.analytics.service import analytics_service
from app.config import settings
from app.services.openai_service import OpenAIService
from app.store import store
from .ai_schemas import AIRecommendationsResponse, RecommendationItem
from .exceptions import AIAdvisorError, InsufficientDataError

logger = logging.getLogger(__name__)

# Pre-compiled concise, dashboard-friendly fallback recommendations catalog
FALLBACK_CATALOG: dict[str, list[dict[str, str]]] = {
    "transport": [
        {
            "title": "Route & Dispatch Optimization",
            "action": "Implement telematics to combine delivery runs and cut idle time. This immediately trims fleet fuel consumption by 10-15%.",
            "impact": "High",
        },
        {
            "title": "Pilot Commercial Electric Vans",
            "action": "Replace high-mileage delivery vans on fixed routes with electric alternatives paired with overnight depot charging.",
            "impact": "Medium",
        },
        {
            "title": "Subsidize Low-Carbon Commuting",
            "action": "Offer monthly transit passes and flexible remote-work policies to reduce employee commuting emissions.",
            "impact": "Low",
        },
    ],
    "electricity": [
        {
            "title": "Smart LED & Motion Controls",
            "action": "Retrofit facility lighting with sensor-activated commercial LEDs to cut lighting power demand by up to 50%.",
            "impact": "High",
        },
        {
            "title": "Peak Grid Load Shaving",
            "action": "Shift machinery cycles and fleet charging outside peak carbon-intensity grid hours to reduce costs and footprint.",
            "impact": "Medium",
        },
        {
            "title": "On-Site Solar PV Installation",
            "action": "Install rooftop solar panels or contract for 100% certified renewable electricity through green tariffs.",
            "impact": "High",
        },
    ],
    "heating": [
        {
            "title": "Boiler Setbacks & Weatherization",
            "action": "Lower thermostat setpoints during non-operating hours and seal loading bay drafts to eliminate wasted natural gas.",
            "impact": "High",
        },
        {
            "title": "Zoned Smart Thermostats",
            "action": "Install programmable radiator valves across facility zones to avoid heating unoccupied storage and office areas.",
            "impact": "Medium",
        },
        {
            "title": "Commercial Heat Pump Retrofit",
            "action": "Plan the phase-out of aging gas boilers in favor of high-efficiency industrial air-source or ground-source heat pumps.",
            "impact": "High",
        },
    ],
    "waste": [
        {
            "title": "Mandatory Source Segregation",
            "action": "Deploy dedicated sorting stations for organics and clean plastics to divert material from high-emission landfills.",
            "impact": "High",
        },
        {
            "title": "Standardize Reusable Packaging",
            "action": "Work with suppliers to replace single-use plastic wrap with durable returnable shipping totes.",
            "impact": "Medium",
        },
        {
            "title": "Certified Circular Recycling",
            "action": "Partner with regional industrial recyclers to ensure commercial scrap enters verified closed-loop recovery.",
            "impact": "Low",
        },
    ],
}


class AIAdvisorService:
    def __init__(self, openai_service: OpenAIService | None = None) -> None:
        self.openai_service = openai_service or OpenAIService()
        self.max_recommendations = 3

    def configure(self, max_recommendations: int = 3) -> None:
        """Configure AI Advisor operational parameters."""
        if not isinstance(max_recommendations, int) or isinstance(max_recommendations, bool) or max_recommendations <= 0:
            raise AIAdvisorError("max_recommendations must be a positive integer")
        self.max_recommendations = max_recommendations

    def _normalize_impact(self, val: str | None) -> str:
        s = (val or "").strip().lower()
        if "high" in s or "immediate" in s or "win" in s:
            return "High"
        if "low" in s:
            return "Low"
        return "Medium"

    def _build_fallback_recommendations(
        self, top_category: str | None
    ) -> list[RecommendationItem]:
        category_key = (top_category or "electricity").lower()
        templates = FALLBACK_CATALOG.get(category_key, FALLBACK_CATALOG["electricity"])

        items: list[RecommendationItem] = []
        for i, t in enumerate(templates[:3]):
            items.append(
                RecommendationItem(
                    id=f"rec-{category_key}-{i + 1}",
                    category=category_key,
                    title=t["title"],
                    action=t["action"],
                    impact=self._normalize_impact(t.get("impact")),
                )
            )
        return items

    def _parse_llm_json(self, raw_text: str) -> list[RecommendationItem] | None:
        """Parse structured recommendations array from LLM output, limited to 3 items."""
        clean = raw_text.strip()
        if clean.startswith("```json"):
            clean = clean[7:]
        elif clean.startswith("```"):
            clean = clean[3:]
        if clean.endswith("```"):
            clean = clean[:-3]
        clean = clean.strip()

        try:
            data = json.loads(clean)
            if isinstance(data, dict) and "recommendations" in data:
                data = data["recommendations"]

            if not isinstance(data, list):
                return None

            items: list[RecommendationItem] = []
            for item in data[:3]:
                title = str(item.get("title") or "Emissions Reduction Action").strip()
                action = str(item.get("action") or item.get("description") or "").strip()
                impact = self._normalize_impact(item.get("impact") or item.get("urgency"))
                category = str(item.get("category") or "general").strip()

                items.append(
                    RecommendationItem(
                        id=str(item.get("id") or f"rec-{uuid4().hex[:6]}"),
                        category=category,
                        title=title,
                        action=action,
                        impact=impact,
                    )
                )
            return items if items else None
        except Exception as err:
            logger.warning("Failed to parse LLM response into recommendations: %s", err)
            return None

    def generate_recommendations(
        self,
        enterprise_id: str,
        require_data: bool = False,
    ) -> AIRecommendationsResponse:
        """
        Generate concise, dashboard-friendly carbon reduction recommendations.
        Limits output to at most configured cards.
        """
        if not isinstance(enterprise_id, str) or not enterprise_id.strip():
            raise AIAdvisorError("Enterprise ID is required and cannot be empty")

        summary = analytics_service.get_summary(enterprise_id=enterprise_id)

        if require_data and summary.total_activities == 0:
            raise InsufficientDataError(
                f"Insufficient activity data for enterprise '{enterprise_id}' to generate recommendations"
            )

        enterprise = store.get_enterprise(enterprise_id) or {}
        company_name = str(enterprise.get("company_name") or "Enterprise")
        industry = str(enterprise.get("industry") or "General Operations")
        now_iso = datetime.now(timezone.utc).isoformat()

        # Handle zero-activity baseline
        if summary.total_activities == 0:
            logger.info(
                "[AI Advisor Fallback] Triggered condition: Zero activities logged for enterprise_id=%s. "
                "Returning baseline onboarding recommendation.",
                enterprise_id,
            )
            return AIRecommendationsResponse(
                enterprise_id=enterprise_id,
                company_name=company_name,
                industry=industry,
                top_category=None,
                top_category_percentage=0.0,
                total_co2e_kg=0.0,
                total_activities=0,
                is_fallback=True,
                model_used="rules-engine-baseline",
                generated_at=now_iso,
                recommendations=[
                    RecommendationItem(
                        id="rec-onboard-1",
                        category="general",
                        title="Log Baseline Activity",
                        action="Record your first energy, fuel, or waste activity to unlock customized emissions reduction strategies.",
                        impact="High",
                    )
                ],
            )

        fallback_reason: str = "Unknown"

        # Attempt live OpenAI completion if configured
        if not self.openai_service.is_available:
            fallback_reason = "OpenAI service is unavailable (OPENAI_API_KEY is not configured or client failed to initialize)"
            logger.warning("[AI Advisor Fallback] Triggered condition: %s", fallback_reason)
        else:
            breakdown_summary = ", ".join(
                f"{item.category}: {item.co2e_kg:.1f}kg ({item.percentage}%)"
                for item in summary.category_breakdown
            )

            prompt = (
                f"Company: {company_name}\n"
                f"Industry: {industry}\n"
                f"Total Footprint: {summary.total_co2e_kg:.1f} kg CO2e ({summary.total_activities} activities)\n"
                f"Primary Driver: {summary.top_category} ({summary.top_category_percentage:.1f}%)\n"
                f"Breakdown: {breakdown_summary}\n\n"
                "Generate EXACTLY 3 short, high-impact carbon reduction recommendations formatted as dashboard cards.\n"
                "Keep actions practical, concise (1-2 sentences maximum), and free of consulting fluff.\n\n"
                "Respond ONLY with a valid JSON array of up to 3 objects with these exact keys:\n"
                '- "id": string (e.g. "rec-1")\n'
                '- "category": "electricity" | "heating" | "transport" | "waste"\n'
                '- "title": string (3 to 6 words maximum)\n'
                '- "action": string (1 to 2 sentences maximum)\n'
                '- "impact": "High" | "Medium" | "Low"\n\n'
                "No markdown backticks, no commentary."
            )

            try:
                raw_response = self.openai_service.generate_text(
                    prompt,
                    system_prompt=(
                        "You are an executive carbon reduction advisor. Provide concise, "
                        "practical recommendations formatted strictly as a JSON array of up to 3 cards."
                    ),
                    temperature=0.2,
                )
                parsed = self._parse_llm_json(raw_response)
                if parsed:
                    logger.info(
                        "[AI Advisor] Successfully generated %d live recommendations via OpenAI (%s)",
                        len(parsed),
                        self.openai_service.model,
                    )
                    return AIRecommendationsResponse(
                        enterprise_id=enterprise_id,
                        company_name=company_name,
                        industry=industry,
                        top_category=summary.top_category,
                        top_category_percentage=summary.top_category_percentage,
                        total_co2e_kg=summary.total_co2e_kg,
                        total_activities=summary.total_activities,
                        is_fallback=False,
                        model_used=self.openai_service.model,
                        generated_at=now_iso,
                        recommendations=parsed[:3],
                    )
                else:
                    fallback_reason = "OpenAI responded, but response could not be parsed into valid JSON cards"
                    logger.warning("[AI Advisor Fallback] Triggered condition: %s. Raw response: %s", fallback_reason, raw_response)
            except Exception as err:
                fallback_reason = f"OpenAI API call failed: {type(err).__name__}: {err}"
                logger.exception("[AI Advisor Fallback] Triggered condition: %s", fallback_reason)

        # Fallback to pre-compiled concise catalog
        logger.info(
            "[AI Advisor Fallback] Returning rules-engine-fallback recommendations. Reason: %s",
            fallback_reason,
        )
        fallback_items = self._build_fallback_recommendations(summary.top_category)
        return AIRecommendationsResponse(
            enterprise_id=enterprise_id,
            company_name=company_name,
            industry=industry,
            top_category=summary.top_category,
            top_category_percentage=summary.top_category_percentage,
            total_co2e_kg=summary.total_co2e_kg,
            total_activities=summary.total_activities,
            is_fallback=True,
            model_used="rules-engine-fallback",
            generated_at=now_iso,
            recommendations=fallback_items[:3],
        )


ai_advisor_service = AIAdvisorService()
