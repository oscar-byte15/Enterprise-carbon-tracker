## Running the Project with Docker Compose

This project supports Docker Compose to simplify the setup and execution of the Enterprise Carbon Tracker application.

Docker Compose automatically builds and runs three services:

- **Frontend:** React + Vite
- **Backend:** Python + FastAPI
- **Database:** MongoDB 8.0

### Prerequisites

Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and ensure Docker Engine is running.

You do not need to install MongoDB, Python, or Node.js separately when using Docker.

### Step 1: Clone the repository

```bash
git clone https://github.com/oscar-byte15/Enterprise-carbon-tracker.git
cd Enterprise-carbon-tracker
```

### Step 2: Configure environment variables

Create a `.env` file in the project root using `.env.example` as a reference.

Configure any required local development secrets or API keys. Never commit real credentials to GitHub.

### Step 3: Start the application

From the project root, run:

```bash
docker compose up --build -d
```

Docker Compose will build and start the frontend, backend, and MongoDB services.

### Step 4: Access the application

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| FastAPI Swagger UI | http://localhost:8000/docs |
| MongoDB Compass | mongodb://127.0.0.1:27018 |

### Useful commands

```bash
# Start containers
docker compose up -d

# Check container status
docker compose ps

# View backend logs
docker compose logs -f backend

# Rebuild after code changes
docker compose up --build -d

# Stop containers
docker compose down
```

### Database persistence

MongoDB uses a Docker volume to persist application data between normal container restarts.

Each developer runs an independent local MongoDB database. Docker Compose does not automatically synchronize data between team members.

**Important:** Avoid `docker compose down -v` unless you intentionally want to remove the Docker-managed database volume.

### Development notes

- FastAPI communicates with MongoDB through the Docker Compose service network.
- The frontend communicates with FastAPI through the exposed backend port.
- Code changes may require rebuilding Docker images.
- Authentication and enterprise records are persisted in MongoDB through `backend/app/mongo_store.py`, which is instantiated by `backend/app/store.py` for the FastAPI routes.
- For additional information, refer to `DOCKER-README.md`.

## Running Unit Tests with Docker

The project supports automated unit testing with **Pytest**.

Subsystem 2 (Carbon Activity Management & Calculation Engine) currently includes 22 unit tests covering emission calculations, input validation, CRUD operations, and enterprise-based data isolation.

### Run Unit Tests using Docker

From the project root directory, build the testing image:

```bash
docker build --target test -t carbon-tracker-tests ./backend
```

Then run the tests:

```bash
docker run --rm carbon-tracker-tests
```

Docker will execute the tests inside an isolated container using Pytest and MongoMock.

**Note:** MongoMock simulates the database, so these unit tests do not require a running MongoDB server or modify production data.

### Run Unit Tests locally

Alternatively, from the `backend` directory:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest tests/ -v
```

### Verified Test Results

| Test Module | Passed | Failed |
|---|---:|---:|
| Calculation Engine | 14 | 0 |
| MongoDB Repository | 8 | 0 |
| **Total** | **22** | **0** |

Last verified: October 31, 2026.

These tests verify the configured emission calculations, repository CRUD operations, and enterprise data isolation at the repository level. They do not replace full API integration or end-to-end tests.

### Adding New Tests

When adding new test files or modifying existing tests, rebuild the test image:

```bash
docker build --target test -t carbon-tracker-tests ./backend
docker run --rm carbon-tracker-tests
```

This ensures Docker runs the latest tests.
---

## Hometask 1 — Object-Oriented Concepts

This assignment translates the team's Capstone subsystem architecture into Python OOP classes. **Submission branch:** `Homeassignment1`.

### Team Overview

| Team member | Assigned subsystem | Implementation |
|---|---|---|
| Xiangping Kong | Subsystem 1 — Authentication & Enterprise Management | [Three OOP classes (User, Enterprise, Department), UML and unit tests](#subsystem-1--user-authentication--enterprise-management-oop-implementation) |
| Oscar Daniel de la Cruz Jara | Subsystem 2 — Carbon Activity Management & Calculation Engine | [Three OOP classes (ActivityRecord, EmissionFactor, CalculationService) and UML](#subsystem-2--carbon-activity-management--calculation-engine) |
| Usama Rasheed | Subsystem 3 — Analytics Dashboard & AI Advisory | [Three OOP classes (EmissionMetric, AnalyticsEngine, SustainabilityAdvisor), UML and unit tests](#subsystem-3--analytics-dashboard--ai-advisory-oop-implementation) |

### System Design — UML Diagrams

#### Subsystem 1 - Authentication & Enterprise Management

The User and Department classes are logically associated with Enterprise through the `enterprise_id` attribute. These relationships represent references by identifier rather than direct object ownership. Therefore, no composition or aggregation is implemented between the three classes.

```mermaid

