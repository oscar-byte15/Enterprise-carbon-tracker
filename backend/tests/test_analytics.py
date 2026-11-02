"""
Unit Tests - AnalyticsService (Subsystem 3)

Purpose:
    Verify MongoDB aggregation calculations, period filtering,
    monthly trends, and enterprise-based data isolation.

Testing tools:
    Pytest, MongoMock
"""

import mongomock
import pytest

from app.analytics.service import AnalyticsService


@pytest.fixture
def analytics_service():
    """Create an AnalyticsService connected to an isolated in-memory mock collection."""
    client = mongomock.MongoClient()
    collection = client["test_carbon_tracker"]["activity_records"]
    service = AnalyticsService(collection=collection)
    yield service
    client.close()


@pytest.fixture
def sample_activities():
    """Sample activities spanning multiple categories and periods."""
    return [
        {
            "id": "act-1",
            "enterprise_id": "enterprise-A",
            "category": "electricity",
            "type": "Grid electricity",
            "amount": 1000.0,
            "unit": "kWh",
            "date": "2026-10-15",
            "period": "2026-10",
            "co2e_kg": 352.0,
        },
        {
            "id": "act-2",
            "enterprise_id": "enterprise-A",
            "category": "heating",
            "type": "Natural gas",
            "amount": 500.0,
            "unit": "kWh",
            "date": "2026-10-20",
            "period": "2026-10",
            "co2e_kg": 91.48,
        },
        {
            "id": "act-3",
            "enterprise_id": "enterprise-A",
            "category": "transport",
            "type": "Diesel",
            "amount": 200.0,
            "unit": "L",
            "date": "2026-11-01",
            "period": "2026-11",
            "co2e_kg": 514.16,
        },
        {
            "id": "act-4",
            "enterprise_id": "enterprise-A",
            "category": "waste",
            "type": "General - Landfill",
            "amount": 100.0,
            "unit": "kg",
            "date": "2026-11-05",
            "period": "2026-11",
            "co2e_kg": 49.73,
        },
        # Activity for enterprise-B (must be isolated)
        {
            "id": "act-5",
            "enterprise_id": "enterprise-B",
            "category": "transport",
            "type": "Petrol",
            "amount": 1000.0,
            "unit": "L",
            "date": "2026-11-02",
            "period": "2026-11",
            "co2e_kg": 2069.16,
        },
    ]


# ============================================================
# SUMMARY TESTS
# ============================================================

def test_summary_empty_database(analytics_service):
    """Verify summary response when an enterprise has no activities."""
    summary = analytics_service.get_summary(enterprise_id="enterprise-empty")
    assert summary.enterprise_id == "enterprise-empty"
    assert summary.total_co2e_kg == 0.0
    assert summary.total_activities == 0
    assert summary.top_category is None
    assert summary.top_category_percentage == 0.0
    assert summary.category_breakdown == []


def test_summary_all_time(analytics_service, sample_activities):
    """Verify all-time summary calculation, category breakdowns, and top category."""
    analytics_service.collection.insert_many(sample_activities)

    summary = analytics_service.get_summary(enterprise_id="enterprise-A")

    assert summary.enterprise_id == "enterprise-A"
    assert summary.total_activities == 4
    expected_total = round(352.0 + 91.48 + 514.16 + 49.73, 2)
    assert summary.total_co2e_kg == expected_total

    # Transport has 514.16, which is the highest
    assert summary.top_category == "transport"
    expected_top_pct = round((514.16 / expected_total) * 100, 2)
    assert summary.top_category_percentage == expected_top_pct

    # Category breakdown contains all 4 categories sorted descending
    assert len(summary.category_breakdown) == 4
    assert summary.category_breakdown[0].category == "transport"
    assert summary.category_breakdown[0].co2e_kg == 514.16


