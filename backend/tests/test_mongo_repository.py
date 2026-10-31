
"""
Unit Tests - MongoActivityRepository

Subsystem 2: Carbon Activity Management

Purpose:
    Verify CRUD operations and enterprise-based data isolation.

Testing tools:
    Pytest, MongoMock, unittest.mock

Notes:
    - No real MongoDB connection is required.
    - Each test uses an isolated mock collection.
    - Production data is never modified.
"""

from unittest.mock import patch

import mongomock
import pytest


# ============================================================
# TEST FIXTURE: MOCK MONGODB REPOSITORY
# ============================================================

@pytest.fixture
def repository():
    """
    Create a repository connected to an in-memory collection.

    The production module creates a MongoDB connection during
    import, so MongoClient is patched while importing it.

    Each test receives an independent collection.
    """

    # Prevent the module-level repository from connecting
    # to the real MongoDB server during the initial import.
    with patch("pymongo.MongoClient"):
        from app.activities.mongo_repository import (
            MongoActivityRepository
        )

    # Arrange: Create a fake MongoDB client and collection.
    client = mongomock.MongoClient()
    collection = client["test_carbon_tracker"]["activity_records"]

    # Inject the fake collection into our real repository class.
    repo = MongoActivityRepository(collection=collection)

    yield repo

    # Cleanup: Close the temporary mock client.
    client.close()


@pytest.fixture
def sample_activity():
    """
    Provide reusable activity data for CRUD tests.
    """
    return {
        "category": "electricity",
        "type": "Grid electricity",
        "amount": 500,
        "unit": "kWh",
        "date": "2026-10-31",
        "period": "2026-10",
        "emission_factor": 0.352,
        "co2e_kg": 176.0,
        "factor_source": "Umweltbundesamt (UBA)"
    }


# ============================================================
# TEST 1: CREATE ACTIVITY
# ============================================================

def test_create_activity(repository, sample_activity):
    """
    Verify that CREATE stores a new activity.

    Each activity must receive:
        - A unique activity ID.
        - The enterprise ID of its owner.
    """

    # Act: Create a carbon activity for Enterprise A.
    created = repository.create(
        sample_activity,
        "enterprise-A"
    )

    # Assert: Verify generated identifiers.
    assert created["id"]
    assert created["enterprise_id"] == "enterprise-A"

    # Assert: Verify that MongoDB contains the record.
    assert repository.collection.count_documents({}) == 1


# ============================================================
# TEST 2: READ ALL ACTIVITIES
# ============================================================

def test_get_all_activities(repository, sample_activity):
    """
    Verify that READ ALL returns only records belonging
    to the requested enterprise.
    """

    # Arrange: Create records for two different enterprises.
    repository.create(sample_activity, "enterprise-A")
    repository.create(sample_activity, "enterprise-A")
    repository.create(sample_activity, "enterprise-B")

    # Act: Query activities for Enterprise A.
    activities = repository.get_all("enterprise-A")

    # Assert: Only Enterprise A's records should appear.
    assert len(activities) == 2
    assert all(
        activity["enterprise_id"] == "enterprise-A"
        for activity in activities
    )


# ============================================================
# TEST 3: READ ACTIVITY BY ID
# ============================================================

def test_get_activity_by_id(repository, sample_activity):
    """
    Verify that an enterprise can retrieve its own activity
    by its unique identifier.
    """

    # Arrange: Create an activity.
    created = repository.create(
        sample_activity,
        "enterprise-A"
    )

    # Act: Retrieve the activity by ID.
    result = repository.get_by_id(
        created["id"],
        "enterprise-A"
    )

    # Assert: The correct activity is returned.
    assert result is not None
    assert result["id"] == created["id"]
    assert result["amount"] == 500


# ============================================================
# TEST 4: PREVENT UNAUTHORIZED READ
# ============================================================

def test_enterprise_cannot_read_other_enterprise_activity(
    repository, sample_activity
):
    """
    Verify enterprise data isolation.

    Enterprise B must not be able to access
    an activity belonging to Enterprise A.
    """

    # Arrange: Create an activity owned by Enterprise A.
    created = repository.create(
        sample_activity,
        "enterprise-A"
    )

    # Act: Attempt access as Enterprise B.
    result = repository.get_by_id(
        created["id"],
        "enterprise-B"
    )

    # Assert: Access must be denied.
    assert result is None


# ============================================================
# TEST 5: UPDATE ACTIVITY
# ============================================================

def test_update_activity(repository, sample_activity):
    """
    Verify that UPDATE modifies an existing activity
    while preserving its identity and enterprise ownership.
    """

    # Arrange: Create an activity.
    created = repository.create(
        sample_activity,
        "enterprise-A"
    )

    updated_data = {
        **sample_activity,
        "amount": 100,
        "co2e_kg": 35.2
    }

    # Act: Update the activity.
    updated = repository.update(
        created["id"],
        updated_data,
        "enterprise-A"
    )

    # Assert: Verify updated values.
    assert updated is not None
    assert updated["amount"] == 100
    assert updated["co2e_kg"] == 35.2

    # Assert: Identifiers remain unchanged.
    assert updated["id"] == created["id"]
    assert updated["enterprise_id"] == "enterprise-A"


# ============================================================
# TEST 6: PREVENT UNAUTHORIZED UPDATE
# ============================================================

def test_enterprise_cannot_update_other_enterprise_activity(
    repository, sample_activity
):
    """
    Verify that an enterprise cannot update
    a record belonging to another enterprise.
    """

    # Arrange: Create an activity owned by Enterprise A.
    created = repository.create(
        sample_activity,
        "enterprise-A"
    )

    changed_data = {
        **sample_activity,
        "amount": 999
    }

    # Act: Attempt to update as Enterprise B.
    result = repository.update(
        created["id"],
        changed_data,
        "enterprise-B"
    )

    # Assert: Update must be rejected.
    assert result is None

    # Assert: The original value remains unchanged.
    original = repository.get_by_id(
        created["id"],
        "enterprise-A"
    )

    assert original["amount"] == 500


# ============================================================
# TEST 7: DELETE ACTIVITY
# ============================================================

def test_delete_activity(repository, sample_activity):
    """
    Verify that DELETE permanently removes
    an activity owned by the requesting enterprise.
    """

    # Arrange: Create an activity.
    created = repository.create(
        sample_activity,
        "enterprise-A"
    )

    # Act: Delete the activity.
    deleted = repository.delete(
        created["id"],
        "enterprise-A"
    )

    # Assert: Delete reports success.
    assert deleted is True

    # Assert: The activity no longer exists.
    assert repository.get_by_id(
        created["id"],
        "enterprise-A"
    ) is None


# ============================================================
# TEST 8: PREVENT UNAUTHORIZED DELETE
# ============================================================

def test_enterprise_cannot_delete_other_enterprise_activity(
    repository, sample_activity
):
    """
    Verify that Enterprise B cannot delete
    an activity belonging to Enterprise A.
    """

    # Arrange: Create an activity owned by Enterprise A.
    created = repository.create(
        sample_activity,
        "enterprise-A"
    )

    # Act: Attempt deletion as Enterprise B.
    deleted = repository.delete(
        created["id"],
        "enterprise-B"
    )

    # Assert: Unauthorized deletion must fail.
    assert deleted is False

    # Assert: The original record still exists.
    original = repository.get_by_id(
        created["id"],
        "enterprise-A"
    )

    assert original is not None