classDiagram
    class User {
        -str _id
        -str _email
        -str _password_hash
        -str _enterprise_id
        -str _role
        +__init__(email, password_hash, enterprise_id, role)
        +get_email() str
        +set_email(email)
        +get_role() str
        +set_role(role)
    }

    class Enterprise {
        -str _enterprise_id
        -str _company_name
        -str _industry
        -str _address
        +__init__(company_name, industry, enterprise_id)
        +get_enterprise_id() str
        +get_company_name() str
        +get_industry() str
        +get_address() str
        +set_company_name(name)
        +set_industry(industry)
        +set_address(address)
        +update_profile(company_name, industry, address)
    }

    class Department {
        -str _department_id
        -str _enterprise_id
        -str _name
        -str _description
        +__init__(enterprise_id, name, description, department_id)
        +get_department_id() str
        +get_enterprise_id() str
        +get_name() str
        +get_description() str
        +set_name(name)
        +set_description(description)
        +update_details(name, description)
    }

    User ..> Enterprise : references enterprise_id
    Department ..> Enterprise : references enterprise_id
```

#### Subsystem 2 — Carbon Activity Management & Calculation Engine

The composition (◆) indicates CalculationService owns zero or more EmissionFactor objects; there is no aggregation between the three classes. ActivityRecord is supplied to a calculation, rather than owned. Full design details are available in [Hometask 1 — Subsystem 2](docs/Hometask1-Subsystem2.md).

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
        +matches(activity) bool
        +get_factor() float
        +set_factor(value)
    }
    class CalculationService {
        -dict _factor_catalog
        -dict _factors
        +initialize_factors()
        +get_factor_catalog() dict
        +set_factor_catalog(catalog)
        +get_emission_factor(category, type) EmissionFactor
        +validate_units(activity, factor)
        +calculate(activity) dict
    }
    CalculationService "1" *-- "0..*" EmissionFactor : owns
    CalculationService ..> ActivityRecord : calculates for
    EmissionFactor ..> ActivityRecord : matches
```

#### Subsystem 3 — Analytics Dashboard & AI Advisory

The composition (◆) models AnalyticsEngine creating, managing, and owning multiple EmissionMetric instances. SustainabilityAdvisor exhibits a dependency (..>) on AnalyticsEngine, analyzing enterprise metrics without retaining ownership.

```mermaid
classDiagram
    class EmissionMetric {
        -str _category
        -Decimal _co2e_kg
        -Decimal _percentage
        -int _activity_count
        +get_category() str
        +set_category(value)
        +get_co2e_kg() float
        +set_co2e_kg(value)
        +get_percentage() float
        +set_percentage(value)
        +get_activity_count() int
        +set_activity_count(value)
        +to_dict() dict
    }
    class AnalyticsEngine {
        -str _enterprise_id
        -dict _metrics
        -Decimal _total_co2e_kg
        +initialize_metrics()
        +get_enterprise_id() str
        +set_enterprise_id(value)
        +get_total_co2e_kg() float
        +get_metrics() dict
        +set_metrics(metrics)
        +add_metric(category, co2e_kg, count)
        +recalculate_percentages()
        +get_top_category() str
        +generate_summary() dict
    }
    class SustainabilityAdvisor {
        -str _advisor_mode
        -dict _catalog
        +initialize_catalog()
        +get_advisor_mode() str
        +set_advisor_mode(mode)
        +get_catalog() dict
        +set_catalog(catalog)
        +generate_recommendations(analytics) list
    }
    AnalyticsEngine "1" *-- "0..*" EmissionMetric : owns
    SustainabilityAdvisor ..> AnalyticsEngine : analyzes
```

**Team note:** Add UML diagrams for Subsystems 1 and 4 when their owners finish implementing their three classes.

