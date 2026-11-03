"""
Unit Tests - AI Sustainability Advisor (Subsystem 3)

Purpose:
    Verify concise, dashboard-friendly recommendation generation,
    impact levels (High/Medium/Low), max 3 cards limit, fallback behavior,
    and enterprise isolation.

Testing tools:
    Pytest, MongoMock, unittest.mock
"""

from unittest.mock import MagicMock
import mongomock
import pytest

from app.analytics.ai_advisor import AIAdvisorService
from app.analytics.service import AnalyticsService
from app.store import store


@pytest.fixture
def test_setup():
    """Setup isolated MongoMock collection and custom services."""
    client = mongomock.MongoClient()
    collection = client["test_carbon_tracker"]["activity_records"]

    analytics_svc = AnalyticsService(collection=collection)

    mock_openai = MagicMock()
    mock_openai.is_available = False
    mock_openai.model = "gpt-4o-mini"

    advisor_svc = AIAdvisorService(openai_service=mock_openai)

    store.create_enterprise(
        email="test_concise_ai@example.com",
        password="Password123",
        company_name="GreenTech Solutions",
        industry="Technology Logistics",
    )
    user = store.get_user_by_email("test_concise_ai@example.com")
    ent_id = user["enterprise_id"]

    yield {
        "collection": collection,
        "analytics_svc": analytics_svc,
        "advisor_svc": advisor_svc,
        "mock_openai": mock_openai,
        "enterprise_id": ent_id,
    }
    client.close()


def test_ai_advisor_zero_activities_onboarding(test_setup, monkeypatch):
    """When an enterprise has 0 activities, return onboarding guidance."""
    setup = test_setup
    monkeypatch.setattr("app.analytics.ai_advisor.analytics_service", setup["analytics_svc"])

    response = setup["advisor_svc"].generate_recommendations(setup["enterprise_id"])

    assert response.enterprise_id == setup["enterprise_id"]
    assert response.total_activities == 0
    assert response.is_fallback is True
    assert len(response.recommendations) == 1
    rec = response.recommendations[0]
    assert "Log" in rec.title
    assert rec.impact in ["High", "Medium", "Low"]
    assert len(rec.action) > 0


def test_ai_advisor_fallback_tailored_to_transport(test_setup, monkeypatch):
    """When OpenAI is unconfigured and transport is the highest driver, deliver max 3 concise transport cards."""
    setup = test_setup
    monkeypatch.setattr("app.analytics.ai_advisor.analytics_service", setup["analytics_svc"])

    setup["collection"].insert_many([
        {
            "id": "act-1",
            "enterprise_id": setup["enterprise_id"],
            "category": "transport",
            "type": "Diesel",
            "amount": 500.0,
            "unit": "L",
            "date": "2026-10-15",
            "period": "2026-10",
            "co2e_kg": 1285.4,
        },
        {
            "id": "act-2",
            "enterprise_id": setup["enterprise_id"],
            "category": "electricity",
            "type": "Grid electricity",
            "amount": 100.0,
            "unit": "kWh",
            "date": "2026-10-16",
            "period": "2026-10",
            "co2e_kg": 35.2,
        },
    ])

    response = setup["advisor_svc"].generate_recommendations(setup["enterprise_id"])

    assert response.is_fallback is True
    assert response.top_category == "transport"
    assert response.total_activities == 2
    assert len(response.recommendations) <= 3
    assert len(response.recommendations) == 3

    for rec in response.recommendations:
        assert rec.category == "transport"
        assert len(rec.title) > 0
        assert len(rec.action) > 0
        assert rec.impact in ["High", "Medium", "Low"]


def test_ai_advisor_live_openai_success(test_setup, monkeypatch):
    """When OpenAI is available and returns valid JSON, parse concise cards."""
    setup = test_setup
    monkeypatch.setattr("app.analytics.ai_advisor.analytics_service", setup["analytics_svc"])

    setup["mock_openai"].is_available = True
    setup["mock_openai"].generate_text.return_value = """
    [
        {
            "id": "ai-1",
            "category": "electricity",
            "title": "LED & Sensor Retrofit",
            "action": "Replace warehouse lighting with motion-activated LEDs to reduce base load by 40%.",
            "impact": "High"
        },
        {
            "id": "ai-2",
            "category": "electricity",
            "title": "Off-Peak Battery Storage",
            "action": "Store cheap renewable power at night to power operations during peak tariff periods.",
            "impact": "Medium"
        }
    ]
    """

    setup["collection"].insert_one({
        "id": "act-elec",
        "enterprise_id": setup["enterprise_id"],
        "category": "electricity",
        "type": "Grid electricity",
        "amount": 2000.0,
        "unit": "kWh",
        "date": "2026-11-01",
        "period": "2026-11",
        "co2e_kg": 704.0,
    })

    response = setup["advisor_svc"].generate_recommendations(setup["enterprise_id"])

    assert response.is_fallback is False
    assert response.model_used == "gpt-4o-mini"
    assert len(response.recommendations) == 2
    assert response.recommendations[0].title == "LED & Sensor Retrofit"
    assert response.recommendations[0].impact == "High"
    assert "LEDs" in response.recommendations[0].action


def test_ai_advisor_malformed_llm_json_falls_back(test_setup, monkeypatch):
    """If OpenAI returns unparseable text, gracefully fall back to rule-based catalog."""
    setup = test_setup
    monkeypatch.setattr("app.analytics.ai_advisor.analytics_service", setup["analytics_svc"])

    setup["mock_openai"].is_available = True
    setup["mock_openai"].generate_text.return_value = "Non-JSON response text."

    setup["collection"].insert_one({
        "id": "act-elec",
        "enterprise_id": setup["enterprise_id"],
        "category": "electricity",
        "type": "Grid electricity",
        "amount": 500.0,
        "unit": "kWh",
        "date": "2026-11-01",
        "period": "2026-11",
        "co2e_kg": 176.0,
    })

    response = setup["advisor_svc"].generate_recommendations(setup["enterprise_id"])

    assert response.is_fallback is True
    assert 0 < len(response.recommendations) <= 3
    assert response.top_category == "electricity"
    assert response.recommendations[0].impact in ["High", "Medium", "Low"]
