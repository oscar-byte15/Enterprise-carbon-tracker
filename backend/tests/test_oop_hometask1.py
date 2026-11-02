"""Unit tests for Hometask 1 (Subsystem 2 OOP classes)."""
from datetime import date

import pytest

from app.activities.oop import ActivityRecord, CalculationService, EmissionFactor


def make_activity(amount=10, unit="kWh"):
    return ActivityRecord("electricity", "Grid electricity", amount, unit,
                          date(2026, 11, 2), "enterprise-1")


def test_activity_initialization_and_getters():
    activity = make_activity()
    assert activity.get_category() == "electricity"
    assert activity.get_period() == "2026-11"
    assert activity.get_enterprise_id() == "enterprise-1"


def test_activity_setters_and_validation():
    activity = make_activity()
    activity.set_amount(15)
    assert activity.get_amount() == 15
    with pytest.raises(ValueError):
        activity.set_amount(-1)
    with pytest.raises(ValueError):
        activity.set_amount(float("nan"))


def test_emission_factor_getters_setters_matches():
    factor = EmissionFactor("electricity", "Grid electricity",
                            0.352, "kWh", "UBA")
    assert factor.matches(make_activity())
    factor.set_factor(0.4)
    assert factor.get_factor() == 0.4
    with pytest.raises(ValueError):
        factor.set_factor(-0.1)
    assert not factor.matches(make_activity(unit="L"))


def test_service_uses_production_json_and_rounds():
    service = CalculationService()
    result = service.calculate(make_activity())
    assert result["co2e_kg"] == 3.52
    assert result["emission_factor"] == 0.352


def test_service_rejects_wrong_units():
    service = CalculationService()
    with pytest.raises(ValueError):
        service.calculate(make_activity(unit="L"))


def test_service_custom_catalog_and_encapsulation():
    service = CalculationService({
        "electricity": {
            "Grid electricity": {
                "factor": 0.5, "unit": "kWh", "source": "Test"
            }
        }
    })
    catalog = service.get_factor_catalog()
    catalog["electricity"]["Grid electricity"]["factor"] = 99
    assert service.calculate(make_activity())["co2e_kg"] == 5.0