### Subsystem 1 — User Authentication & Enterprise Management (OOP Implementation)

The Subsystem 1 OOP implementation is located in `backend/app/oop_subsystem1.py`.

This subsystem focuses on user account information, enterprise profiles, and department management. Three OOP classes have been implemented to represent the core entities of Subsystem 1.

#### Three Implemented Classes

| Class | Responsibility | Constructor | Encapsulation / Methods |
|---|---|---|---|
| `User` | Represents a user account associated with an enterprise. Stores the user's email, hashed password, enterprise ID, and role. | `__init__(email, password_hash, enterprise_id, role="admin")` | Uses protected-style attributes (`_email`, `_role`, etc.) and getter/setter methods to access and update account information. |
| `Enterprise` | Represents an enterprise profile, including its company name, industry, and address. | `__init__(company_name, industry, enterprise_id=None)` | Provides getter/setter methods for enterprise information and `update_profile()` for updating multiple profile fields. |
| `Department` | Represents a department belonging to an enterprise, including its name and description. | `__init__(enterprise_id, name, description=None, department_id=None)` | Provides getter/setter methods for department information and `update_details()` for updating department details. |

#### Mapping to Capstone Subsystem 1 Architecture

- **`User`:** Corresponds to the user account information managed during registration and authentication.
- **`Enterprise`:** Represents the enterprise profile created during registration and maintained through enterprise profile management.
- **`Department`:** Represents the department information managed through department creation and listing functionality.

#### OOP Concepts Applied

- **Constructors:** Each class uses `__init__()` to initialize its attributes.
- **Encapsulation:** Attributes use a leading underscore, with getter and setter methods providing controlled access.
- **Data validation:** Setter methods validate selected fields, such as non-empty email addresses, company names, and department names.
- **Configuration methods:** `Enterprise.update_profile()` and `Department.update_details()` support updating object information.
- **Class relationships:** `User` and `Department` reference an enterprise through `enterprise_id`.

**Implementation note:** These classes are implemented separately for Hometask 1. The existing FastAPI routes and application behavior remain unchanged.

### Subsystem 2 — Carbon Activity Management & Calculation Engine (OOP Implementation)

The Subsystem 2 OOP implementation is located in `backend/app/activities/oop.py`.

This subsystem manages enterprise carbon activity records, emission factor configurations, and CO2e calculations. Three OOP classes implement the domain model and support the FastAPI activity creation and update workflow.

#### Three Implemented Classes

| **Class** | **Responsibility** | **Constructor** | **Encapsulation / Methods** |
| --------- | ------------------ | --------------- | --------------------------- |
| `ActivityRecord` | Represents an enterprise carbon activity, storing its category, activity type, amount, unit, date, and enterprise ID. | `__init__(category, activity_type, amount, unit, activity_date, enterprise_id)` | Uses underscore-prefixed attributes with getters and validated setters; `get_period()` derives the reporting period. |
| `EmissionFactor` | Represents the conversion factor associated with an activity category, type, unit, and source. | `__init__(category, activity_type, factor, unit, source)` | Provides validated getters and setters; `matches(activity)` checks whether a factor matches an activity. |
| `CalculationService` | Loads and manages emission factors, validates units, and calculates CO2e emissions. | `__init__(factor_catalog=None)` | Provides `initialize_factors()`, `get_factor_catalog()`, `set_factor_catalog()`, `get_emission_factor()`, `validate_units()`, and `calculate()`. |

#### Mapping to Capstone Subsystem 2 Architecture

- **`ActivityRecord`:** Represents activity data validated and prepared during FastAPI create/update requests.
- **`EmissionFactor`:** Represents a category-specific emission factor loaded from the configured JSON catalog and used during CO2e calculations.
- **`CalculationService`:** Implements the calculation engine used by `POST /activities/` and `PUT /activities/{activity_id}` before the processed records are persisted through the MongoDB repository.

#### OOP Concepts Applied

- **Constructors:** Each class uses `__init__()` to initialize state.
- **Encapsulation:** Attributes use a leading underscore, with getter and setter methods providing controlled access.
- **Data validation:** Setters reject missing fields, non-positive amounts, negative factors, and invalid dates or units.
- **Composition:** `CalculationService` creates and owns its `EmissionFactor` objects.
- **Class relationships:** `CalculationService` uses an `ActivityRecord` and a matching `EmissionFactor` to calculate emissions, rather than owning the activity record.

