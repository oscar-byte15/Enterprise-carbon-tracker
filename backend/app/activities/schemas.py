
"""
Activity Schemas - Subsystem 2

NFR4:
    Validate carbon activities according to their
    category, type, and measurement unit.

The allowed activity combinations are loaded from
emission_factors.json to avoid duplicated definitions.
"""

from datetime import date
from math import isfinite
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from .calculator import load_emission_factors


class ActivityCreate(BaseModel):
    """
    Request schema for creating and updating activities.

    Business rules:
        - Category must be supported.
        - Amount must be positive and finite.
        - Activity type must belong to its category.
        - Unit must match the configured emission factor.
        - Date must be valid.
    """

    category: Literal[
        "electricity",
        "heating",
        "transport",
        "waste"
    ]

    type: str
    amount: float = Field(gt=0)
    unit: str
    date: date

    @model_validator(mode="after")
    def validate_activity_configuration(self):
        """
        Validate category-specific constraints using
        the configured emission factor catalog.
        """

        # Reject NaN and infinity.
        if not isfinite(self.amount):
            raise ValueError(
                "Amount must be a positive finite number"
            )

        factors = load_emission_factors()

        # Retrieve available types for the selected category.
        category_factors = factors.get(self.category)

        if category_factors is None:
            raise ValueError(
                f"Unknown category: {self.category}"
            )

        # Validate the selected activity type.
        factor_data = category_factors.get(self.type)

        if factor_data is None:
            raise ValueError(
                f"Invalid activity type '{self.type}' "
                f"for category '{self.category}'"
            )

        # Validate its measurement unit.
        expected_unit = factor_data["unit"]

        if self.unit != expected_unit:
            raise ValueError(
                f"Invalid unit for {self.category}: "
                f"expected {expected_unit}, got {self.unit}"
            )

        return self
