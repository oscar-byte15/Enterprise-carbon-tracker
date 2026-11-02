# Hometask 1 — Subsystem 2: Object-Oriented Concepts

**Author:** Oscar Daniel de la Cruz Jara  
**Assigned subsystem:** Carbon Activity Management & Calculation Engine

## Three implemented classes

| Class | Responsibility | Constructor | Encapsulation / setup |
|---|---|---|---|
| `ActivityRecord` | Models an enterprise carbon activity with category, type, amount, unit, date, and enterprise | `__init__(...)` | Getters/setters validate state; `get_period()` derives reporting month |
| `EmissionFactor` | Represents a configured emission multiplier and metadata | `__init__(...)` | Getters/setters and `matches(activity)` |
| `CalculationService` | Loads catalog, selects factor, validates units and calculates CO2e | `__init__(factor_catalog=None)` | `initialize_factors()`, catalog getter/setter, `calculate()` |

The OOP implementation lives in `backend/app/activities/oop.py`. It is intentionally non-disruptive: existing FastAPI endpoints, schemas and MongoDB code retain their original behavior.

## UML class diagram

```mermaid
classDiagram
    class ActivityRecord {
      -str _category
      -str _activity_type
      -Decimal _amount
      -str _unit
      -date _date
      -str _enterprise_id
      +get_amount() float
      +set_amount(value)
      +get_period() str
    }
    class EmissionFactor {
      -str _category
      -str _activity_type
      -Decimal _factor
      -str _unit
      -str _source
      +get_factor() float
      +set_factor(value)
      +matches(activity) bool
    }
    class CalculationService {
      -dict _factor_catalog
      +initialize_factors()
      +get_factor_catalog() dict
      +set_factor_catalog(catalog)
      +get_emission_factor(category, type) EmissionFactor
      +validate_units(activity, factor)
      +calculate(activity) dict
    }
    CalculationService ..> ActivityRecord : processes
    CalculationService ..> EmissionFactor : creates/uses
    EmissionFactor ..> ActivityRecord : matches
```

Each model also exposes getters/setters for its other private attributes; see source for the full implementation.

## Run the tests

From `backend/`:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest tests/test_oop_hometask1.py -v
```

## Suggested personal demonstration (~45–60 seconds)

1. Explain how `ActivityRecord` encapsulates activity inputs and rejects nonpositive amounts.
2. Show `EmissionFactor.matches()` preventing invalid category/type/unit combinations.
3. Explain how `CalculationService` loads the existing JSON factors and computes a two-decimal result.
4. Demonstrate `python -m pytest tests/test_oop_hometask1.py -v` and connect the class relationships to this Mermaid UML.

## Team video

Add the final **single 3–5 minute team presentation link** to the root README once the recording is uploaded.