**Implementation note:** These classes are integrated into the existing FastAPI activity create/update workflow in `backend/app/activities/router.py`. MongoDB persistence is handled separately by `MongoActivityRepository`.

### Subsystem 3 — Analytics Dashboard & AI Advisory (OOP Implementation)

The Subsystem 3 OOP implementation is located in `backend/app/analytics/oop.py`.

#### Three Implemented Classes

| Class | Responsibility | Constructor | Encapsulation / Relationships |
|---|---|---|---|
| `EmissionMetric` | Encapsulates an aggregated carbon metric for a category, tracking emissions, share percentage, and activity count | `__init__(category, co2e_kg, percentage=0.0, activity_count=0)` | Private attributes with setters enforcing range and numeric constraints; `to_dict()` for dashboard serialization |
| `AnalyticsEngine` | Aggregates enterprise activity records, calculates total emissions, computes category percentages, and detects the top carbon driver | `__init__(enterprise_id, raw_activities=None)` | **Composition:** `AnalyticsEngine "1" *-- "0..*" EmissionMetric : owns`. Defensive copies returned from `get_metrics()` |
| `SustainabilityAdvisor` | Evaluates enterprise analytics to produce prioritized, actionable carbon mitigation recommendations (High/Medium/Low) | `__init__(advisor_mode="rules", catalog=None)` | **Dependency:** `SustainabilityAdvisor ..> AnalyticsEngine : analyzes`. Defensive copying of advisory strategy catalog |

#### Mapping to Capstone Subsystem 3 Architecture
- **`EmissionMetric`:** Directly mirrors the category breakdown cards and distribution chart elements on the Analytics Dashboard (`frontend/src/features/activities/pages/Dashboard.jsx`).
- **`AnalyticsEngine`:** Represents the domain aggregation engine powering `GET /analytics/summary` and monthly reporting trends in `backend/app/analytics/`.
- **`SustainabilityAdvisor`:** Encapsulates the recommendation generation engine powering the AI Coach (`frontend/src/features/activities/pages/AICoach.jsx`) and `POST /ai/recommendations`.

### Team Video Presentation (3–5 minutes)

**Video link:** Pending team recording — replace this placeholder with the direct YouTube, Loom or Google Drive link before submission.

All four team members should explain their own classes and how they correspond to their subsystem's UML architecture.

### Running Hometask 1 Tests

```bash
cd backend
python -m pip install -r requirements-dev.txt
# Run Subsystem 1 OOP tests
python -m pytest tests/test_oop_subsystem1.py -v

# Run Subsystem 2 OOP tests
python -m pytest tests/test_oop_hometask1.py -v

# Run Subsystem 3 OOP tests
python -m pytest tests/test_oop_subsystem3.py -v

# Run all Hometask 1 tests together
python -m pytest tests/test_oop_hometask1.py tests/test_oop_subsystem3.py -v
```

## Hometask 2 — Real-Time Data Processing

### Project Overview

**Project:** Enterprise Carbon Footprint Tracker & AI Assistant

**Submission Branch:** `HomeworkAssignment2`

This assignment implements an event-driven stream processing
framework in Python using Object-Oriented Programming (OOP).

The framework filters operational carbon activities by
GHG emission scope (Scope 1, Scope 2, and Scope 3) and
transforms valid activity measurements into metric tons
of CO2 equivalent (CO2e).

### Subsystem 2 — Carbon Activity Streaming Pipeline

**Implemented by:** Oscar Daniel de la Cruz Jara

**Source Code:**
`backend/app/activities/subsystem2_homeassignment2.py`

**Automated Tests:**
`backend/tests/test_subsystem2_homeassignment2.py`

### Implemented Classes

| Class | Responsibility | OOP Concept |
|---|---|---|
| `StreamProcessor` | Defines the abstract processing interface. | Abstract Base Class |
| `ScopeFilter` | Filters events according to emission scope. | Inheritance & Polymorphism |
| `EmissionTransformer` | Converts activity metrics into metric tons of CO2e. | Inheritance & Polymorphism |
| `ProcessingPipeline` | Composes and executes stream processors. | Operator Overloading & Generators |
| `EventStream` | Iterates through incoming activity events. | Iterators |

### UML Class Diagram — Subsystem 2

