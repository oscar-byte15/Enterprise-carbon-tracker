
"""
Unit Tests - Category-Specific Activity Validation

NFR4:
    Verify valid and invalid combinations of
    category, activity type, and measurement unit.
"""

import pytest

from datetime import date
from pydantic import ValidationError

from app.activities.schemas import ActivityCreate


# ------------------------------------------------------------
# TEST 1-4: Valid category-specific activity requests
# ------------------------------------------------------------

@pytest.mark.parametrize(
    "category,activity_type,unit",
    [
        ("electricity", "Grid electricity", "kWh"),
        ("heating", "Natural gas", "kWh"),
        ("transport", "Diesel", "L"),
        ("waste", "Plastic - Recycling", "kg"),
    ],
)
def test_valid_category_schema(
    category, activity_type, unit
):
    """
    A valid activity configuration must be accepted.
    """

    activity = ActivityCreate(
        category=category,
        type=activity_type,
        amount=100,
        unit=unit,
        date=date(2026, 10, 31),
    )

    assert activity.category == category
    assert activity.unit == unit


# ------------------------------------------------------------
# TEST 5: Type does not belong to the category
# ------------------------------------------------------------

def test_invalid_category_type_combination():
    """
    Diesel cannot be registered as electricity.
    """

    with pytest.raises(
        ValidationError,
        match="Invalid activity type"
    ):
        ActivityCreate(
            category="electricity",
            type="Diesel",
            amount=100,
            unit="L",
            date=date(2026, 10, 31),
        )


# ------------------------------------------------------------
# TEST 6: Incorrect measurement unit
# ------------------------------------------------------------

def test_invalid_category_unit():
    """
    Natural gas must use the configured unit, kWh.
    """

    with pytest.raises(
        ValidationError,
        match="Invalid unit"
    ):
        ActivityCreate(
            category="heating",
            type="Natural gas",
            amount=100,
            unit="kg",
            date=date(2026, 10, 31),
        )


# ------------------------------------------------------------
# TEST 7: Non-positive amount
# ------------------------------------------------------------

def test_invalid_amount():
    """
    Negative consumption amounts must be rejected.
    """

    with pytest.raises(ValidationError):
        ActivityCreate(
            category="transport",
            type="Petrol",
            amount=-50,
            unit="L",
            date=date(2026, 10, 31),
        )


# ------------------------------------------------------------
# TEST 8: Non-finite amount
# ------------------------------------------------------------

def test_non_finite_amount():
    """
    Infinity must never be accepted as consumption.
    """

    with pytest.raises(ValidationError):
        ActivityCreate(
            category="electricity",
            type="Grid electricity",
            amount=float("inf"),
            unit="kWh",
            date=date(2026, 10, 31),
        )
