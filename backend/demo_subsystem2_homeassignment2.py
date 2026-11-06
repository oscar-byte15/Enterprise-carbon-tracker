
"""
Hometask 2 - Real-Time Data Processing
Subsystem 2: Carbon Activity Management & Calculation Engine

Demonstrates:
1. Scope-based event filtering
2. Carbon emission transformation
3. Operator overloading with |
4. Iterators and generators
"""

from datetime import date

from app.activities.subsystem2_homeassignment2 import (
    EventStream,
    ScopeFilter,
    EmissionTransformer,
    ProcessingPipeline,
)


def create_sample_events():
    """Simulate incoming operational carbon activities."""
    return [
        {
            "scope": "Scope 1",
            "category": "transport",
            "activity_type": "Diesel",
            "amount": 50,
            "unit": "L",
            "date": date(2026, 11, 6),
            "enterprise_id": "enterprise-demo",
        },
        {
            "scope": "Scope 2",
            "category": "electricity",
            "activity_type": "Grid electricity",
            "amount": 100,
            "unit": "kWh",
            "date": date(2026, 11, 6),
            "enterprise_id": "enterprise-demo",
        },
        {
            "scope": "Scope 3",
            "category": "waste",
            "activity_type": "Plastic - Recycling",
            "amount": 100,
            "unit": "kg",
            "date": date(2026, 11, 6),
            "enterprise_id": "enterprise-demo",
        },
    ]


def demonstrate_pipeline(allowed_scopes):
    """Execute the streaming pipeline for selected scopes."""

    print("\n" + "=" * 65)
    print("HOMETASK 2 - CARBON ACTIVITY STREAMING")
    print(f"Allowed scopes: {', '.join(sorted(allowed_scopes))}")
    print("=" * 65)

    events = create_sample_events()

    # Abstract class, inheritance and polymorphism
    scope_filter = ScopeFilter(allowed_scopes)
    transformer = EmissionTransformer()

    # Operator overloading: __or__()
    pipeline = scope_filter | transformer

    print(f"\nPipeline created: {type(pipeline).__name__}")
    print(f"Is ProcessingPipeline: {isinstance(pipeline, ProcessingPipeline)}")

    # Iterator: __iter__() and __next__()
    stream = EventStream(events)

    # Generator: ProcessingPipeline.run() uses yield
    results = pipeline.run(stream)

    print(f"\nGenerator: {type(results).__name__}")
    print("\nProcessed events:")

    processed_count = 0

    for event in results:
        processed_count += 1

        print(
            f"\n  Scope: {event['scope']}"
            f"\n  Activity: {event['activity_type']}"
            f"\n  Amount: {event['amount']} {event['unit']}"
            f"\n  Emissions: {event['co2e_kg']} kg CO2e"
            f"\n  Metric tons: {event['co2e_tons']} t CO2e"
        )

    print(f"\nTotal incoming events: {len(events)}")
    print(f"Total processed events: {processed_count}")
    print(f"Total filtered events: {len(events) - processed_count}")


def main():
    # Scenario 1: Accept only Scope 2 activities
    demonstrate_pipeline({"Scope 2"})

    # Scenario 2: Accept all three scopes
    demonstrate_pipeline({"Scope 1", "Scope 2", "Scope 3"})


if __name__ == "__main__":
    main()