```mermaid
classDiagram
    direction TB

    class StreamProcessor {
        <<abstract>>
        +process(event: dict) dict | None*
        +__or__(other: StreamProcessor) ProcessingPipeline
    }

    class ScopeFilter {
        +VALID_SCOPES: set
        -_allowed_scopes: set
        +__init__(allowed_scopes: set)
        +process(event: dict) dict | None
    }

    class EmissionTransformer {
        -_calculation_service: CalculationService
        +__init__(calculation_service=None)
        +process(event: dict) dict
    }

    class ProcessingPipeline {
        -_processors: list
        +__init__(processors: list)
        +__or__(other: StreamProcessor) ProcessingPipeline
        +process(event: dict) dict | None
        +run(stream) Generator
    }

    class EventStream {
        -_events: Iterator
        +__init__(events)
        +__iter__() EventStream
        +__next__() dict
    }

    class ActivityRecord {
        -_category: str
        -_activity_type: str
        -_amount: Decimal
        -_unit: str
        -_date: date
        -_enterprise_id: str
        +__init__(category, activity_type, amount, unit, activity_date, enterprise_id)
        +get_category()
        +set_category(value)
        +get_activity_type()
        +set_activity_type(value)
        +get_amount()
        +set_amount(value)
        +get_unit()
        +set_unit(value)
        +get_date()
        +set_date(value)
        +get_enterprise_id()
        +set_enterprise_id(value)
        +get_period()
    }

    class CalculationService {
        -_factor_catalog: dict
        -_factors: dict
        +__init__(factor_catalog=None)
        +initialize_factors()
        +get_factor_catalog()
        +set_factor_catalog(catalog)
        +get_emission_factor(category, activity_type)
        +validate_units(activity, factor)
        +calculate(activity)
    }

    class EmissionFactor {
        -_category: str
        -_activity_type: str
        -_factor: Decimal
        -_unit: str
        -_source: str
        +__init__(category, activity_type, factor, unit, source)
        +get_category()
        +set_category(value)
        +get_activity_type()
        +set_activity_type(value)
        +get_factor()
        +set_factor(value)
        +get_unit()
        +set_unit(value)
        +get_source()
        +set_source(value)
        +matches(activity)
    }

    StreamProcessor <|-- ScopeFilter
    StreamProcessor <|-- EmissionTransformer
    StreamProcessor <|-- ProcessingPipeline

    ProcessingPipeline "0..*" o-- "1..*" StreamProcessor : aggregates
    EmissionTransformer "0..*" --> "1" CalculationService : references

    EmissionTransformer ..> ActivityRecord : creates
    ProcessingPipeline ..> EventStream : consumes
    CalculationService "1" *-- "0..*" EmissionFactor : owns
    CalculationService ..> ActivityRecord : calculates
```

### OOP Concepts Applied

**1. Abstract Base Classes**

`StreamProcessor` inherits from Python's `ABC` and declares
`process()` using `@abstractmethod`.

**2. Inheritance and Polymorphism**

`ScopeFilter`, `EmissionTransformer`, and `ProcessingPipeline`
inherit from `StreamProcessor` and implement `process()`
with different behaviors.

**3. Operator Overloading**

The `__or__()` method allows processors to be composed
using the `|` operator.

**4. Iterators and Generators**

`EventStream` implements `__iter__()` and `__next__()`,
while `ProcessingPipeline.run()` uses `yield` for lazy
event processing.

### Processing Example

```python
pipeline = (
    ScopeFilter({"Scope 2"})
    | EmissionTransformer()
)

for result in pipeline.run(EventStream(events)):
    print(result["co2e_tons"])
```

For an electricity activity of 100 kWh with an emission
factor of 0.352 kg CO2e/kWh, the result is:

```text
0.0352 metric tons CO2e
```

### Run Automated Tests

From the `backend` directory:

```bash
# Run Subsystem 2 tests
python -m pytest tests/test_subsystem2_homeassignment2.py -v
```

---

### Subsystem 3 — Analytics Dashboard & AI Advisory Streaming Pipeline

**Implemented by:** Usama Rasheed

**Source Code:**
`backend/app/analytics/subsystem3_homeassignment2.py`

**Automated Tests:**
`backend/tests/test_subsystem3_homeassignment2.py`

