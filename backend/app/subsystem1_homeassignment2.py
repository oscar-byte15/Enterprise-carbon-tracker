"""
Hometask 2 - Real-Time Event Processing
Subsystem 1: Authentication & Enterprise Management

OOP concepts:
1. Abstract Base Classes
2. Inheritance and Polymorphism
3. Operator Overloading
4. Iterators and Generators
"""

from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from typing import ClassVar


class StreamProcessor(ABC):
    """Base abstract class for enterprise management stream processors."""

    @abstractmethod
    def process(self, event: dict) -> dict | None:
        """Process a single event or filter it out."""
        return None

    def __or__(self, other):
        """Compose processors using the | operator."""
        if not isinstance(other, StreamProcessor):
            return NotImplemented

        return ProcessingPipeline([self, other])

    def run(self, stream: Iterable[dict]) -> Iterator[dict]:
        """Lazily process events using a generator."""
        for event in stream:
            result = self.process(event)
            if result is not None:
                yield result


class EventTypeFilter(StreamProcessor):
    """Keep only enterprise events that match a configured type."""

    VALID_TYPES: ClassVar[set[str]] = {
        "user_registration",
        "enterprise_created",
        "enterprise_update",
        "department_created",
        "department_updated",
    }

    def __init__(self, allowed_types: set[str] | list[str]):
        types = set(allowed_types)

        if not types:
            raise ValueError("At least one event type is required")

        invalid = types - self.VALID_TYPES
        if invalid:
            raise ValueError(f"Unsupported event type(s): {sorted(invalid)}")

        self._allowed_types = types

    def process(self, event: dict) -> dict | None:
        """Keep only matching enterprise-management events."""
        if not isinstance(event, dict):
            raise TypeError("Event must be a dictionary")

        if event.get("event_type") in self._allowed_types:
            return event.copy()

        return None


class EnterpriseEventTransformer(StreamProcessor):
    """Convert raw enterprise events into an audit-friendly structure."""

    def process(self, event: dict) -> dict:
        """Enrich an event with normalized metadata and a summary."""
        if not isinstance(event, dict):
            raise TypeError("Event must be a dictionary")

        event_type = event.get("event_type")
        if not event_type:
            raise ValueError("Event is missing 'event_type'")

        normalized = event.copy()
        normalized["status"] = "processed"
        normalized["normalized_event_type"] = event_type.replace("_", " ").title()

        if event_type == "user_registration":
            email = event.get("user_email", "unknown@example.com")
            enterprise_id = event.get("enterprise_id", "unknown")
            normalized["audit_summary"] = (
                f"User {email} registered for enterprise {enterprise_id}."
            )
        elif event_type == "enterprise_created":
            company_name = event.get("company_name", "Unknown company")
            normalized["audit_summary"] = (
                f"Enterprise {company_name} was created."
            )
        elif event_type == "enterprise_update":
            company_name = event.get("company_name", "Unknown company")
            normalized["audit_summary"] = (
                f"Enterprise {company_name} profile was updated."
            )
        elif event_type == "department_created":
            department_name = event.get("department_name", "Unknown department")
            normalized["audit_summary"] = (
                f"Department {department_name} was created."
            )
        elif event_type == "department_updated":
            department_name = event.get("department_name", "Unknown department")
            normalized["audit_summary"] = (
                f"Department {department_name} was updated."
            )
        else:
            normalized["audit_summary"] = f"Event {event_type} processed."

        return normalized


class ProcessingPipeline(StreamProcessor):
    """A sequence of processors that transforms events step by step."""

    def __init__(self, processors: list[StreamProcessor]):
        if not processors:
            raise ValueError("Pipeline requires at least one processor")

        if not all(isinstance(p, StreamProcessor) for p in processors):
            raise TypeError("All processors must inherit StreamProcessor")

        self._processors = list(processors)

    def get_processors(self) -> list[StreamProcessor]:
        return list(self._processors)

    def __or__(self, other):
        """Append a processor using the | operator."""
        if not isinstance(other, StreamProcessor):
            return NotImplemented

        if isinstance(other, ProcessingPipeline):
            return ProcessingPipeline(self._processors + other._processors)

        return ProcessingPipeline(self._processors + [other])

    def process(self, event: dict) -> dict | None:
        """Pass one event through all processors in sequence."""
        result = event

        for processor in self._processors:
            if result is None:
                return None
            result = processor.process(result)

        return result


class EventStream:
    """An iterator that yields enterprise events one at a time."""

    def __init__(self, events: Iterable[dict]):
        self._events = iter(events)

    def __iter__(self):
        return self

    def __next__(self) -> dict:
        return next(self._events)
