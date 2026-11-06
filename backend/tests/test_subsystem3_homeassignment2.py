"""
Hometask 2 - Subsystem 3 Automated Tests

Tests:
- Abstract Base Classes
- Inheritance and Polymorphism
- Operator Overloading (__or__, __add__)
- Iterators and Generators (__iter__, __next__, yield)
- Telemetry processing:
  * Scope filtering (Scope 1, Scope 2, Scope 3)
  * Business flight bookings (Scope 3)
  * Data center server utility logs (Scope 2)
  * Freight logistics payloads (Scope 1 / Scope 3)
"""

from datetime import date
from decimal import Decimal
import pytest

from app.analytics.subsystem3_homeassignment2 import (
    StreamProcessor,
    ScopeFilter,
    FlightTelemetryProcessor,
    DataCenterTelemetryProcessor,
    FreightTelemetryProcessor,
    ProcessingPipeline,
    TelemetryStream,
)


def make_flight_event(
    scope="Scope 3",
    distance_km=1000,
    passengers=1,
    cabin_class="economy",
    flight_type="short_haul",
):
    return {
        "telemetry_type": "flight",
        "scope": scope,
        "flight_number": "LH-402",
        "distance_km": distance_km,
        "passengers": passengers,
        "cabin_class": cabin_class,
        "flight_type": flight_type,
        "timestamp": "2026-11-06T10:00:00Z",
        "enterprise_id": "ent-alpha",
    }


def make_datacenter_event(
    scope="Scope 2",
    energy_kwh=5000,
    pue=1.2,
    grid_factor=0.352,
    server_load=1.0,
):
    return {
        "telemetry_type": "datacenter",
        "scope": scope,
        "facility_id": "dc-frankfurt-1",
        "energy_kwh": energy_kwh,
        "pue": pue,
        "grid_factor": grid_factor,
        "server_load": server_load,
        "timestamp": "2026-11-06T11:00:00Z",
        "enterprise_id": "ent-alpha",
    }


def make_freight_event(
    scope="Scope 3",
    cargo_weight_tons=20,
    distance_km=350,
    transport_mode="road",
):
    return {
        "telemetry_type": "freight",
        "scope": scope,
        "shipment_id": "FR-9821",
        "cargo_weight_tons": cargo_weight_tons,
        "distance_km": distance_km,
        "transport_mode": transport_mode,
        "timestamp": "2026-11-06T12:00:00Z",
        "enterprise_id": "ent-alpha",
    }


# =========================================================================
# 1. Abstract Base Class & Inheritance
# =========================================================================

def test_stream_processor_cannot_be_instantiated():
    """Verify StreamProcessor is an abstract class requiring implementation."""
    with pytest.raises(TypeError):
        StreamProcessor()


def test_processors_inherit_from_stream_processor():
    """Verify all specialized processors inherit from StreamProcessor."""
    assert isinstance(ScopeFilter({"Scope 1"}), StreamProcessor)
    assert isinstance(FlightTelemetryProcessor(), StreamProcessor)
    assert isinstance(DataCenterTelemetryProcessor(), StreamProcessor)
    assert isinstance(FreightTelemetryProcessor(), StreamProcessor)
    assert isinstance(ProcessingPipeline([FlightTelemetryProcessor()]), StreamProcessor)


# =========================================================================
# 2. ScopeFilter Unit Tests
# =========================================================================

def test_scope_filter_accepts_matching_event():
    filter_proc = ScopeFilter({"Scope 3"})
    event = make_flight_event(scope="Scope 3")
    result = filter_proc.process(event)

    assert result == event
    assert result is not event  # Defensive copy


def test_scope_filter_discards_non_matching_scope():
    filter_proc = ScopeFilter({"Scope 2"})
    event = make_flight_event(scope="Scope 3")
    assert filter_proc.process(event) is None


def test_scope_filter_accepts_multiple_scopes():
    filter_proc = ScopeFilter({"Scope 1", "Scope 3"})
    assert filter_proc.process(make_freight_event(scope="Scope 1")) is not None
    assert filter_proc.process(make_flight_event(scope="Scope 3")) is not None
    assert filter_proc.process(make_datacenter_event(scope="Scope 2")) is None


