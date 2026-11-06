from unittest.mock import patch

import mongomock
import pytest
from pymongo.errors import DuplicateKeyError

from app.exceptions import (
    EmailAlreadyRegisteredError,
    EnterpriseNotFoundError,
    Subsystem1Error,
)
from app.mongo_store import MongoStore

with patch("app.mongo_store.MongoClient", return_value=mongomock.MongoClient()):
    from app import routes


@pytest.fixture
def store():
    client = mongomock.MongoClient()
    database = client["test_enterprise_carbon_tracker"]
    return MongoStore(database=database)


def test_custom_exceptions_are_value_error():
    assert issubclass(Subsystem1Error, ValueError)
    assert issubclass(EmailAlreadyRegisteredError, Subsystem1Error)
    assert issubclass(EnterpriseNotFoundError, Subsystem1Error)


def test_create_enterprise_raises_email_already_registered_error(store):
    store.create_enterprise(
        "test@example.com",
        "Password123!",
        "Test Company",
        "Technology",
    )

    with pytest.raises(EmailAlreadyRegisteredError, match="Email is already registered"):
        store.create_enterprise(
            "TEST@example.com",
            "Password456!",
            "Another Company",
            "Energy",
        )


def test_duplicate_key_error_is_wrapped(store):
    def raise_duplicate_key(*args, **kwargs):
        raise DuplicateKeyError("duplicate email")

    with patch.object(store.users, "insert_one", side_effect=raise_duplicate_key), pytest.raises(
        EmailAlreadyRegisteredError,
        match="Email is already registered",
    ):
        store.create_enterprise(
            "new@example.com",
            "Password123!",
            "Test Company",
            "Technology",
        )


def test_update_enterprise_raises_enterprise_not_found_error(store):
    with pytest.raises(EnterpriseNotFoundError, match="Enterprise not found"):
        store.update_enterprise(
            "missing-enterprise-id",
            {"company_name": "Any Company"},
        )


def test_register_route_maps_email_conflict_to_409():
    with patch(
        "app.routes.store.create_enterprise",
        side_effect=EmailAlreadyRegisteredError("Email is already registered"),
    ), pytest.raises(Exception) as excinfo:
        routes.register(
            routes.RegisterRequest(
                email="test@example.com",
                password="Password123!",
                company_name="Test Company",
                industry="Technology",
            )
        )

    assert excinfo.value.status_code == 409
    assert excinfo.value.detail == "Email is already registered"


def test_update_profile_route_maps_missing_enterprise_to_404():
    with patch(
        "app.routes.store.update_enterprise",
        side_effect=EnterpriseNotFoundError("Enterprise not found"),
    ), pytest.raises(Exception) as excinfo:
        routes.update_profile(
            payload=routes.EnterpriseProfileUpdate(company_name="Updated Company"),
            current_user={"enterprise_id": "missing-enterprise-id"},
        )

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Enterprise not found"
