# Enterprise Carbon Footprint Tracker & AI Assistant

**FH Dortmund — Master Digital Transformation**  
**Compact Programming Course — Hometask Assignments**

## 🎥 Project Video Presentation

**[▶ Hometask 1 – Object-Oriented Programming (OOP)](https://drive.google.com/file/d/1KW9YBkFFk_YKnRE3nSJbLDVhMkl2JuRP/view)**
This video presents the OOP design in our Enterprise Carbon Footprint Tracker & AI Assistant project, including the implementation and architecture of its three subsystems.

**▶ [Hometask 3 – Web APIs & Database Access Layers](https://drive.google.com/file/d/1xFejjy9W8Rf-03NgcsOqctBE6gSU-yPN/view?usp=drive_link)**
This video demonstrates our FastAPI endpoints, MongoDB integration, and database access layer implementation.

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


| Team Member | Matriculation Number (Matrikelnummer) | Assigned Subsystem | Implementation |
|---|---|---|---|
| Xiangping Kong | 7226940 | Subsystem 1 — Authentication & Enterprise Management | [Three OOP classes (User, Enterprise, Department), UML and unit tests](#subsystem-1--user-authentication--enterprise-management-oop-implementation) |
| Oscar Daniel de la Cruz Jara | 7226240 | Subsystem 2 — Carbon Activity Management & Calculation Engine | [Three OOP classes (ActivityRecord, EmissionFactor, CalculationService) and UML](#subsystem-2--carbon-activity-management--calculation-engine) |
| Usama Rasheed | 7227033 | Subsystem 3 — Analytics Dashboard & AI Advisory | [Three OOP classes (EmissionMetric, AnalyticsEngine, SustainabilityAdvisor), UML and unit tests](#subsystem-3--analytics-dashboard--ai-advisory-oop-implementation) |

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

This subsystem manages enterprise carbon activity data, emission factor configurations, and CO2e calculations. Three OOP classes implement the domain model and are used by the existing FastAPI activity creation and update pipeline.

#### Three Implemented Classes

| **Class** | **Responsibility** | **Constructor** | **Encapsulation / Relationships** |
| --------- | ------------------ | --------------- | --------------------------------- |
| `ActivityRecord` | Represents an enterprise carbon activity, storing its category, activity type, consumption amount, unit, date, and enterprise ID. | `__init__(category, activity_type, amount, unit, activity_date, enterprise_id)` | **Encapsulation:** underscore-prefixed attributes with validated getters and setters; `get_period()` derives the reporting period. **Dependency:** supplied to `CalculationService` for calculation. |
| `EmissionFactor` | Represents a conversion factor associated with an activity category, activity type, unit, and source. | `__init__(category, activity_type, factor, unit, source)` | **Encapsulation:** validated getters and setters. **Composition:** created and owned by `CalculationService`; `matches(activity)` checks category, activity type, and unit. |
| `CalculationService` | Loads the factor catalog, validates units, and calculates CO2e emissions using activity data. | `__init__(factor_catalog=None)` | **Composition:** owns multiple `EmissionFactor` objects. **Dependency:** uses `ActivityRecord` in `calculate(activity)`. Catalog access is encapsulated through getters/setters; results are rounded to two decimals. |

#### Mapping to Capstone Subsystem 2 Architecture

- **`ActivityRecord`:** Represents the validated activity data submitted through `POST /activities/` or `PUT /activities/{activity_id}`. Its fields are used for emission calculation and eventual database persistence.
- **`EmissionFactor`:** Represents a configured conversion factor used to convert a specific activity amount into CO2e; the factor catalog is loaded from `backend/app/activities/emission_factors.json`.
- **`CalculationService`:** Performs category/type lookup, unit validation, and CO2e calculations before the API writes the prepared activity to MongoDB through `MongoActivityRepository`.

#### OOP Concepts Applied

- **Constructors:** All three classes use `__init__()` for initialization and configuration.
- **Encapsulation:** Underscore-prefixed attributes are accessed and updated using getter and setter methods, including validation.
- **Data validation:** `ActivityRecord.set_amount()` rejects non-numeric, non-finite, and non-positive amounts; `EmissionFactor.set_factor()` rejects negative or non-finite factors.
- **Composition:** `CalculationService` creates and owns its `EmissionFactor` instances based on the factor catalog.
- **Object collaboration:** `CalculationService.calculate(activity)` uses an `ActivityRecord` and its matching `EmissionFactor` to calculate CO2e, rounding the result to two decimal places.

**Implementation note:** The OOP classes are integrated into the existing FastAPI create/update flow in `backend/app/activities/router.py`. MongoDB persistence remains encapsulated in `backend/app/activities/mongo_repository.py`.

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
