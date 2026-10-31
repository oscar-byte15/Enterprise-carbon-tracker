
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


# Location of the JSON file
FACTORS_FILE = Path(__file__).with_name("emission_factors.json")


def load_emission_factors():
    """Load emission factors from the JSON configuration."""
    with FACTORS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def calculate_emissions(category, activity_type, amount, unit):
    """Calculate CO2e emissions for a carbon activity."""

    # 1. Validate the amount
    amount_decimal = Decimal(str(amount))

    if not amount_decimal.is_finite() or amount_decimal <= 0:
        raise ValueError("Amount must be a positive finite number")

    # 2. Load emission factors
    factors = load_emission_factors()

    # 3. Find the category
    category_factors = factors.get(category)

    if category_factors is None:
        raise ValueError(f"Unknown category: {category}")

    # 4. Find the activity type
    factor_data = category_factors.get(activity_type)

    if factor_data is None:
        raise ValueError(
            f"Unknown activity type: {activity_type}"
        )

    # 5. Validate the unit
    if unit != factor_data["unit"]:
        raise ValueError(
            f"Invalid unit: expected {factor_data['unit']}, got {unit}"
        )

    # 6. Calculate emissions
    emission_factor = Decimal(str(factor_data["factor"]))

    if not emission_factor.is_finite() or emission_factor < 0:
        raise ValueError("Emission factor must be finite and non-negative")

    emissions = amount_decimal * emission_factor

    # 7. Round to 2 decimal places
    emissions = emissions.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )

    # 8. Return calculation result

    return {
    "emission_factor": float(emission_factor),
    "factor_source": factor_data["source"],
    "factor_source_url": factor_data.get("source_url"),
    "factor_year": factor_data.get("year"),
    "factor_region": factor_data.get("region"),
    "factor_methodology": factor_data.get("methodology"),
    "treatment_method": factor_data.get("treatment_method"),
    "co2e_kg": float(emissions)
    }

