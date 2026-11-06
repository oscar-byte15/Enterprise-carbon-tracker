"""
Hometask 2 - Real-Time Data Processing
Subsystem 3: Analytics Dashboard & AI Advisory

Demonstrates:
1. Operational telemetry stream ingestion (Flight, Data Center, Freight)
2. GHG Protocol scope-based filtering (Scope 1, Scope 2, Scope 3)
3. Domain-specific emission transformation into metric tons (tCO2e)
4. Operator overloading with | and +
5. Stream consumption via TelemetryStream (Iterator) and pipeline.run() (Generator)
"""

from app.analytics.subsystem3_homeassignment2 import (
    TelemetryStream,
    ScopeFilter,
    FlightTelemetryProcessor,
    DataCenterTelemetryProcessor,
    FreightTelemetryProcessor,
    ProcessingPipeline,
)


def create_sample_telemetry_events():
    """Simulate real-time operational telemetry feeds."""
    return [
        {
            "telemetry_type": "flight",
            "scope": "Scope 3",
            "flight_number": "LH-402",
            "route": "FRA -> JFK",
            "distance_km": 6200,
            "passengers": 4,
            "cabin_class": "business",
            "flight_type": "long_haul",
            "enterprise_id": "enterprise-demo",
        },
        {
            "telemetry_type": "datacenter",
            "scope": "Scope 2",
            "facility_id": "dc-frankfurt-01",
            "energy_kwh": 25000,
            "pue": 1.25,
            "grid_factor": 0.352,
            "server_load": 0.90,
            "enterprise_id": "enterprise-demo",
        },
        {
            "telemetry_type": "freight",
            "scope": "Scope 1",
            "fleet_id": "truck-fleet-north",
            "cargo_weight_tons": 18,
            "distance_km": 420,
            "transport_mode": "road",
            "enterprise_id": "enterprise-demo",
        },
        {
            "telemetry_type": "freight",
            "scope": "Scope 3",
            "shipment_id": "cargo-rail-trans",
            "cargo_weight_tons": 120,
            "distance_km": 850,
            "transport_mode": "rail",
            "enterprise_id": "enterprise-demo",
        },
    ]


def demonstrate_telemetry_pipeline(allowed_scopes, description):
    """Execute the streaming telemetry pipeline for designated scopes."""

    print("\n" + "=" * 70)
    print("HOMETASK 2 - SUBSYSTEM 3 REAL-TIME TELEMETRY PIPELINE")
    print(f"Scenario: {description}")
    print(f"Allowed scopes: {', '.join(sorted(allowed_scopes))}")
    print("=" * 70)

    events = create_sample_telemetry_events()

    # 1. Scope filter
    scope_filter = ScopeFilter(allowed_scopes)

    # 2. Specialized telemetry processors (Inheritance & Polymorphism)
    flight_processor = FlightTelemetryProcessor()
    datacenter_processor = DataCenterTelemetryProcessor()
    freight_processor = FreightTelemetryProcessor()

    # 3. Operator overloading composition using | and +
    # (scope_filter | flight_processor) composed with (datacenter + freight)
    pipeline = (
        scope_filter
        | flight_processor
        | datacenter_processor
        + freight_processor
    )

    print(f"\nPipeline Type: {type(pipeline).__name__}")
    print(f"Stages Count: {len(pipeline.get_processors())}")
    print(f"Is StreamProcessor: {isinstance(pipeline, ProcessingPipeline)}")

    # 4. Iterator: TelemetryStream (__iter__ and __next__)
    stream = TelemetryStream(events)

    # 5. Generator: pipeline.run() uses yield for lazy stream processing
    results = pipeline.run(stream)

    print(f"\nGenerator Instance: {type(results).__name__}")
    print("\nProcessed Telemetry Events:")

    processed_count = 0
    total_co2e_tons = 0.0

    for event in results:
        processed_count += 1
        t_type = event.get("telemetry_type")
        co2e_tons = event.get("co2e_tons", 0.0)
        co2e_kg = event.get("co2e_kg", 0.0)
        total_co2e_tons += co2e_tons

        print(
            f"\n  [Event #{processed_count}]"
            f"\n  Type:       {t_type.upper()}"
            f"\n  Scope:      {event.get('scope')}"
            f"\n  Emissions:  {co2e_kg:,.2f} kg CO2e"
            f"\n  Metric:     {co2e_tons:,.6f} tCO2e"
        )

    print("-" * 70)
    print(f"Total incoming telemetry events: {len(events)}")
    print(f"Total processed events:          {processed_count}")
    print(f"Filtered out events:             {len(events) - processed_count}")
    print(f"Cumulative Emissions:            {total_co2e_tons:,.6f} tCO2e")


def main():
    # Scenario 1: Process only Scope 2 (Data Center server utilities)
    demonstrate_telemetry_pipeline(
        {"Scope 2"},
        "Scope 2 Clean Energy Compliance (Data Center Utilities)"
    )

    # Scenario 2: Process Scope 1 and Scope 3 (Logistics payloads & Business travel)
    demonstrate_telemetry_pipeline(
        {"Scope 1", "Scope 3"},
        "Scope 1 & 3 Operational Ingestion (Freight & Business Flights)"
    )

    # Scenario 3: Process all 3 scopes concurrently
    demonstrate_telemetry_pipeline(
        {"Scope 1", "Scope 2", "Scope 3"},
        "Enterprise Full-Scope Real-Time Telemetry Pipeline"
    )


if __name__ == "__main__":
    main()

