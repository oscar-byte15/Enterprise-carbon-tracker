# Copilot instructions for Enterprise Carbon Tracker

## Project shape
- This repo is a small two-part app: a FastAPI backend in `backend/` and a Vite React frontend in `frontend/`.
- The backend is intentionally modularized around the carbon activity domain: `backend/app/activities/router.py` exposes the `/activities` API, `calculator.py` performs validation + CO2e math, and `emission_factors.json` is the source of truth for category/type/unit factors.
- The frontend is a feature-based React app under `frontend/src/features/activities/`; `App.jsx` mounts `ActivitiesLayout`, which swaps between `NewActivity`, `ActivityHistory`, and `EditActivity` using local page state (`activePage`, `selectedActivity`).
- The current app is a demo/local-state workflow: data is saved in browser `localStorage` via `frontend/src/features/activities/services/activityStorage.js`; it is not yet wired to the FastAPI backend.

## Key data flow
- `ActivityForm` creates a payload with `{ category, type, amount, unit, date, period }` and persists it via `saveActivity()`.
- `ActivityHistory` reads from `localStorage`, filters by category/search term, and forwards an activity to `EditActivity` through `onEdit`.
- `EditActivity` updates local storage through `updateActivity(id, updatedData)` and then notifies the layout via `onSaved()`.
- On the backend, `ActivityCreate` in `backend/app/activities/schemas.py` validates input; `router.py` calls `calculate_emissions()` and returns `co2e_kg`, `emission_factor`, and `factor_source`.

## Domain conventions that matter
- Activity categories are strict: `electricity`, `heating`, `transport`, `waste`.
- Matching activity types and units are defined in both the frontend `activityTypes`/`units` maps and the backend `emission_factors.json` file. If you add a new type, update both sides and keep the unit consistent.
- The backend uses `Decimal` for financial-style numeric safety, then rounds to 2 decimal places in `calculator.py` using `ROUND_HALF_UP`.
- The demo factor file explicitly says “Demo factor - replace before production”; treat it as a placeholder, not a complete emissions data source.

## Working commands
- Backend: from `backend/`, run `python -m uvicorn app.activities.dev_main:app --reload`.
- Health check: `GET /health` is defined in `backend/app/activities/dev_main.py`.
- Frontend: from `frontend/`, run `npm install` once, then `npm run dev`.
- Build: `npm run build` from `frontend/`.
- Lint: `npm run lint` from `frontend/`.
- Python dependencies are listed in `backend/requirements.txt`; install them in the backend environment before testing the API.

## Coding patterns to follow
- Keep feature code in the existing folder structure: `components/`, `pages/`, `services/` under `frontend/src/features/activities`.
- Prefer props-driven callbacks (`onSubmit`, `onSaved`, `onNavigate`, `onEdit`) rather than adding a centralized store or route library.
- When modifying the activity schema, preserve the current naming conventions: `category`, `type`, `amount`, `unit`, `date`, `period`.
- For API changes, update both the Pydantic model and the FastAPI response contract; the app currently keeps those tightly aligned.

## What to avoid
- Do not assume backend persistence exists; the current frontend is localStorage-based unless explicitly wired to the API.
- Do not add unsupported category/type combinations without updating `emission_factors.json` and the corresponding frontend select options.
- Do not introduce a new framework or routing pattern for this feature without checking the existing single-layout structure in `ActivitiesLayout.jsx`.
