"""Unit tests for Hometask 1 (Subsystem 3 OOP classes).

Verifies EmissionMetric, AnalyticsEngine, and SustainabilityAdvisor domain classes,
encapsulation, setters/getters, validation, composition, and dependencies.
"""
from decimal import Decimal
import pytest

from app.analytics.oop import AnalyticsEngine, EmissionMetric, SustainabilityAdvisor


# =========================================================================
# 1. EmissionMetric Unit Tests
# =========================================================================

def test_emission_metric_initialization_and_getters():
    metric = EmissionMetric(
        category="electricity",
        co2e_kg=1250.50,
        percentage=45.2,
        activity_count=8,
    )
    assert metric.get_category() == "electricity"
    assert metric.get_co2e_kg() == 1250.50
    assert metric.get_percentage() == 45.2
    assert metric.get_activity_count() == 8

    d = metric.to_dict()
    assert d["category"] == "electricity"
    assert d["co2e_kg"] == 1250.50
    assert d["percentage"] == 45.2
    assert d["activity_count"] == 8


def test_emission_metric_setters_and_updates():
    metric = EmissionMetric("transport", 100.0)
    assert metric.get_percentage() == 0.0
    assert metric.get_activity_count() == 0

    metric.set_category("transport-fleet")
    assert metric.get_category() == "transport-fleet"

    metric.set_co2e_kg(250.75)
    assert metric.get_co2e_kg() == 250.75

    metric.set_percentage(20.5)
    assert metric.get_percentage() == 20.5

    metric.set_activity_count(3)
    assert metric.get_activity_count() == 3


def test_emission_metric_validation_errors():
    # Empty / invalid category
    with pytest.raises(ValueError, match="Category is required"):
        EmissionMetric("", 100.0)
    with pytest.raises(ValueError, match="Category is required"):
        EmissionMetric("   ", 100.0)

    # Negative or non-numeric emissions
    with pytest.raises(ValueError, match="cannot be negative"):
        EmissionMetric("electricity", -5.0)
    with pytest.raises(ValueError, match="must be numeric"):
        EmissionMetric("electricity", "invalid-number")

    # Percentage range violations
    with pytest.raises(ValueError, match="between 0 and 100"):
        EmissionMetric("electricity", 100.0, percentage=-1.0)
    with pytest.raises(ValueError, match="between 0 and 100"):
        EmissionMetric("electricity", 100.0, percentage=100.1)

    # Activity count validations
    with pytest.raises(ValueError, match="cannot be negative"):
        EmissionMetric("electricity", 100.0, activity_count=-1)
    with pytest.raises(ValueError, match="must be an integer"):
        EmissionMetric("electricity", 100.0, activity_count=2.5)  # type: ignore[arg-type]


# =========================================================================
# 2. AnalyticsEngine Unit Tests (Composition & Aggregations)
# =========================================================================

def test_analytics_engine_empty_initialization():
    engine = AnalyticsEngine("enterprise-42")
    assert engine.get_enterprise_id() == "enterprise-42"
    assert engine.get_total_co2e_kg() == 0.0
    assert engine.get_top_category() is None
    assert engine.get_metrics() == {}

    summary = engine.generate_summary()
    assert summary["enterprise_id"] == "enterprise-42"
    assert summary["total_co2e_kg"] == 0.0
    assert summary["total_activities"] == 0
    assert summary["top_category"] is None
    assert summary["category_breakdown"] == []


def test_analytics_engine_add_metric_and_composition():
    engine = AnalyticsEngine("enterprise-test")
    engine.add_metric("electricity", 400.0, count=2)
    engine.add_metric("transport", 600.0, count=3)

    # Verify total
    assert engine.get_total_co2e_kg() == 1000.0

    # Composition: Engine owns EmissionMetric objects
    metrics = engine.get_metrics()
    assert len(metrics) == 2
    assert isinstance(metrics["electricity"], EmissionMetric)
    assert isinstance(metrics["transport"], EmissionMetric)

    # Verify recalculate_percentages
    assert metrics["electricity"].get_percentage() == 40.0
    assert metrics["transport"].get_percentage() == 60.0

    # Verify top category
    assert engine.get_top_category() == "transport"


