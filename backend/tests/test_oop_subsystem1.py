
import pytest

from app.oop_subsystem1 import User, Enterprise, Department


# ---------- User Tests ----------

def test_user_initialization():
    user = User("TEST@example.com", "hashed_password", "ent001")

    assert user.get_email() == "test@example.com"
    assert user.get_role() == "admin"


def test_user_set_email():
    user = User("old@example.com", "hashed_password", "ent001")
    user.set_email("NEW@example.com")

    assert user.get_email() == "new@example.com"


def test_user_set_role():
    user = User("test@example.com", "hashed_password", "ent001")
    user.set_role("member")

    assert user.get_role() == "member"


def test_user_invalid_email():
    user = User("test@example.com", "hashed_password", "ent001")

    with pytest.raises(ValueError):
        user.set_email("")


# ---------- Enterprise Tests ----------

def test_enterprise_initialization():
    enterprise = Enterprise("BMW", "Automotive")

    assert enterprise.get_company_name() == "BMW"
    assert enterprise.get_industry() == "Automotive"
    assert enterprise.get_enterprise_id()


def test_enterprise_set_company_name():
    enterprise = Enterprise("BMW", "Automotive")
    enterprise.set_company_name("Mercedes")

    assert enterprise.get_company_name() == "Mercedes"


def test_enterprise_update_profile():
    enterprise = Enterprise("BMW", "Automotive")
    enterprise.update_profile(
        company_name="Mercedes",
        industry="Manufacturing",
        address="Berlin"
    )

    assert enterprise.get_company_name() == "Mercedes"
    assert enterprise.get_industry() == "Manufacturing"
    assert enterprise.get_address() == "Berlin"


def test_enterprise_invalid_name():
    enterprise = Enterprise("BMW", "Automotive")

    with pytest.raises(ValueError):
        enterprise.set_company_name("")


# ---------- Department Tests ----------

def test_department_initialization():
    department = Department("ent001", "IT", "Technical Support")

    assert department.get_name() == "IT"
    assert department.get_description() == "Technical Support"
    assert department.get_enterprise_id() == "ent001"


def test_department_set_name():
    department = Department("ent001", "IT")
    department.set_name("HR")

    assert department.get_name() == "HR"


def test_department_update_details():
    department = Department("ent001", "IT")
    department.update_details(
        name="Finance",
        description="Financial Management"
    )

    assert department.get_name() == "Finance"
    assert department.get_description() == "Financial Management"


def test_department_invalid_name():
    department = Department("ent001", "IT")

    with pytest.raises(ValueError):
        department.set_name("")
