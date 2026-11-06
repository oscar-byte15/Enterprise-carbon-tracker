
"""
Hometask 2 - Real-Time Data Processing
Subsystem 2: Carbon Activity Management & Calculation Engine

OOP concepts:
1. Abstract Base Classes
2. Inheritance and Polymorphism
3. Operator Overloading
4. Iterators and Generators
"""

from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from .oop import ActivityRecord, CalculationService


class StreamProcessor(ABC):
    """Base abstract class for stream processors."""

    @abstractmethod
    def process(self, event: dict) -> dict | None:
        """Process an event or filter it out."""
        pass

    def __or__(self, other):
        """Compose processors using the | operator."""
        if not isinstance(other, StreamProcessor):
            return NotImplemented

        return ProcessingPipeline([self, other])


class ScopeFilter(StreamProcessor):
    """Filter activity events by GHG Protocol scope."""

    VALID_SCOPES = {"Scope 1", "Scope 2", "Scope 3"}

    def __init__(self, allowed_scopes: set[str]):
        scopes = set(allowed_scopes)

        if not scopes:
            raise ValueError(
                "At least one scope is required"
            )

        if not scopes.issubset(self.VALID_SCOPES):
            raise ValueError(
                "Invalid carbon emission scope"
            )

        self._allowed_scopes = scopes

    def process(self, event: dict) -> dict | None:
        """Keep only matching scope events."""
        if event.get("scope") in self._allowed_scopes:
            return event.copy()

        return None


class EmissionTransformer(StreamProcessor):
    """Convert activity metrics into metric tons of CO2e."""

    def __init__(self, calculation_service=None):
        if calculation_service is None:
            calculation_service = CalculationService()

        self._calculation_service = calculation_service

    def process(self, event: dict) -> dict:
        """Calculate emissions using the existing OOP engine."""
        activity_date = event.get("date")

        if isinstance(activity_date, str):
            activity_date = date.fromisoformat(
                activity_date
            )

        activity = ActivityRecord(
            category=event["category"],
            activity_type=event["activity_type"],
            amount=event["amount"],
            unit=event["unit"],
            activity_date=activity_date,
            enterprise_id=event["enterprise_id"],
        )

        result = self._calculation_service.calculate(
            activity
        )

        tons = (
            Decimal(str(result["co2e_kg"]))
            / Decimal("1000")
        ).quantize(
            Decimal("0.000001"),
            rounding=ROUND_HALF_UP
        )

        return {
            **event,
            **result,
            "co2e_tons": float(tons),
        }


class ProcessingPipeline(StreamProcessor):
    """A composable sequence of stream processors."""

    def __init__(self, processors: list[StreamProcessor]):
        if not processors:
            raise ValueError(
                "Pipeline requires at least one processor"
            )

        if not all(
            isinstance(p, StreamProcessor)
            for p in processors
        ):
            raise TypeError(
                "All processors must inherit StreamProcessor"
            )

        self._processors = list(processors)

    def __or__(self, other):
        """Append a processor using the | operator."""
        if not isinstance(other, StreamProcessor):
            return NotImplemented

        if isinstance(other, ProcessingPipeline):
            return ProcessingPipeline(
                self._processors + other._processors
            )

        return ProcessingPipeline(
            self._processors + [other]
        )

    def process(self, event: dict) -> dict | None:
        """Pass one event through all processors."""
        result = event

        for processor in self._processors:
            if result is None:
                return None

            result = processor.process(result)

        return result

    def run(self, stream):
        """Lazily process events using a generator."""
        for event in stream:
            result = self.process(event)

            if result is not None:
                yield result


class EventStream:
    """An iterator that consumes activity events."""

    def __init__(self, events):
        self._events = iter(events)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self._events)
