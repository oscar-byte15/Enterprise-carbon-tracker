"""Hometask 2 - Subsystem 1 Automated Tests"""

import pytest

from app.subsystem1_homeassignment2 import (
    EventStream,
    EventTypeFilter,
    EnterpriseEventTransformer,
    ProcessingPipeline,
    StreamProcessor,
)


def make_event(event_type="user_registration", enterprise_id="ent-001", **extra):
    event = {
        "event_type": event_type,
        "enterprise_id": enterprise_id,
        "timestamp": "2026-11-06T10:00:00Z",
    }
    event.update(extra)
    return event


def test_abstract_class_cannot_be_instantiated():
    with pytest.raises(TypeError):
        StreamProcessor()


def test_event_type_filter_accepts_matching_event():
    processor = EventTypeFilter({"user_registration"})
    event = make_event()

    result = processor.process(event)

    assert result == event
    assert result is not event


def test_event_type_filter_rejects_other_events():
    processor = EventTypeFilter({"enterprise_update"})
    event = make_event(event_type="user_registration")

    assert processor.process(event) is None


def test_event_type_filter_validates_configuration():
    with pytest.raises(ValueError, match="At least one event type is required"):
        EventTypeFilter(set())

    with pytest.raises(ValueError, match="Unsupported event type"):
        EventTypeFilter({"unsupported_event"})


def test_event_type_filter_accepts_multiple_types():
    processor = EventTypeFilter({"user_registration", "department_created"})

    assert processor.process(make_event(event_type="user_registration")) is not None
    assert processor.process(make_event(event_type="department_created")) is not None
    assert processor.process(make_event(event_type="enterprise_update")) is None


def test_transformer_enriches_event():
    processor = EnterpriseEventTransformer()
    event = make_event(
        event_type="user_registration",
        user_email="alice@example.com",
    )

    result = processor.process(event)

    assert result["status"] == "processed"
    assert result["normalized_event_type"] == "User Registration"
    assert "alice@example.com" in result["audit_summary"]
    assert result["enterprise_id"] == "ent-001"


def test_transformer_raises_for_missing_type():
    processor = EnterpriseEventTransformer()

    with pytest.raises(ValueError, match="missing 'event_type'"):
        processor.process({"enterprise_id": "ent-001"})


def test_operator_overloading_creates_pipeline():
    pipeline = EventTypeFilter({"user_registration"}) | EnterpriseEventTransformer()

    assert isinstance(pipeline, ProcessingPipeline)


def test_pipeline_filters_and_transforms():
    pipeline = EventTypeFilter({"user_registration", "department_created"}) | EnterpriseEventTransformer()

    events = [
        make_event(event_type="user_registration", user_email="alice@example.com"),
        make_event(event_type="enterprise_update"),
        make_event(event_type="department_created", department_name="Engineering"),
    ]

    results = list(pipeline.run(events))

    assert len(results) == 2
    assert results[0]["audit_summary"].startswith("User alice@example.com")
    assert results[1]["audit_summary"].startswith("Department Engineering")


def test_pipeline_supports_chaining():
    pipeline = (
        EventTypeFilter({"user_registration", "enterprise_update"})
        | EventTypeFilter({"user_registration"})
        | EnterpriseEventTransformer()
    )

    result = pipeline.process(make_event(event_type="user_registration", user_email="bob@example.com"))

    assert result["audit_summary"].startswith("User bob@example.com")


def test_event_stream_is_iterator():
    stream = EventStream([
        make_event(event_type="user_registration"),
        make_event(event_type="department_created", department_name="HR"),
    ])

    assert iter(stream) is stream
    assert next(stream)["event_type"] == "user_registration"
    assert next(stream)["department_name"] == "HR"

    with pytest.raises(StopIteration):
        next(stream)


def test_pipeline_generator_is_lazy():
    pipeline = EventTypeFilter({"user_registration"}) | EnterpriseEventTransformer()
    events = EventStream([make_event(user_email="charlie@example.com")])

    generator = pipeline.run(events)

    assert hasattr(generator, "__next__")

    result = next(generator)

    assert result["status"] == "processed"
    assert "charlie@example.com" in result["audit_summary"]

    with pytest.raises(StopIteration):
        next(generator)


def test_original_event_is_not_modified():
    event = make_event(user_email="dana@example.com")
    original = event.copy()

    result = EnterpriseEventTransformer().process(event)

    assert event == original
    assert "status" not in event
    assert "status" in result


def test_invalid_event_type_rejected_by_filter():
    processor = EventTypeFilter({"user_registration"})

    with pytest.raises(TypeError):
        processor.process(None)


def test_stream_processor_is_polymorphic():
    filters = [
        EventTypeFilter({"user_registration"}),
        EventTypeFilter({"enterprise_update"}),
    ]

    for processor, event_type in [
        (filters[0], "user_registration"),
        (filters[1], "enterprise_update"),
    ]:
        assert isinstance(processor, StreamProcessor)
        assert processor.process(make_event(event_type=event_type)) is not None
