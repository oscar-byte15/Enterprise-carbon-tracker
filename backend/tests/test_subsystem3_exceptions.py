"""Hometask 4: Subsystem 3 error handling and API/aggregation tests.

Run from backend/: python -m pytest tests/test_subsystem3_exceptions.py -v
MongoMock isolates data; no running MongoDB or external services required.
"""
from decimal import Decimal
from unittest.mock import patch, MagicMock

import mongomock
import pytest
from fastapi import HTTPException

from app.analytics.exceptions import (
    Subsystem3Error,
    InvalidMetricError,
    InvalidDatePeriodError,
    AnalyticsAggregationError,
    InsufficientDataError,
    AIAdvisorError,
)
from app.analytics.oop import (
    EmissionMetric,
    AnalyticsEngine,
    SustainabilityAdvisor,
)

# Mock MongoDB client before importing modules that instantiate repositories at load time
with patch("pymongo.MongoClient", return_value=mongomock.MongoClient()):
    from app.analytics.service import AnalyticsService
    from app.analytics.ai_advisor import AIAdvisorService
    from app.analytics import router as analytics_router
    from app.analytics import ai_router as ai_advisor_router


# ============================================================================
# 1. Exception Hierarchy Tests
# ============================================================================

def test_subsystem3_exception_hierarchy():
    """Verify that Subsystem3Error inherits from ValueError and all domain errors inherit from it."""
    assert issubclass(Subsystem3Error, ValueError)
    assert issubclass(InvalidMetricError, Subsystem3Error)
    assert issubclass(InvalidDatePeriodError, Subsystem3Error)
    assert issubclass(AnalyticsAggregationError, Subsystem3Error)
    assert issubclass(InsufficientDataError, Subsystem3Error)
    assert issubclass(AIAdvisorError, Subsystem3Error)


def test_exception_preserves_error_message():
    """Verify custom exceptions preserve descriptive error messages."""
    msg = "Invalid period: 2026-13"
    err = InvalidDatePeriodError(msg)
    assert str(err) == msg
    assert isinstance(err, ValueError)


# ============================================================================
# 2. OOP Validation Tests
# ============================================================================

@pytest.mark.parametrize("invalid_co2", [-10.5, -1, float("nan")])
def test_emission_metric_rejects_negative_and_nan_emissions(invalid_co2):
    """EmissionMetric rejects negative or non-finite CO2e amounts with InvalidMetricError."""
    with pytest.raises(InvalidMetricError, match="CO2e emissions cannot be negative"):
        EmissionMetric(category="electricity", co2e_kg=invalid_co2)


@pytest.mark.parametrize("invalid_pct", [-1.0, 100.5, "not-a-number"])
def test_emission_metric_rejects_invalid_percentage(invalid_pct):
    """EmissionMetric rejects out-of-range or non-numeric percentages with InvalidMetricError."""
    with pytest.raises(InvalidMetricError):
        EmissionMetric(category="electricity", co2e_kg=100.0, percentage=invalid_pct)


@pytest.mark.parametrize("invalid_cat", ["", "   ", None, 123])
def test_emission_metric_rejects_invalid_category(invalid_cat):
    """EmissionMetric rejects empty, whitespace, or non-string category."""
    with pytest.raises(InvalidMetricError, match="Category is required"):
        EmissionMetric(category=invalid_cat, co2e_kg=100.0)


@pytest.mark.parametrize("invalid_count", [-1, 2.5, True])
def test_emission_metric_rejects_invalid_activity_count(invalid_count):
    """EmissionMetric rejects negative, non-integer, or boolean activity counts."""
    with pytest.raises(InvalidMetricError):
        EmissionMetric(category="electricity", co2e_kg=100.0, activity_count=invalid_count)


@pytest.mark.parametrize("invalid_ent", ["", "   ", None])
def test_analytics_engine_rejects_invalid_enterprise_id(invalid_ent):
    """AnalyticsEngine rejects empty or missing enterprise ID with AnalyticsAggregationError."""
    with pytest.raises(AnalyticsAggregationError, match="Enterprise ID is required"):
        AnalyticsEngine(enterprise_id=invalid_ent)