**Interactive Demonstration:**
`backend/demo_subsystem3_homeassignment2.py`

#### Scenario Overview

Subsystem 3 ingests high-frequency, operational carbon telemetry feeds across three critical enterprise activity streams:
1. **Business Travel Flight Bookings (Scope 3):** Flight distance in kilometers, passenger volume, cabin travel tier, and radiative forcing flight categorization.
2. **Data Center Server Utility Logs (Scope 2):** Server electrical energy in kWh, Power Usage Effectiveness (PUE), server load ratio, and regional grid intensity factors.
3. **Freight Logistics Payloads (Scope 1 & Scope 3):** Heavy freight cargo weight in tons, transit distance, and multimodal transport logistics (road, rail, sea, air freight).

The streaming pipeline filters operational activity records by GHG Protocol scope tags (`Scope 1`, `Scope 2`, `Scope 3`) and transforms real-time metrics into **metric tons of $\text{CO}_2\text{e}$** ($\text{tCO}_2\text{e}$).

#### Implemented Classes

| Class | Responsibility | OOP Concept |
|---|---|---|
| `StreamProcessor` | Abstract root interface contract defining `process()` and pipeline composition. | Abstract Base Class (ABC) |
| `ScopeFilter` | Filters streaming telemetry events by GHG emission scope (`Scope 1`, `Scope 2`, `Scope 3`). | Inheritance & Polymorphism |
| `FlightTelemetryProcessor` | Transforms corporate flight bookings into metric tons of CO2e based on distance, cabin class, and pkm factors. | Inheritance & Polymorphism |
| `DataCenterTelemetryProcessor` | Transforms server utility and compute logs into metric tons of CO2e considering PUE and grid intensity. | Inheritance & Polymorphism |
| `FreightTelemetryProcessor` | Transforms freight shipping payloads into metric tons of CO2e using modal tonne-kilometer factors. | Inheritance & Polymorphism |
| `ProcessingPipeline` | Sequentially chains and executes stream processors using operator composition and lazy generators. | Operator Overloading (`\|`, `+`) & Generators (`yield`) |
| `TelemetryStream` | Iterates over incoming telemetry events one by one. | Iterators (`__iter__`, `__next__`) |

#### UML Class Diagram — Subsystem 3

```mermaid
classDiagram
    direction TB

    class StreamProcessor {
        <<abstract>>
        +process(event: dict) dict | None*
        +__or__(other: StreamProcessor) ProcessingPipeline
        +__add__(other: StreamProcessor) ProcessingPipeline
        +run(stream) Generator
    }

    class ScopeFilter {
        +VALID_SCOPES: set
        -_allowed_scopes: set
        +__init__(allowed_scopes: set)
        +get_allowed_scopes() set
        +process(event: dict) dict | None
    }

    class FlightTelemetryProcessor {
        +BASE_FACTORS: dict
        +CABIN_MULTIPLIERS: dict
        +process(event: dict) dict
    }

    class DataCenterTelemetryProcessor {
        +DEFAULT_GRID_FACTOR: Decimal
        +DEFAULT_PUE: Decimal
        +process(event: dict) dict
    }

    class FreightTelemetryProcessor {
        +MODE_FACTORS: dict
        +process(event: dict) dict
    }

    class ProcessingPipeline {
        -_processors: list
        +__init__(processors: list)
        +get_processors() list
        +__or__(other: StreamProcessor) ProcessingPipeline
        +__add__(other: StreamProcessor) ProcessingPipeline
        +process(event: dict) dict | None
        +run(stream) Generator
    }

    class TelemetryStream {
        -_events: Iterator
        +__init__(events)
        +__iter__() TelemetryStream
        +__next__() dict
    }

    StreamProcessor <|-- ScopeFilter
    StreamProcessor <|-- FlightTelemetryProcessor
    StreamProcessor <|-- DataCenterTelemetryProcessor
    StreamProcessor <|-- FreightTelemetryProcessor
    StreamProcessor <|-- ProcessingPipeline

    ProcessingPipeline "1" *-- "1..*" StreamProcessor : composes
    ProcessingPipeline ..> TelemetryStream : consumes
```

#### Mapping to Required OOP Concepts

1. **Abstract Base Classes (ABCs):**
   `StreamProcessor` inherits from Python's `abc.ABC` and defines the abstract contract `@abstractmethod def process(self, event: dict) -> dict | None`.
