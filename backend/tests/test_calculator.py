
"""
Unit Tests - Carbon Emission Calculation Engine

Subsystem 2: Carbon Activity Management & Calculation Engine

Purpose:
    Validate emission calculations for supported activity types,
    input validation, rounding behavior, and emission factor metadata.

Testing framework:
    Pytest

Notes:
    - These tests do not require MongoDB.
    - These tests do not require FastAPI or React.
    - Each test runs independently.
    - Expected values are based on the configured emission factors.
"""

import pytest

from app.activities.calculator import calculate_emissions


# ============================================================
# TEST 1-7: VALID EMISSION CALCULATIONS
# ============================================================

@pytest.mark.parametrize(
    "category,activity_type,amount,unit,expected",
    [
        # Electricity:
        # 500 kWh * 0.352 kg CO2e/kWh = 176.00 kg CO2e
        ("electricity", "Grid electricity", 500, "kWh", 176.00),

        # Heating:
        # 500 kWh * 0.18296 kg CO2e/kWh = 91.48 kg CO2e
        ("heating", "Natural gas", 500, "kWh", 91.48),

        # Transport - Petrol:
        # 50 L * 2.06916 kg CO2e/L = 103.46 kg CO2e
        ("transport", "Petrol", 50, "L", 103.46),

        # Transport - Diesel:
        # 50 L * 2.57082 kg CO2e/L = 128.54 kg CO2e
        ("transport", "Diesel", 50, "L", 128.54),

        # Waste - Plastic Recycling:
        # 100 kg * 0.00465358 = 0.47 kg CO2e
        ("waste", "Plastic - Recycling", 100, "kg", 0.47),

        # Waste - Organic Composting:
        # 100 kg * 0.00900687 = 0.90 kg CO2e
        ("waste", "Organic - Composting", 100, "kg", 0.90),

        # Waste - General Landfill:
        # 100 kg * 0.49729 = 49.73 kg CO2e
        ("waste", "General - Landfill", 100, "kg", 49.73),
    ],
)
def test_calculate_emissions(
    category, activity_type, amount, unit, expected
):
    """
    Verify that each supported activity type produces
    the expected CO2e emissions using its emission factor.

    Also verify that the result includes valid
    factor metadata for traceability.
    """

    # Act: Calculate emissions using the given input.
    result = calculate_emissions(
        category=category,
        activity_type=activity_type,
        amount=amount,
        unit=unit,
    )

    # Assert: Verify the calculated emissions.
    assert result["co2e_kg"] == expected

    # Assert: The emission factor must not be negative.
    assert result["emission_factor"] >= 0

    # Assert: Emission factor provenance must be available.
    assert result["factor_source"]
    assert result["factor_year"] is not None
    assert result["factor_source_url"]


# ============================================================
# TEST 8: NEGATIVE AMOUNT VALIDATION
# ============================================================

def test_negative_amount():
    """
    Verify that negative activity quantities are rejected.

    An activity cannot have a negative consumption amount.
    The Calculation Engine must raise a ValueError.
    """

    # Act and Assert: A negative amount must raise an error.
    with pytest.raises(ValueError, match="positive"):
        calculate_emissions(
            "electricity",
            "Grid electricity",
            -100,
            "kWh",
        )


# ============================================================
# TEST 9: ZERO AMOUNT VALIDATION
# ============================================================

def test_zero_amount():
    """
    Verify that zero activity quantities are rejected.

    The current business rules require an amount greater
    than zero for each carbon activity.
    """

    # Act and Assert: Zero is not a valid activity amount.
    with pytest.raises(ValueError, match="positive"):
        calculate_emissions(
            "electricity",
            "Grid electricity",
            0,
            "kWh",
        )


# ============================================================
# TEST 10: INVALID UNIT VALIDATION
# ============================================================

def test_invalid_unit():
    """
    Verify that the Calculation Engine rejects
    units that do not match the configured factor.

    Example:
        Electricity requires kWh, not kg.
    """

    # Act and Assert: Incorrect unit must raise ValueError.
    with pytest.raises(ValueError, match="Invalid unit"):
        calculate_emissions(
            "electricity",
            "Grid electricity",
            100,
            "kg",
        )


# ============================================================
# TEST 11: UNKNOWN CATEGORY VALIDATION
# ============================================================

def test_unknown_category():
    """
    Verify that unsupported activity categories are rejected.

    Only electricity, heating, transport, and waste
    are supported by the current Calculation Engine.
    """

    # Act and Assert: Unknown category must be rejected.
    with pytest.raises(ValueError, match="Unknown category"):
        calculate_emissions(
            "unknown",
            "Grid electricity",
            100,
            "kWh",
        )


# ============================================================
# TEST 12: UNKNOWN ACTIVITY TYPE VALIDATION
# ============================================================

def test_unknown_activity_type():
    """
    Verify that an activity type not defined in
    emission_factors.json is rejected.

    This prevents calculations using nonexistent factors.
    """

    # Act and Assert: Unsupported activity type raises error.
    with pytest.raises(ValueError, match="Unknown activity type"):
        calculate_emissions(
            "electricity",
            "Unknown electricity",
            100,
            "kWh",
        )


# ============================================================
# TEST 13: EMISSION ROUNDING
# ============================================================

def test_rounding():
    """
    Verify that calculated CO2e emissions are rounded
    to two decimal places using ROUND_HALF_UP.

    Calculation:
        1.234 kWh * 0.352 = 0.434368
        Expected result = 0.43 kg CO2e
    """

    # Act: Calculate emissions with a decimal input.
    result = calculate_emissions(
        "electricity",
        "Grid electricity",
        1.234,
        "kWh",
    )

    # Assert: Result must be rounded to two decimals.
    assert result["co2e_kg"] == 0.43


# ============================================================
# TEST 14: EMISSION FACTOR METADATA
# ============================================================

def test_metadata_is_preserved():
    """
    Verify that emission factor metadata is returned.

    Metadata is important for transparency and traceability.
    It allows users to identify the factor source,
    reference year, region, and waste treatment method.
    """

    # Act: Calculate emissions for recycled plastic.
    result = calculate_emissions(
        "waste",
        "Plastic - Recycling",
        100,
        "kg",
    )

    # Assert: Verify the configured region.
    assert result["factor_region"] == "United Kingdom"

    # Assert: Verify the reference year.
    assert result["factor_year"] == 2026

    # Assert: Verify the waste treatment method.
    assert result["treatment_method"] == "Closed-loop recycling"

    # Assert: Verify the official source identifier.
    assert "DESNZ" in result["factor_source"]
