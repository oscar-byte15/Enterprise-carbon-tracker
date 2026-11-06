"""
Hometask 2 - Real-Time Data Processing
Subsystem 3: Analytics Dashboard & AI Advisory

OOP concepts:
1. Abstract Base Classes (ABCs)
2. Inheritance and Polymorphism
3. Operator Overloading (__or__, __add__)
4. Iterators and Generators (__iter__, __next__, yield)

Operational telemetry streams:
- Flight bookings (Scope 3: Business Travel)
- Data center server utility logs (Scope 2: Purchased Electricity & Compute)
- Freight logistics payloads (Scope 1 / Scope 3: Transport Logistics)
"""

from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Iterable, Iterator


class StreamProcessor(ABC):
    """Base abstract class defining the contract for telemetry stream processors."""

    @abstractmethod
    def process(self, event: dict) -> dict | None:
        """Process an incoming telemetry event or filter it out (returning None)."""
        pass

    def __or__(self, other):
        """Compose processors using the | operator."""
        if not isinstance(other, StreamProcessor):
            return NotImplemented

        return ProcessingPipeline([self, other])

    def __add__(self, other):
        """Compose processors using the + operator."""
        if not isinstance(other, StreamProcessor):
            return NotImplemented

        return ProcessingPipeline([self, other])

    def run(self, stream: Iterable[dict]) -> Iterator[dict]:
        """Lazily process telemetry events using a generator."""
        for event in stream:
            result = self.process(event)
            if result is not None:
                yield result


class ScopeFilter(StreamProcessor):
    """Filter operational telemetry records by GHG Protocol scope tag."""

    VALID_SCOPES = {"Scope 1", "Scope 2", "Scope 3"}

    def __init__(self, allowed_scopes: set[str] | list[str]):
        scopes = set(allowed_scopes)

        if not scopes:
            raise ValueError("At least one scope is required")

        if not scopes.issubset(self.VALID_SCOPES):
            raise ValueError("Invalid carbon emission scope")

        self._allowed_scopes = scopes

    def get_allowed_scopes(self) -> set[str]:
        return set(self._allowed_scopes)

    def process(self, event: dict) -> dict | None:
        """Keep only events matching the configured scope tags."""
        if event.get("scope") in self._allowed_scopes:
            return event.copy()

        return None


class FlightTelemetryProcessor(StreamProcessor):
    """Transform business flight telemetry into metric tons of CO2e (Scope 3)."""

    # Base emission factors per passenger-kilometer (kg CO2e / pkm)
    BASE_FACTORS = {
        "domestic": Decimal("0.24587"),      # < 500 km
        "short_haul": Decimal("0.15353"),    # 500 - 3700 km
        "long_haul": Decimal("0.14787"),     # > 3700 km
    }

    # Cabin class weighting factors
    CABIN_MULTIPLIERS = {
        "economy": Decimal("1.0"),
        "premium_economy": Decimal("1.5"),
        "business": Decimal("2.5"),
        "first": Decimal("4.0"),
    }

    def process(self, event: dict) -> dict:
        """Calculate flight emissions in kg and metric tons of CO2e."""
        telemetry_type = event.get("telemetry_type")
        if telemetry_type is not None and telemetry_type != "flight":
            return event.copy()

        if "distance_km" not in event:
            raise ValueError("Flight event missing 'distance_km'")

        try:
            distance = Decimal(str(event["distance_km"]))
        except Exception as exc:
            raise ValueError("Flight distance must be numeric") from exc

        if not distance.is_finite() or distance <= 0:
            raise ValueError("Flight distance must be a positive finite number")

        passengers = event.get("passengers", 1)
        if not isinstance(passengers, int) or isinstance(passengers, bool) or passengers <= 0:
            raise ValueError("Passengers must be a positive integer")

        cabin = str(event.get("cabin_class", "economy")).lower().strip()
        if cabin not in self.CABIN_MULTIPLIERS:
            raise ValueError(f"Unknown cabin class: {cabin}")

        flight_type = event.get("flight_type")
        if flight_type:
            flight_type = str(flight_type).lower().strip()
            if flight_type not in self.BASE_FACTORS:
                raise ValueError(f"Unknown flight type: {flight_type}")
        else:
            if distance < 500:
                flight_type = "domestic"
            elif distance <= 3700:
                flight_type = "short_haul"
            else:
                flight_type = "long_haul"

        base_factor = self.BASE_FACTORS[flight_type]
        cabin_mult = self.CABIN_MULTIPLIERS[cabin]

        pkm = distance * Decimal(str(passengers))
        co2e_kg = (pkm * base_factor * cabin_mult).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        co2e_tons = (co2e_kg / Decimal("1000")).quantize(
            Decimal("0.000001"), rounding=ROUND_HALF_UP
        )

        return {
            **event,
            "flight_type": flight_type,
            "cabin_class": cabin,
            "passenger_km": float(pkm),
            "co2e_kg": float(co2e_kg),
            "co2e_tons": float(co2e_tons),
        }