def test_analytics_engine_rejects_invalid_metrics_structure():
    """AnalyticsEngine rejects invalid metric dictionaries with AnalyticsAggregationError."""
    engine = AnalyticsEngine("ent-001")
    with pytest.raises(AnalyticsAggregationError, match="Metrics must be a dictionary"):
        engine.set_metrics("not-a-dict")

    with pytest.raises(AnalyticsAggregationError, match="Metric entries must be EmissionMetric or dict"):
        engine.set_metrics({"electricity": "invalid-entry"})


@pytest.mark.parametrize("invalid_mode", ["", "unknown", "deepseek", None])
def test_sustainability_advisor_rejects_invalid_mode(invalid_mode):
    """SustainabilityAdvisor rejects invalid advisor mode with AIAdvisorError."""
    with pytest.raises(AIAdvisorError):
        SustainabilityAdvisor(advisor_mode=invalid_mode)


def test_sustainability_advisor_rejects_invalid_analytics_instance():
    """SustainabilityAdvisor rejects non-AnalyticsEngine object with AIAdvisorError."""
    advisor = SustainabilityAdvisor(advisor_mode="rules")
    with pytest.raises(AIAdvisorError, match="analytics must be an instance of AnalyticsEngine"):
        advisor.generate_recommendations("not-an-analytics-instance")


def test_ai_advisor_service_configuration_error():
    """AIAdvisorService rejects non-positive recommendation counts with AIAdvisorError."""
    service = AIAdvisorService()
    with pytest.raises(AIAdvisorError, match="max_recommendations must be a positive integer"):
        service.configure(max_recommendations=0)


# ============================================================================
# 3. Analytics Service Tests
# ============================================================================

@pytest.mark.parametrize("bad_period", ["2026", "2026-1", "invalid", "2026-13", "2026-00"])
def test_analytics_service_rejects_invalid_period_format(bad_period):
    """AnalyticsService rejects malformed periods or invalid months with InvalidDatePeriodError."""
    service = AnalyticsService(collection=mongomock.MongoClient()["test"]["activities"])
    with pytest.raises(InvalidDatePeriodError):
        service.get_summary(enterprise_id="ent-1", period=bad_period)


@pytest.mark.parametrize("bad_year", [1999, 2101, "2026"])
def test_analytics_service_rejects_invalid_year(bad_year):
    """AnalyticsService rejects years outside 2000-2100 or non-integer years with InvalidDatePeriodError."""
    service = AnalyticsService(collection=mongomock.MongoClient()["test"]["activities"])
    with pytest.raises(InvalidDatePeriodError):
        service.get_trends(enterprise_id="ent-1", year=bad_year)


@pytest.mark.parametrize("bad_ent", ["", "   "])
def test_analytics_service_rejects_empty_enterprise_id(bad_ent):
    """AnalyticsService rejects empty enterprise ID with AnalyticsAggregationError."""
    service = AnalyticsService(collection=mongomock.MongoClient()["test"]["activities"])
    with pytest.raises(AnalyticsAggregationError, match="Enterprise ID is required"):
        service.get_summary(enterprise_id=bad_ent)


def test_analytics_service_aggregation_failure_wrapped():
    """Database aggregation errors are caught and re-raised as AnalyticsAggregationError."""
    mock_collection = MagicMock()
    mock_collection.aggregate.side_effect = RuntimeError("Database connection lost")
    service = AnalyticsService(collection=mock_collection)

    with pytest.raises(AnalyticsAggregationError, match="Analytics aggregation failed"):
        service.get_summary(enterprise_id="ent-1")

    with pytest.raises(AnalyticsAggregationError, match="Analytics trend aggregation failed"):
        service.get_trends(enterprise_id="ent-1")


def test_analytics_service_insufficient_data():
    """When require_data is True, missing records raise InsufficientDataError."""
    empty_collection = mongomock.MongoClient()["test"]["empty_activities"]
    service = AnalyticsService(collection=empty_collection)

    with pytest.raises(InsufficientDataError, match="Insufficient activity data"):
        service.get_summary(enterprise_id="ent-empty", require_data=True)

    with pytest.raises(InsufficientDataError, match="Insufficient activity data"):
        service.get_trends(enterprise_id="ent-empty", require_data=True)


