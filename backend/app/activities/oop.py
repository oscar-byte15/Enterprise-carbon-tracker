"""Hometask 1: OOP implementation of Subsystem 2.

Domain objects used by the FastAPI activity create/update pipeline.
The existing API response fields and MongoDB repository are preserved.
"""
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from .calculator import load_emission_factors


class ActivityRecord:
    """A measured enterprise activity (not a MongoDB document)."""

    def __init__(self, category: str, activity_type: str, amount: float,
                 unit: str, activity_date: date, enterprise_id: str):
        self.set_category(category)
        self.set_activity_type(activity_type)
        self.set_amount(amount)
        self.set_unit(unit)
        self.set_date(activity_date)
        self.set_enterprise_id(enterprise_id)

    def get_category(self):
        return self._category

    def set_category(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Category is required")
        self._category = value

    def get_activity_type(self):
        return self._activity_type

    def set_activity_type(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Activity type is required")
        self._activity_type = value

    def get_amount(self):
        return float(self._amount)

    def set_amount(self, value):
        try:
            amount = Decimal(str(value))
        except Exception as exc:
            raise ValueError("Amount must be numeric") from exc
        if not amount.is_finite() or amount <= 0:
            raise ValueError("Amount must be a positive finite number")
        self._amount = amount

    def get_unit(self):
        return self._unit

    def set_unit(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Unit is required")
        self._unit = value

    def get_date(self):
        return self._date

    def set_date(self, value):
        if not isinstance(value, date):
            raise ValueError("Date must be a date object")
        self._date = value

    def get_enterprise_id(self):
        return self._enterprise_id

    def set_enterprise_id(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Enterprise ID is required")
        self._enterprise_id = value

    def get_period(self):
        return self._date.strftime("%Y-%m")


class EmissionFactor:
    """Factor configuration for one category and activity type."""

    def __init__(self, category: str, activity_type: str, factor: float,
                 unit: str, source: str):
        self.set_category(category)
        self.set_activity_type(activity_type)
        self.set_factor(factor)
        self.set_unit(unit)
        self.set_source(source)

    def get_category(self):
        return self._category

    def set_category(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Category is required")
        self._category = value

    def get_activity_type(self):
        return self._activity_type

    def set_activity_type(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Activity type is required")
        self._activity_type = value

    def get_factor(self):
        return float(self._factor)

    def set_factor(self, value):
        try:
            factor = Decimal(str(value))
        except Exception as exc:
            raise ValueError("Factor must be numeric") from exc
        if not factor.is_finite() or factor < 0:
            raise ValueError("Factor must be finite and non-negative")
        self._factor = factor

    def get_unit(self):
        return self._unit

    def set_unit(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Unit is required")
        self._unit = value

    def get_source(self):
        return self._source

    def set_source(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Source is required")
        self._source = value

    def matches(self, activity: ActivityRecord) -> bool:
        return (self._category == activity.get_category()
                and self._activity_type == activity.get_activity_type()
                and self._unit == activity.get_unit())


class CalculationService:
    """Loads/configures factors and calculates CO2e using domain objects."""

    def __init__(self, factor_catalog=None):
        self.set_factor_catalog(factor_catalog)

    def initialize_factors(self):
        """Reload current factors from the production JSON configuration."""
        self.set_factor_catalog(load_emission_factors())

    def get_factor_catalog(self):
        return {category: {name: dict(data) for name, data in types.items()}
                for category, types in self._factor_catalog.items()}

    def set_factor_catalog(self, catalog):
        if catalog is None:
            self.initialize_factors()
        elif not isinstance(catalog, dict):
            raise ValueError("Factor catalog must be a dictionary")
        else:
            self._factor_catalog = {
                category: {name: dict(data) for name, data in types.items()}
                for category, types in catalog.items()
            }
            # Composition: this service creates and owns its factor objects.
            self._factors = {
                (category, name): EmissionFactor(
                    category, name, data["factor"], data["unit"], data["source"]
                )
                for category, types in self._factor_catalog.items()
                for name, data in types.items()
            }

    def get_emission_factor(self, category, activity_type):
        category_factors = self._factor_catalog.get(category)
        if category_factors is None:
            raise ValueError(f"Unknown category: {category}")
        data = category_factors.get(activity_type)
        if data is None:
            raise ValueError(f"Unknown activity type: {activity_type}")
        return self._factors[(category, activity_type)]

    def validate_units(self, activity: ActivityRecord, factor: EmissionFactor):
        if not factor.matches(activity):
            raise ValueError("Activity category, type or unit does not match emission factor")

    def calculate(self, activity: ActivityRecord):
        factor = self.get_emission_factor(activity.get_category(),
                                          activity.get_activity_type())
        self.validate_units(activity, factor)
        amount = activity._amount  # Decimal retained to avoid float precision loss
        result = (amount * factor._factor).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        factor_data = self._factor_catalog[activity.get_category()][activity.get_activity_type()]
        return {
            "co2e_kg": float(result),
            "emission_factor": factor.get_factor(),
            "factor_source": factor.get_source(),
            "factor_source_url": factor_data.get("source_url"),
            "factor_year": factor_data.get("year"),
            "factor_region": factor_data.get("region"),
            "factor_methodology": factor_data.get("methodology"),
            "treatment_method": factor_data.get("treatment_method"),
            "period": activity.get_period(),
        }