class DataCenterTelemetryProcessor(StreamProcessor):
    """Transform server utility and power logs into metric tons of CO2e (Scope 2)."""

    DEFAULT_GRID_FACTOR = Decimal("0.352")  # kg CO2e / kWh (German grid benchmark)
    DEFAULT_PUE = Decimal("1.20")           # Power Usage Effectiveness benchmark

    def process(self, event: dict) -> dict:
        """Calculate data center electricity emissions in kg and metric tons."""
        telemetry_type = event.get("telemetry_type")
        if telemetry_type is not None and telemetry_type not in ("datacenter", "server"):
            return event.copy()

        if "energy_kwh" not in event:
            raise ValueError("Data center event missing 'energy_kwh'")

        try:
            kwh = Decimal(str(event["energy_kwh"]))
        except Exception as exc:
            raise ValueError("Energy consumption must be numeric") from exc

        if not kwh.is_finite() or kwh <= 0:
            raise ValueError("Energy consumption must be a positive finite number")

        pue_val = event.get("pue", self.DEFAULT_PUE)
        try:
            pue = Decimal(str(pue_val))
        except Exception as exc:
            raise ValueError("PUE must be numeric") from exc

        if not pue.is_finite() or pue < Decimal("1.0"):
            raise ValueError("PUE must be greater than or equal to 1.0")

        grid_val = event.get("grid_factor", self.DEFAULT_GRID_FACTOR)
        try:
            grid_factor = Decimal(str(grid_val))
        except Exception as exc:
            raise ValueError("Grid factor must be numeric") from exc

        if not grid_factor.is_finite() or grid_factor < 0:
            raise ValueError("Grid factor cannot be negative")

        load_val = event.get("server_load", 1.0)
        try:
            server_load = Decimal(str(load_val))
        except Exception as exc:
            raise ValueError("Server load must be numeric") from exc

        if not server_load.is_finite() or server_load <= 0:
            raise ValueError("Server load must be a positive factor")

        effective_kwh = (kwh * pue * server_load).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        co2e_kg = (effective_kwh * grid_factor).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        co2e_tons = (co2e_kg / Decimal("1000")).quantize(
            Decimal("0.000001"), rounding=ROUND_HALF_UP
        )

        return {
            **event,
            "effective_kwh": float(effective_kwh),
            "co2e_kg": float(co2e_kg),
            "co2e_tons": float(co2e_tons),
        }


class FreightTelemetryProcessor(StreamProcessor):
    """Transform logistics freight payloads into metric tons of CO2e (Scope 1 / Scope 3)."""

    # Emission factors in kg CO2e per tonne-kilometer (tkm)
    MODE_FACTORS = {
        "road": Decimal("0.105"),    # Heavy goods diesel truck
        "rail": Decimal("0.028"),    # Electric/diesel freight train
        "sea": Decimal("0.016"),     # Container cargo vessel
        "air": Decimal("0.602"),     # Air freight cargo
    }

    def process(self, event: dict) -> dict:
        """Calculate freight logistics emissions in kg and metric tons."""
        telemetry_type = event.get("telemetry_type")
        if telemetry_type is not None and telemetry_type not in ("freight", "logistics"):
            return event.copy()

        if "cargo_weight_tons" not in event:
            raise ValueError("Freight event missing 'cargo_weight_tons'")

        if "distance_km" not in event:
            raise ValueError("Freight event missing 'distance_km'")

        try:
            weight = Decimal(str(event["cargo_weight_tons"]))
        except Exception as exc:
            raise ValueError("Cargo weight must be numeric") from exc

        if not weight.is_finite() or weight <= 0:
            raise ValueError("Cargo weight must be a positive finite number")

        try:
            distance = Decimal(str(event["distance_km"]))
        except Exception as exc:
            raise ValueError("Freight distance must be numeric") from exc

        if not distance.is_finite() or distance <= 0:
            raise ValueError("Freight distance must be a positive finite number")

        mode = str(event.get("transport_mode", "road")).lower().strip()
        if mode not in self.MODE_FACTORS:
            raise ValueError(f"Unknown transport mode: {mode}")

        factor = self.MODE_FACTORS[mode]
        tonne_km = (weight * distance).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        co2e_kg = (tonne_km * factor).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        co2e_tons = (co2e_kg / Decimal("1000")).quantize(
            Decimal("0.000001"), rounding=ROUND_HALF_UP
        )

        return {
            **event,
            "transport_mode": mode,
            "tonne_km": float(tonne_km),
            "co2e_kg": float(co2e_kg),
            "co2e_tons": float(co2e_tons),
        }


class ProcessingPipeline(StreamProcessor):
    """A composable pipeline of sequential stream processors."""

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

    def __add__(self, other):
        """Append a processor using the + operator."""
        if not isinstance(other, StreamProcessor):
            return NotImplemented

        if isinstance(other, ProcessingPipeline):
            return ProcessingPipeline(self._processors + other._processors)

        return ProcessingPipeline(self._processors + [other])

    def process(self, event: dict) -> dict | None:
        """Pass one event sequentially through all processors."""
        result = event

        for processor in self._processors:
            if result is None:
                return None

            result = processor.process(result)

        return result


class TelemetryStream:
    """An iterator that consumes operational telemetry events one by one."""

    def __init__(self, events: Iterable[dict]):
        self._events = iter(events)

    def __iter__(self):
        return self

    def __next__(self) -> dict:
        return next(self._events)

