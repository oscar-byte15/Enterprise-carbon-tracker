
"""
Hometask 2 - Subsystem 2 Automated Tests

Tests:
- Abstract Base Classes
- Inheritance and Polymorphism
- Operator Overloading
- Iterators and Generators
- Carbon emission calculations
"""

from datetime import date

import pytest

from app.activities.subsystem2_homeassignment2 import (
    StreamProcessor,
    ScopeFilter,
    EmissionTransformer,
    ProcessingPipeline,
    EventStream,
)


def make_event(
    scope="Scope 2",
    amount=100,
    category="electricity",
    activity_type="Grid electricity",
    unit="kWh",
):
    return {
        "scope": scope,
        "category": category,
        "activity_type": activity_type,
        "amount": amount,
        "unit": unit,
        "date": date(2026, 11, 6),
        "enterprise_id": "enterprise-1",
    }


def test_abstract_class_cannot_be_instantiated():
    with pytest.raises(TypeError):
        StreamProcessor()


def test_scope_filter_inheritance():
    processor = ScopeFilter({"Scope 2"})

    assert isinstance(processor, StreamProcessor)


def test_scope_filter_accepts_matching_event():
    processor = ScopeFilter({"Scope 2"})
    event = make_event()

    result = processor.process(event)

    assert result == event
    assert result is not event


def test_scope_filter_rejects_other_scopes():
    processor = ScopeFilter({"Scope 2"})
    event = make_event(scope="Scope 1")

    assert processor.process(event) is None


def test_scope_filter_rejects_invalid_configuration():
    with pytest.raises(ValueError):
        ScopeFilter({"Scope 4"})


def test_scope_filter_rejects_empty_configuration():
    with pytest.raises(ValueError):
        ScopeFilter(set())


def test_scope_filter_accepts_multiple_scopes():
    processor = ScopeFilter({"Scope 1", "Scope 2"})

    assert processor.process(
        make_event(scope="Scope 1")
    ) is not None


def test_emission_transformer_inheritance():
    transformer = EmissionTransformer()

    assert isinstance(transformer, StreamProcessor)


def test_emission_transformer_calculates_tons():
    transformer = EmissionTransformer()

    result = transformer.process(make_event())

    assert result["co2e_kg"] == 35.2
    assert result["co2e_tons"] == 0.0352


def test_emission_transformer_rejects_invalid_unit():
    transformer = EmissionTransformer()

    with pytest.raises(ValueError):
        transformer.process(make_event(unit="L"))


def test_operator_overloading_creates_pipeline():
    pipeline = (
        ScopeFilter({"Scope 2"})
        | EmissionTransformer()
    )

    assert isinstance(pipeline, ProcessingPipeline)


def test_pipeline_filters_and_transforms():
    pipeline = (
        ScopeFilter({"Scope 2"})
        | EmissionTransformer()
    )

    events = [
        make_event(scope="Scope 2"),
        make_event(scope="Scope 1"),
        make_event(scope="Scope 2", amount=200),
    ]

    results = list(
        pipeline.run(EventStream(events))
    )

    assert len(results) == 2
    assert results[0]["co2e_tons"] == 0.0352
    assert results[1]["co2e_tons"] == 0.0704


def test_pipeline_supports_chaining():
    pipeline = (
        ScopeFilter({"Scope 1", "Scope 2"})
        | ScopeFilter({"Scope 2"})
        | EmissionTransformer()
    )

    assert isinstance(pipeline, ProcessingPipeline)

    result = pipeline.process(make_event())

    assert result["co2e_tons"] == 0.0352


def test_event_stream_is_iterator():
    stream = EventStream([
        make_event(),
        make_event(amount=200),
    ])

    assert iter(stream) is stream
    assert next(stream)["amount"] == 100
    assert next(stream)["amount"] == 200

    with pytest.raises(StopIteration):
        next(stream)


def test_pipeline_generator_is_lazy():
    pipeline = (
        ScopeFilter({"Scope 2"})
        | EmissionTransformer()
    )

    events = EventStream([make_event()])

    generator = pipeline.run(events)

    assert hasattr(generator, "__next__")

    result = next(generator)

    assert result["co2e_tons"] == 0.0352

    with pytest.raises(StopIteration):
        next(generator)


def test_original_event_is_not_modified():
    event = make_event()
    original = event.copy()

    result = EmissionTransformer().process(event)

    assert event == original
    assert "co2e_tons" not in event
    assert "co2e_tons" in result


# ==========================================
# HOMETASK 2 - SCOPE 1, 2 AND 3 TESTS
# ==========================================

@pytest.mark.parametrize(
    "scope,category,activity_type,amount,unit,expected_kg",
    [
        ("Scope 1", "transport", "Diesel", 50, "L", 128.54),
        ("Scope 2", "electricity", "Grid electricity", 100, "kWh", 35.20),
        ("Scope 3", "waste", "Plastic - Recycling", 100, "kg", 0.47),
    ],
)
def test_all_three_scopes_are_processed(
    scope, category, activity_type, amount, unit, expected_kg
):
    event = make_event(
        scope=scope,
        category=category,
        activity_type=activity_type,
        amount=amount,
        unit=unit,
    )

    pipeline = (
        ScopeFilter({scope})
        | EmissionTransformer()
    )

    results = list(pipeline.run(EventStream([event])))

    assert len(results) == 1
    assert results[0]["scope"] == scope
    assert results[0]["co2e_kg"] == pytest.approx(
        expected_kg, abs=0.01
    )
    assert results[0]["co2e_tons"] == pytest.approx(
        expected_kg / 1000, abs=0.00001
    )


def test_scope_2_filter_discards_scopes_1_and_3():
    events = [
        make_event(
            scope="Scope 1",
            category="transport",
            activity_type="Diesel",
            amount=50,
            unit="L",
        ),
        make_event(
            scope="Scope 2",
            category="electricity",
            activity_type="Grid electricity",
            amount=100,
            unit="kWh",
        ),
        make_event(
            scope="Scope 3",
            category="waste",
            activity_type="Plastic - Recycling",
            amount=100,
            unit="kg",
        ),
    ]

    pipeline = (
        ScopeFilter({"Scope 2"})
        | EmissionTransformer()
    )

    results = list(pipeline.run(EventStream(events)))

    assert len(results) == 1
    assert results[0]["scope"] == "Scope 2"
    assert results[0]["co2e_tons"] == 0.0352


def test_pipeline_accepts_all_scopes():
    events = [
        make_event(
            scope="Scope 1",
            category="transport",
            activity_type="Diesel",
            amount=50,
            unit="L",
        ),
        make_event(
            scope="Scope 2",
            category="electricity",
            activity_type="Grid electricity",
            amount=100,
            unit="kWh",
        ),
        make_event(
            scope="Scope 3",
            category="waste",
            activity_type="Plastic - Recycling",
            amount=100,
            unit="kg",
        ),
    ]

    pipeline = (
        ScopeFilter({"Scope 1", "Scope 2", "Scope 3"})
        | EmissionTransformer()
    )

    results = list(pipeline.run(EventStream(events)))

    assert len(results) == 3
    assert [r["scope"] for r in results] == [
        "Scope 1",
        "Scope 2",
        "Scope 3",
    ]
    assert all("co2e_tons" in r for r in results)