def test_scope_filter_validates_scopes():
    with pytest.raises(ValueError, match="At least one scope is required"):
        ScopeFilter(set())

    with pytest.raises(ValueError, match="Invalid carbon emission scope"):
        ScopeFilter({"Scope 4"})


# =========================================================================
# 3. Flight Telemetry Processor Tests
# =========================================================================

def test_flight_telemetry_calculation():
    processor = FlightTelemetryProcessor()
    # 1000 km, 1 passenger, short-haul (0.15353 kg/pkm), economy (1.0)
    event = make_flight_event(distance_km=1000, passengers=1, cabin_class="economy", flight_type="short_haul")
    result = processor.process(event)

    expected_kg = 153.53
    expected_tons = 0.15353
    assert result["co2e_kg"] == expected_kg
    assert result["co2e_tons"] == expected_tons
    assert result["passenger_km"] == 1000.0


def test_flight_telemetry_cabin_multipliers():
    processor = FlightTelemetryProcessor()
    # Business class multiplier = 2.5
    event = make_flight_event(distance_km=1000, passengers=1, cabin_class="business", flight_type="short_haul")
    result = processor.process(event)

    assert result["co2e_kg"] == pytest.approx(153.53 * 2.5, abs=0.02)
    assert result["co2e_tons"] == pytest.approx((153.53 * 2.5) / 1000, abs=0.00001)


def test_flight_telemetry_validation():
    processor = FlightTelemetryProcessor()
    with pytest.raises(ValueError, match="missing 'distance_km'"):
        processor.process({"telemetry_type": "flight"})

    with pytest.raises(ValueError, match="Flight distance must be a positive"):
        processor.process(make_flight_event(distance_km=-100))

    with pytest.raises(ValueError, match="Passengers must be a positive integer"):
        processor.process(make_flight_event(passengers=0))

    with pytest.raises(ValueError, match="Unknown cabin class"):
        processor.process(make_flight_event(cabin_class="ultra_luxury"))


# =========================================================================
# 4. Data Center Telemetry Processor Tests
# =========================================================================

def test_datacenter_telemetry_calculation():
    processor = DataCenterTelemetryProcessor()
    # 10000 kWh, PUE 1.20, grid factor 0.352 kg/kWh, load 1.0
    # effective kWh = 12000 kWh -> 12000 * 0.352 = 4224.0 kg -> 4.224 tCO2e
    event = make_datacenter_event(energy_kwh=10000, pue=1.2, grid_factor=0.352)
    result = processor.process(event)

    assert result["effective_kwh"] == 12000.0
    assert result["co2e_kg"] == 4224.0
    assert result["co2e_tons"] == 4.224


def test_datacenter_telemetry_validation():
    processor = DataCenterTelemetryProcessor()
    with pytest.raises(ValueError, match="missing 'energy_kwh'"):
        processor.process({"telemetry_type": "datacenter"})

    with pytest.raises(ValueError, match="Energy consumption must be a positive"):
        processor.process(make_datacenter_event(energy_kwh=-50))

    with pytest.raises(ValueError, match="PUE must be greater than or equal to 1.0"):
        processor.process(make_datacenter_event(pue=0.9))

    with pytest.raises(ValueError, match="Grid factor cannot be negative"):
        processor.process(make_datacenter_event(grid_factor=-0.1))


# =========================================================================
# 5. Freight Telemetry Processor Tests
# =========================================================================

def test_freight_telemetry_calculation():
    processor = FreightTelemetryProcessor()
    # Road factor = 0.105 kg/tkm. 20 tons * 100 km = 2000 tkm -> 2000 * 0.105 = 210.0 kg -> 0.21 tCO2e
    event = make_freight_event(cargo_weight_tons=20, distance_km=100, transport_mode="road")
    result = processor.process(event)

    assert result["tonne_km"] == 2000.0
    assert result["co2e_kg"] == 210.0
    assert result["co2e_tons"] == 0.21