def test_summary_with_period_filter(analytics_service, sample_activities):
    """Verify summary respects period filter."""
    analytics_service.collection.insert_many(sample_activities)

    summary = analytics_service.get_summary(
        enterprise_id="enterprise-A", period="2026-10"
    )

    assert summary.period == "2026-10"
    assert summary.total_activities == 2
    expected_oct_total = round(352.0 + 91.48, 2)
    assert summary.total_co2e_kg == expected_oct_total
    assert summary.top_category == "electricity"


def test_summary_enterprise_isolation(analytics_service, sample_activities):
    """Verify that Enterprise A cannot see Enterprise B's emissions in summary."""
    analytics_service.collection.insert_many(sample_activities)

    summary_a = analytics_service.get_summary(enterprise_id="enterprise-A")
    summary_b = analytics_service.get_summary(enterprise_id="enterprise-B")

    # Enterprise B has act-5 (2069.16 kg)
    assert summary_b.total_co2e_kg == 2069.16
    assert summary_b.total_activities == 1

    # Enterprise A must NOT include Enterprise B's 2069.16 kg
    assert summary_a.total_co2e_kg < 2000.0


# ============================================================
# TRENDS TESTS
# ============================================================

def test_trends_empty_database(analytics_service):
    """Verify trends response when an enterprise has no activities."""
    trends = analytics_service.get_trends(enterprise_id="enterprise-empty")
    assert trends.enterprise_id == "enterprise-empty"
    assert trends.trends == []


def test_trends_monthly_aggregation(analytics_service, sample_activities):
    """Verify monthly grouping and category breakdown per month."""
    analytics_service.collection.insert_many(sample_activities)

    result = analytics_service.get_trends(enterprise_id="enterprise-A")

    assert len(result.trends) == 2  # 2026-10 and 2026-11
    oct_trend = result.trends[0]
    assert oct_trend.period == "2026-10"
    assert oct_trend.activity_count == 2
    assert oct_trend.total_co2e_kg == round(352.0 + 91.48, 2)
    assert oct_trend.by_category == {
        "electricity": 352.0,
        "heating": 91.48,
    }

    nov_trend = result.trends[1]
    assert nov_trend.period == "2026-11"
    assert nov_trend.activity_count == 2
    assert nov_trend.total_co2e_kg == round(514.16 + 49.73, 2)
    assert nov_trend.by_category == {
        "transport": 514.16,
        "waste": 49.73,
    }


def test_trends_year_filter(analytics_service, sample_activities):
    """Verify year filter includes matching periods and excludes other years."""
    # Add a 2025 activity
    historical_activity = {
        "id": "act-hist",
        "enterprise_id": "enterprise-A",
        "category": "electricity",
        "type": "Grid electricity",
        "amount": 200.0,
        "unit": "kWh",
        "date": "2025-12-10",
        "period": "2025-12",
        "co2e_kg": 70.4,
    }
    analytics_service.collection.insert_many(
        [*sample_activities, historical_activity]
    )

    result_2026 = analytics_service.get_trends(
        enterprise_id="enterprise-A", year=2026
    )
    assert len(result_2026.trends) == 2
    assert all(item.period.startswith("2026") for item in result_2026.trends)

    result_2025 = analytics_service.get_trends(
        enterprise_id="enterprise-A", year=2025
    )
    assert len(result_2025.trends) == 1
    assert result_2025.trends[0].period == "2025-12"


def test_trends_enterprise_isolation(analytics_service, sample_activities):
    """Verify that trends do not leak records between different enterprises."""
    analytics_service.collection.insert_many(sample_activities)

    trends_a = analytics_service.get_trends(enterprise_id="enterprise-A")
    trends_b = analytics_service.get_trends(enterprise_id="enterprise-B")

    # Enterprise B has only 1 period in 2026-11
    assert len(trends_b.trends) == 1
    assert trends_b.trends[0].total_co2e_kg == 2069.16

    # Enterprise A in 2026-11 should not include Enterprise B's 2069.16
    nov_a = [t for t in trends_a.trends if t.period == "2026-11"][0]
    assert nov_a.total_co2e_kg == round(514.16 + 49.73, 2)
