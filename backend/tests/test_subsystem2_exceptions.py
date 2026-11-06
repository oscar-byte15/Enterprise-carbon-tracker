"""Hometask 4: Subsystem 2 error handling and API/database tests.

Run from backend/: python -m pytest tests/test_subsystem2_exceptions.py -v
MongoMock isolates data; no running MongoDB is necessary.
"""
from datetime import date
from unittest.mock import patch

import mongomock
import pytest
from fastapi import HTTPException

from app.activities.exceptions import (
    Subsystem2Error,
    InvalidActivityError,
    EmissionFactorNotFoundError,
    ActivityNotFoundError,
)
from app.activities.oop import ActivityRecord, CalculationService, EmissionFactor
from app.activities.mongo_repository import MongoActivityRepository
from app.activities.schemas import ActivityCreate

# The router imports database-backed dependencies at module load time.
# Mock the MongoDB client before importing it to avoid a live connection.
with patch("pymongo.MongoClient", return_value=mongomock.MongoClient()):
    from app.activities import router as activity_routes


def activity(amount=10, unit="kWh", category="electricity", activity_type="Grid electricity"):
    return ActivityRecord(
        category, activity_type, amount, unit, date(2026, 11, 6), "company-a"
    )


def payload():
    return ActivityCreate(
        category="electricity", type="Grid electricity",
        amount=10, unit="kWh", date=date(2026, 11, 6)
    )


def test_subsystem2_exception_hierarchy():
    assert issubclass(InvalidActivityError, Subsystem2Error)
    assert issubclass(EmissionFactorNotFoundError, Subsystem2Error)
    assert issubclass(ActivityNotFoundError, Subsystem2Error)
    assert issubclass(Subsystem2Error, ValueError)


@pytest.mark.parametrize("amount", [-10, 0, float("nan")])
def test_activity_rejects_invalid_amount(amount):
    with pytest.raises(InvalidActivityError, match="positive finite"):
        activity(amount=amount)


def test_factor_rejects_negative_value():
    with pytest.raises(InvalidActivityError, match="non-negative"):
        EmissionFactor("electricity", "Grid electricity", -0.1, "kWh", "Test")


def test_unknown_category_raises_specific_exception():
    with pytest.raises(EmissionFactorNotFoundError, match="Unknown category"):
        CalculationService().get_emission_factor("unknown", "Grid electricity")


def test_unknown_type_raises_specific_exception():
    with pytest.raises(EmissionFactorNotFoundError, match="Unknown activity type"):
        CalculationService().get_emission_factor("electricity", "Unknown type")


def test_invalid_unit_raises_specific_exception():
    with pytest.raises(InvalidActivityError, match="does not match"):
        CalculationService().calculate(activity(unit="L"))


def test_prepare_activity_returns_calculated_fields():
    result = activity_routes.prepare_activity(payload(), "company-a")
    assert result["co2e_kg"] == 3.52
    assert result["period"] == "2026-11"
    assert result["emission_factor"] == 0.352


def test_prepare_activity_maps_domain_error_to_422():
    # model_copy intentionally bypasses Pydantic revalidation to exercise
    # the router's handling of errors from its own domain layer.
    bad = payload().model_copy(update={"unit": "L"})
    with pytest.raises(HTTPException) as exc:
        activity_routes.prepare_activity(bad, "company-a")
    assert exc.value.status_code == 422
    assert "does not match" in exc.value.detail


def test_create_route_saves_prepared_activity():
    with patch.object(activity_routes.activity_repository, "create", return_value={"id": "a1"}) as create:
        result = activity_routes.create_activity(payload(), enterprise_id="company-a")
    assert result["message"] == "Activity created successfully"
    create.assert_called_once()
    assert create.call_args.args[1] == "company-a"


def test_read_missing_activity_maps_to_404():
    with patch.object(activity_routes.activity_repository, "get_by_id", return_value=None):
        with pytest.raises(HTTPException) as exc:
            activity_routes.get_activity_by_id("missing", enterprise_id="company-a")
    assert exc.value.status_code == 404


def test_update_missing_activity_maps_to_404():
    with patch.object(activity_routes.activity_repository, "update", return_value=None):
        with pytest.raises(HTTPException) as exc:
            activity_routes.update_activity("missing", payload(), enterprise_id="company-a")
    assert exc.value.status_code == 404


def test_delete_missing_activity_maps_to_404():
    with patch.object(activity_routes.activity_repository, "delete", return_value=False):
        with pytest.raises(HTTPException) as exc:
            activity_routes.delete_activity("missing", enterprise_id="company-a")
    assert exc.value.status_code == 404


def test_repository_isolates_enterprise_activity_records():
    collection = mongomock.MongoClient()["test_carbon"]["activity_records"]
    repository = MongoActivityRepository(collection=collection)
    created = repository.create({"category": "electricity", "amount": 10}, "company-a")
    assert repository.get_by_id(created["id"], "company-a") is not None
    assert repository.get_by_id(created["id"], "company-b") is None
    assert repository.get_all("company-b") == []
    assert repository.update(created["id"], {"amount": 99}, "company-b") is None
    assert repository.delete(created["id"], "company-b") is False
    assert repository.get_by_id(created["id"], "company-a")["amount"] == 10