def test_freight_telemetry_modalities():
    processor = FreightTelemetryProcessor()
    # Rail factor = 0.028 kg/tkm
    rail_res = processor.process(make_freight_event(cargo_weight_tons=10, distance_km=500, transport_mode="rail"))
    assert rail_res["co2e_kg"] == 140.0
    assert rail_res["co2e_tons"] == 0.14


def test_freight_telemetry_validation():
    processor = FreightTelemetryProcessor()
    with pytest.raises(ValueError, match="missing 'cargo_weight_tons'"):
        processor.process({"telemetry_type": "freight", "distance_km": 100})

    with pytest.raises(ValueError, match="Cargo weight must be a positive"):
        processor.process(make_freight_event(cargo_weight_tons=-10))

    with pytest.raises(ValueError, match="Unknown transport mode"):
        processor.process(make_freight_event(transport_mode="rocket"))


# =========================================================================
# 6. Operator Overloading & Pipeline Chaining
# =========================================================================

def test_operator_overloading_pipe():
    filter_proc = ScopeFilter({"Scope 3"})
    flight_proc = FlightTelemetryProcessor()

    pipeline = filter_proc | flight_proc
    assert isinstance(pipeline, ProcessingPipeline)
    assert len(pipeline.get_processors()) == 2


def test_operator_overloading_add():
    filter_proc = ScopeFilter({"Scope 2"})
    dc_proc = DataCenterTelemetryProcessor()

    pipeline = filter_proc + dc_proc
    assert isinstance(pipeline, ProcessingPipeline)
    assert len(pipeline.get_processors()) == 2


def test_multi_stage_pipeline_composition():
    # Demonstrating chain of 4 processors: ScopeFilter | Flight | DataCenter | Freight
    pipeline = (
        ScopeFilter({"Scope 2", "Scope 3"})
        | FlightTelemetryProcessor()
        | DataCenterTelemetryProcessor()
        | FreightTelemetryProcessor()
    )

    assert isinstance(pipeline, ProcessingPipeline)
    assert len(pipeline.get_processors()) == 4

    flight_res = pipeline.process(make_flight_event(scope="Scope 3", distance_km=1000))
    assert flight_res is not None
    assert "co2e_tons" in flight_res

    dc_res = pipeline.process(make_datacenter_event(scope="Scope 2", energy_kwh=1000))
    assert dc_res is not None
    assert "co2e_tons" in dc_res

    scope1_res = pipeline.process(make_freight_event(scope="Scope 1"))
    assert scope1_res is None


# =========================================================================
# 7. Iterators & Generators
# =========================================================================

def test_telemetry_stream_iterator():
    events = [
        make_flight_event(distance_km=500),
        make_datacenter_event(energy_kwh=2000),
    ]
    stream = TelemetryStream(events)

    assert iter(stream) is stream
    item1 = next(stream)
    assert item1["telemetry_type"] == "flight"
    item2 = next(stream)
    assert item2["telemetry_type"] == "datacenter"

    with pytest.raises(StopIteration):
        next(stream)


def test_pipeline_generator_lazy_evaluation():
    pipeline = ScopeFilter({"Scope 3"}) | FlightTelemetryProcessor()

    raw_events = [
        make_flight_event(scope="Scope 3", distance_km=1000),
        make_datacenter_event(scope="Scope 2", energy_kwh=5000),  # Filtered out
        make_flight_event(scope="Scope 3", distance_km=2000),
    ]

    stream = TelemetryStream(raw_events)
    gen = pipeline.run(stream)

    assert hasattr(gen, "__iter__")
    assert hasattr(gen, "__next__")

    results = list(gen)
    assert len(results) == 2
    assert results[0]["distance_km"] == 1000
    assert results[1]["distance_km"] == 2000


def test_event_immutability():
    """Verify original incoming event is not modified in-place."""
    original = make_flight_event(distance_km=1000)
    copy_backup = dict(original)

    processor = FlightTelemetryProcessor()
    res = processor.process(original)

    assert original == copy_backup
    assert "co2e_tons" not in original
    assert "co2e_tons" in res