def test_analytics_service_isolates_enterprise_data():
    """Analytics calculations strictly isolate enterprise records."""
    collection = mongomock.MongoClient()["test"]["tenant_activities"]
    collection.insert_many([
        {"enterprise_id": "company-a", "category": "electricity", "co2e_kg": 50.0, "period": "2026-11"},
        {"enterprise_id": "company-b", "category": "electricity", "co2e_kg": 200.0, "period": "2026-11"},
    ])
    service = AnalyticsService(collection=collection)

    summary_a = service.get_summary(enterprise_id="company-a")
    summary_b = service.get_summary(enterprise_id="company-b")

    assert summary_a.total_co2e_kg == 50.0
    assert summary_a.total_activities == 1
    assert summary_b.total_co2e_kg == 200.0
    assert summary_b.total_activities == 1


# ============================================================================
# 4. API & HTTP Status Code Mapping Tests
# ============================================================================

def test_analytics_router_maps_invalid_period_to_400():
    """Router maps InvalidDatePeriodError to HTTP 400 Bad Request."""
    with pytest.raises(HTTPException) as exc:
        analytics_router.get_analytics_summary(
            period="2026-99",
            require_data=False,
            enterprise_id="company-a",
        )
    assert exc.value.status_code == 400
    assert "Invalid month" in exc.value.detail


def test_analytics_router_maps_invalid_year_to_400():
    """Router maps InvalidDatePeriodError for year to HTTP 400 Bad Request."""
    with pytest.raises(HTTPException) as exc:
        analytics_router.get_analytics_trends(
            year=1980,
            require_data=False,
            enterprise_id="company-a",
        )
    assert exc.value.status_code == 400
    assert "Invalid year" in exc.value.detail


def test_analytics_router_maps_insufficient_data_to_404():
    """Router maps InsufficientDataError to HTTP 404 Not Found."""
    with patch.object(
        analytics_router.analytics_service,
        "get_summary",
        side_effect=InsufficientDataError("No activity data found"),
    ):
        with pytest.raises(HTTPException) as exc:
            analytics_router.get_analytics_summary(
                period=None,
                require_data=True,
                enterprise_id="company-a",
            )
        assert exc.value.status_code == 404
        assert "No activity data found" in exc.value.detail


def test_analytics_router_maps_aggregation_error_to_500():
    """Router maps AnalyticsAggregationError to HTTP 500 Internal Server Error."""
    with patch.object(
        analytics_router.analytics_service,
        "get_summary",
        side_effect=AnalyticsAggregationError("Database pipeline collapsed"),
    ):
        with pytest.raises(HTTPException) as exc:
            analytics_router.get_analytics_summary(
                period=None,
                require_data=False,
                enterprise_id="company-a",
            )
        assert exc.value.status_code == 500
        assert "Database pipeline collapsed" in exc.value.detail


def test_ai_router_maps_advisor_error_to_500():
    """AI Router maps AIAdvisorError to HTTP 500 Internal Server Error."""
    with patch.object(
        ai_advisor_router.ai_advisor_service,
        "generate_recommendations",
        side_effect=AIAdvisorError("AI generation pipeline failed unrecoverably"),
    ):
        with pytest.raises(HTTPException) as exc:
            ai_advisor_router.get_ai_recommendations(
                require_data=False,
                enterprise_id="company-a",
            )
        assert exc.value.status_code == 500
        assert "AI generation pipeline failed unrecoverably" in exc.value.detail


def test_ai_router_maps_insufficient_data_to_404():
    """AI Router maps InsufficientDataError to HTTP 404 Not Found."""
    with patch.object(
        ai_advisor_router.ai_advisor_service,
        "generate_recommendations",
        side_effect=InsufficientDataError("No activities found for recommendations"),
    ):
        with pytest.raises(HTTPException) as exc:
            ai_advisor_router.get_ai_recommendations(
                require_data=True,
                enterprise_id="company-a",
            )
        assert exc.value.status_code == 404
        assert "No activities found for recommendations" in exc.value.detail
