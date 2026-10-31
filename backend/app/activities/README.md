# Subsystem 2 — Carbon Activity Management & Calculation Engine

## 1. Overview

This subsystem manages enterprise carbon activity records and calculates greenhouse gas emissions using documented emission factors.

It supports electricity, heating, transport, and waste activities.

Main responsibilities:

- Validate carbon activity requests using Pydantic.
- Calculate emissions in kilograms of CO₂ equivalent (kg CO₂e).
- Store activities and calculation results in MongoDB.
- Support Create, Read, Update, and Delete operations.
- Restrict data access using the authenticated enterprise ID.
- Preserve emission factor metadata for traceability.

## 2. Emission Calculation Formula

The Calculation Engine applies:

**CO₂e (kg) = Activity Amount × Emission Factor**

Where:

- **Activity Amount:** Quantity of energy, fuel, or waste.
- **Emission Factor:** Emissions per unit of activity.
- **CO₂e:** Resulting emissions, expressed in kilograms of CO₂ equivalent.

The activity unit must match the unit associated with the emission factor.

## 3. Supported Activities and Units

| Category | Activity type | Input unit | Factor unit |
|---|---|---|---|
| Electricity | Grid electricity | kWh | kg CO₂e/kWh |
| Heating | Natural gas | kWh | kg CO₂e/kWh |
| Transport | Petrol | L | kg CO₂e/L |
| Transport | Diesel | L | kg CO₂e/L |
| Waste | Plastic - Recycling | kg | kg CO₂e/kg |
| Waste | Organic - Composting | kg | kg CO₂e/kg |
| Waste | General - Landfill | kg | kg CO₂e/kg |

## 4. Worked Example

For 500 kWh of electricity consumption:

- Activity amount: 500 kWh
- Emission factor: 0.352 kg CO₂e/kWh
- Calculation: 500 × 0.352
- Result: **176.00 kg CO₂e**

The electricity factor represents the German electricity generation mix for the configured reference year.

## 5. Emission Factor Configuration

Emission factors are stored in `emission_factors.json`, outside the calculation source code.

Each configured factor includes:

- Factor value and measurement unit
- Source and source URL
- Reference year and geographical region
- Calculation methodology
- Waste treatment method, where applicable

The current catalog includes German electricity factors and UK reference factors for fuels and waste. These factors have different reporting boundaries and must not be presented as universally equivalent lifecycle estimates.

## 6. Validation Rules

The system rejects:

- Zero or negative activity amounts
- Non-finite numbers
- Unknown categories
- Activity types incompatible with their category
- Incorrect measurement units
- Invalid dates

Pydantic validates incoming requests before persistence. The Calculation Engine also performs its own validation.

## 7. Precision and Rounding

The engine uses Python's `Decimal` for the multiplication and rounds calculated results to two decimal places using `ROUND_HALF_UP`.

Example:

1.234 kWh × 0.352 = 0.434368 kg CO₂e

Stored result: **0.43 kg CO₂e**

The underlying emission factor is preserved separately from the rounded result.

## 8. MongoDB Persistence

Collection: `activity_records`

Each new record includes an activity UUID, the authenticated `enterprise_id`, activity details, the calculated emissions, and emission factor metadata.

The repository provides CRUD operations and filters records by enterprise ID. A compound index on `enterprise_id` and `date` supports enterprise-specific queries.

## 9. Performance Requirement — NFR2

Target: individual Calculation Engine execution under 50 milliseconds.

Benchmark command, executed from the `backend` directory:

`python -m tests.benchmark_calculator`

Measurements include loading the factor JSON and executing the calculation, but exclude HTTP and database latency.

Record the date, execution environment, number of calculations, mean latency, P95 latency, maximum latency and result after running the benchmark.

## 10. Automated Tests

Unit tests use Pytest and MongoMock to validate calculations, request schemas, CRUD behavior and enterprise-based repository isolation.

Run locally from the `backend` directory:

`python -m pytest tests/ -v`

The repository tests use a simulated MongoDB collection and do not modify production records.

## 11. Scope and Limitations

- The calculation catalog contains reference factors tied to specific years, regions and methodologies.
- Historical records retain their factor values.
- The benchmark evaluates the calculation function, not total API latency.
- Full enterprise lifecycle persistence belongs to Subsystem 1.
- Dashboard analytics and AI recommendations belong to Subsystem 3.