2. **Inheritance & Polymorphism:**
   `ScopeFilter`, `FlightTelemetryProcessor`, `DataCenterTelemetryProcessor`, `FreightTelemetryProcessor`, and `ProcessingPipeline` inherit from `StreamProcessor` and polymorphically implement `process()` to transform distinct telemetry schemas.
3. **Operator Overloading:**
   `StreamProcessor` and `ProcessingPipeline` implement both `__or__()` (`|`) and `__add__()` (`+`), enabling expressive, declarative pipeline composition:
   ```python
   pipeline = scope_filter | flight_processor | datacenter_processor + freight_processor
   ```
4. **Iterators & Generators:**
   `TelemetryStream` implements the standard iterator protocol with `__iter__()` and `__next__()`. `ProcessingPipeline.run()` lazily processes telemetry events using a generator with `yield`.

#### Processing Example

```python
pipeline = (
    ScopeFilter({"Scope 2", "Scope 3"})
    | FlightTelemetryProcessor()
    | DataCenterTelemetryProcessor()
)

stream = TelemetryStream(telemetry_events)
for record in pipeline.run(stream):
    print(f"{record['telemetry_type'].upper()}: {record['co2e_tons']:.6f} tCO2e")
```

#### Run Automated Tests

From the `backend` directory:

```bash
# Run Subsystem 2 tests
python -m pytest tests/test_subsystem2_homeassignment2.py -v

# Run Subsystem 3 tests
python -m pytest tests/test_subsystem3_homeassignment2.py -v

# Run all Hometask 2 tests
python -m pytest tests/test_subsystem2_homeassignment2.py tests/test_subsystem3_homeassignment2.py -v
```

#### Run Interactive Demonstration

```bash
cd backend
python demo_subsystem3_homeassignment2.py
```


### Team Video Presentation

**Duration:** 5 minutes

**Video Link:** Pending team recording.
Replace this placeholder with the direct video link
before submission.

## Hometask 3 — Web APIs & Database Access Layers

This assignment documents the current FastAPI + MongoDB implementation of the Enterprise Carbon Tracker. The project is structured as a full-stack application: a React frontend in `frontend/` consumes the backend API, the FastAPI backend in `backend/app/` exposes the business logic, and MongoDB persists tenant and activity data in the database layer.

### Project architecture

- **Frontend:** `frontend/` contains the React + Vite app for authentication, activity capture, analytics, and enterprise profile screens.
- **Backend:** `backend/app/` contains FastAPI routers, validation schemas, calculation logic, analytics services, and MongoDB access objects.
- **Database:** MongoDB is used for persistent storage of users, enterprises, departments, and carbon activity records. The app connects through `pymongo` using the configured `MONGODB_URI` and `MONGODB_DB` values in `backend/app/config.py`.

### Implemented API endpoints

The API is assembled in `backend/app/main.py` and includes the following authenticated and public routes.

#### Subsystem 1 — Authentication & Enterprise Management

`backend/app/routes.py` exposes the following endpoints:

- `POST /login` — authenticate a user and return a JWT token
- `POST /register` — create an enterprise and its admin user
- `GET /profile` — return the current enterprise profile
- `PUT /profile` — update the current enterprise profile
- `GET /departments` — list departments for the current enterprise
- `POST /departments` — create a department for the current enterprise

#### Subsystem 2 — Carbon Activity Management & Calculation Engine

`backend/app/activities/router.py` registers the `"/activities"` router and implements:

- `POST /activities/` — create an activity, validate inputs, calculate CO2e, and save the record
- `GET /activities/` — list all activities for the authenticated enterprise
- `GET /activities/{activity_id}` — fetch one activity by ID for the authenticated enterprise
- `PUT /activities/{activity_id}` — update an activity owned by the enterprise
- `DELETE /activities/{activity_id}` — delete an activity owned by the enterprise

#### Subsystem 3 — Analytics Dashboard & AI Advisory

`backend/app/analytics/router.py` exposes:

- `GET /analytics/summary` — aggregate enterprise emissions by category and period
- `GET /analytics/trends` — return monthly trend data for the enterprise

`backend/app/analytics/ai_router.py` exposes:

- `POST /ai/recommendations` — generate reduction recommendations for the authenticated enterprise

#### Service health