def test_analytics_engine_aggregates_existing_category():
    engine = AnalyticsEngine("enterprise-test")
    engine.add_metric("heating", 150.0, count=1)
    engine.add_metric("heating", 50.0, count=2)

    assert engine.get_total_co2e_kg() == 200.0
    metric = engine.get_metrics()["heating"]
    assert metric.get_co2e_kg() == 200.0
    assert metric.get_activity_count() == 3
    assert metric.get_percentage() == 100.0


def test_analytics_engine_raw_activities_constructor():
    raw_data = [
        {"category": "electricity", "co2e_kg": 300.0, "count": 2},
        {"category": "waste", "co2e_kg": 100.0, "count": 1},
    ]
    engine = AnalyticsEngine("ent-raw", raw_activities=raw_data)
    assert engine.get_total_co2e_kg() == 400.0
    assert engine.get_top_category() == "electricity"
    summary = engine.generate_summary()
    assert summary["total_activities"] == 3
    assert summary["top_category_percentage"] == 75.0
    assert len(summary["category_breakdown"]) == 2


def test_analytics_engine_encapsulation_and_defensive_copies():
    engine = AnalyticsEngine("ent-defensive")
    engine.add_metric("electricity", 500.0)

    # Mutating returned dictionary does not alter engine internal state
    metrics = engine.get_metrics()
    metrics["corrupted"] = None  # type: ignore[assignment]
    assert "corrupted" not in engine.get_metrics()


def test_analytics_engine_validation_errors():
    with pytest.raises(ValueError, match="Enterprise ID is required"):
        AnalyticsEngine("")
    with pytest.raises(ValueError, match="Enterprise ID is required"):
        AnalyticsEngine("   ")

    engine = AnalyticsEngine("ent-1")
    with pytest.raises(ValueError, match="Category is required"):
        engine.add_metric("", 50.0)
    with pytest.raises(ValueError, match="cannot be negative"):
        engine.add_metric("electricity", -10.0)
    with pytest.raises(ValueError, match="non-negative integer"):
        engine.add_metric("electricity", 10.0, count=-1)


# =========================================================================
# 3. SustainabilityAdvisor Unit Tests (Dependency & Advisory)
# =========================================================================

def test_sustainability_advisor_initialization():
    advisor = SustainabilityAdvisor()
    assert advisor.get_advisor_mode() == "rules"
    catalog = advisor.get_catalog()
    assert "electricity" in catalog
    assert "heating" in catalog
    assert "transport" in catalog
    assert "waste" in catalog
    assert "general" in catalog


def test_sustainability_advisor_setters_and_mode_validation():
    advisor = SustainabilityAdvisor()
    advisor.set_advisor_mode("ai")
    assert advisor.get_advisor_mode() == "ai"

    with pytest.raises(ValueError, match="Advisor mode must be 'rules' or 'ai'"):
        advisor.set_advisor_mode("unsupported-mode")


def test_sustainability_advisor_recommends_for_top_category():
    engine = AnalyticsEngine("ent-advise")
    engine.add_metric("electricity", 800.0)
    engine.add_metric("transport", 200.0)

    advisor = SustainabilityAdvisor()
    recs = advisor.generate_recommendations(engine)

    assert len(recs) <= 3
    assert len(recs) == 3
    for r in recs:
        assert r["category"] == "electricity"
        assert r["priority"] in ["High", "Medium", "Low"]
        assert "title" in r
        assert "description" in r


def test_sustainability_advisor_baseline_for_empty_engine():
    engine = AnalyticsEngine("ent-empty")
    advisor = SustainabilityAdvisor()
    recs = advisor.generate_recommendations(engine)

    assert len(recs) >= 1
    assert recs[0]["category"] == "general"


def test_sustainability_advisor_rejects_invalid_analytics_instance():
    advisor = SustainabilityAdvisor()
    with pytest.raises(ValueError, match="must be an instance of AnalyticsEngine"):
        advisor.generate_recommendations({"top_category": "electricity"})  # type: ignore[arg-type]


def test_sustainability_advisor_catalog_encapsulation():
    advisor = SustainabilityAdvisor()
    cat = advisor.get_catalog()
    cat["electricity"].append({"title": "External Injection"})

    fresh_cat = advisor.get_catalog()
    assert len(fresh_cat["electricity"]) == 3
