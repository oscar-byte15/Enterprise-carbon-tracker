
import pytest
import mongomock

from app.mongo_store import MongoStore


@pytest.fixture
def store():
    client = mongomock.MongoClient()
    database = client["test_enterprise_carbon_tracker"]
    return MongoStore(database=database)


def test_create_enterprise(store):
    result = store.create_enterprise(
        email="test@example.com",
        password="Password123!",
        company_name="Test Company",
        industry="Technology",
    )

    assert result["user"]["email"] == "test@example.com"
    assert result["enterprise"]["company_name"] == "Test Company"
    assert result["user"]["enterprise_id"] == result["enterprise"]["enterprise_id"]


def test_duplicate_email(store):
    store.create_enterprise(
        "test@example.com",
        "Password123!",
        "Company A",
        "Technology",
    )

    with pytest.raises(ValueError, match="Email is already registered"):
        store.create_enterprise(
            "TEST@example.com",
            "Password456!",
            "Company B",
            "Energy",
        )


def test_get_user_by_email(store):
    store.create_enterprise(
        "Test@Example.com",
        "Password123!",
        "Test Company",
        "Technology",
    )

    user = store.get_user_by_email("test@example.com")

    assert user is not None
    assert user["email"] == "test@example.com"
    assert "_id" not in user


def test_get_enterprise(store):
    result = store.create_enterprise(
        "test@example.com",
        "Password123!",
        "Test Company",
        "Technology",
    )

    enterprise_id = result["enterprise"]["enterprise_id"]
    enterprise = store.get_enterprise(enterprise_id)

    assert enterprise is not None
    assert enterprise["company_name"] == "Test Company"


def test_update_enterprise(store):
    result = store.create_enterprise(
        "test@example.com",
        "Password123!",
        "Test Company",
        "Technology",
    )

    enterprise_id = result["enterprise"]["enterprise_id"]

    updated = store.update_enterprise(
        enterprise_id,
        {"company_name": "Updated Company", "city": "Dortmund"},
    )

    assert updated["company_name"] == "Updated Company"
    assert updated["city"] == "Dortmund"


def test_create_department(store):
    result = store.create_enterprise(
        "test@example.com",
        "Password123!",
        "Test Company",
        "Technology",
    )

    enterprise_id = result["enterprise"]["enterprise_id"]

    department = store.create_department(
        enterprise_id,
        "IT Department",
        "IT infrastructure",
    )

    assert department["name"] == "IT Department"
    assert department["enterprise_id"] == enterprise_id


def test_list_departments(store):
    result = store.create_enterprise(
        "test@example.com",
        "Password123!",
        "Test Company",
        "Technology",
    )

    enterprise_id = result["enterprise"]["enterprise_id"]

    store.create_department(enterprise_id, "IT")
    store.create_department(enterprise_id, "HR")

    departments = store.list_departments(enterprise_id)

    assert len(departments) == 2
    assert {d["name"] for d in departments} == {"IT", "HR"}


def test_data_persistence(store):
    result = store.create_enterprise(
        "test@example.com",
        "Password123!",
        "Test Company",
        "Technology",
    )

    # Create another store using the same mock database.
    another_store = MongoStore(
        database=store.users.database
    )

    user = another_store.get_user_by_email("test@example.com")

    assert user is not None
    assert user["enterprise_id"] == result["enterprise"]["enterprise_id"]