- `GET /health` — returns application health status

### MongoDB persistence implementation

The database access layer is implemented with MongoDB-backed service objects rather than an in-memory store.

- `backend/app/mongo_store.py` defines `MongoStore`, which connects to MongoDB and manages the `users`, `enterprises`, and `departments` collections.
- The constructor creates unique indexes for `email`, `enterprise_id`, and `department_id` and adds an `enterprise_id` index for department queries.
- `create_enterprise()`, `get_user_by_email()`, `get_enterprise()`, `update_enterprise()`, `list_departments()`, and `create_department()` are the persistence methods used by Subsystem 1 routes.
- `backend/app/store.py` imports and instantiates `MongoStore` as `store`, which is the object used by the authentication and enterprise API layer.
- `backend/app/activities/mongo_repository.py` defines `MongoActivityRepository`, which manages the `activity_records` collection and supports create, list, fetch-by-id, update, and delete operations keyed by `enterprise_id` and `id`.
- The repository creates unique and filtered indexes to support enterprise-scoped queries and chronological retrieval of activity data.

### How the API routes interact with the database layer

The backend routes are intentionally thin and delegate persistence to the database access objects:

- Subsystem 1 routes in `backend/app/routes.py` call `store.get_user_by_email()`, `store.create_enterprise()`, `store.get_enterprise()`, `store.update_enterprise()`, `store.list_departments()`, and `store.create_department()`.
- Subsystem 2 routes in `backend/app/activities/router.py` validate and calculate the activity payload, then pass the result to `activity_repository.create()`, `get_all()`, `get_by_id()`, `update()`, and `delete()`.
- Subsystem 3 analytics routes do not bypass the repository layer: `backend/app/analytics/service.py` uses `activity_repository.collection.aggregate(...)` to calculate summaries and trends, while the AI advisor also reads enterprise data via `store.get_enterprise()`.

---

## Hometask 4 — Error Handling & Automated Testing

**Submission branch:** `HomeworkAssignment4`. Python backend: **FastAPI + MongoDB**. Automated testing: **pytest + mongomock**.

### Subsystem 1 — Authentication & Enterprise Management

- Custom exception classes: `backend/app/exceptions.py` — `Subsystem1Error`, `EmailAlreadyRegisteredError`, `EnterpriseNotFoundError`.
- HTTP errors: `backend/app/routes.py` maps duplicate registrations to **409 Conflict** and missing enterprises to **404 Not Found**.
- Tests: `backend/tests/test_subsystem1_exceptions.py` — **6 tests**.

### Subsystem 2 — Carbon Activity Management & Calculation Engine

**Implemented by Oscar Daniel de la Cruz Jara.**


- Custom exception classes: `backend/app/activities/exceptions.py`.
  - `Subsystem2Error`: base application exception (subclass of `ValueError` to preserve compatibility).
  - `InvalidActivityError`: missing or invalid fields, non-positive/non-finite amounts or factors, and mismatched units.
  - `EmissionFactorNotFoundError`: unknown emission categories or activity types.
  - `ActivityNotFoundError`: a record does not exist (or is not accessible to the requesting enterprise).
- Error handling in `backend/app/activities/oop.py`: validation and factor lookup raise specific domain exceptions, retaining their prior messages.
- HTTP mapping in `backend/app/activities/router.py`: invalid activity data yields **422 Unprocessable Entity** and missing activities yield **404 Not Found**.
- Test module: `backend/tests/test_subsystem2_exceptions.py`. **15 pytest test cases** (13 test functions, including 3 parameterized invalid amounts), covering exception inheritance, invalid input and unit handling, missing factors, valid calculation, HTTP error mapping, activity creation, and enterprise data isolation.

### Run Hometask 4 Tests

From the `backend/` directory, install development dependencies and run:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest tests/test_subsystem1_exceptions.py tests/test_subsystem2_exceptions.py -v
```

The two Hometask 4 modules define **21 test cases** in total (6 for Subsystem 1 and 15 for Subsystem 2). These are defined cases, not a claim of a verified passing run. The tests use MongoMock and mocked persistence methods to avoid modifying production data.

**Team completion note:** Each remaining subsystem should add its own custom error-handling class, integrate it into the application, and contribute tests as required by the instructor. Existing Subsystem 2 OOP and repository tests can also be run as regression checks.


---
