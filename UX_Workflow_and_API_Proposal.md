# Enterprise Carbon Footprint Tracker — UX and API Proposal

**Status:** Team discussion draft, not approved implementation. Based on the team's 13 October 2026 capstone slides. The interface adds proposed navigation and behaviors beyond the presentation.

## Ownership and screens

| Owner | Screen | Main user actions | Next screens |
|---|---|---|---|
| Xiangping — Subsystem 1 | Login | Enter credentials; sign in; open registration | Dashboard; Register |
| Xiangping | Register / onboarding | Enter email, password, enterprise name and industry | Dashboard |
| Xiangping | Enterprise profile | View and edit company metadata | Dashboard; Departments |
| Xiangping | Departments | Add optional departments | Enterprise profile |
| Usama — Subsystem 3 | Dashboard | View totals, navigate to activity capture, analytics, profile | Activity form; History; Analytics; Profile |
| Oscar — Subsystem 2 | New carbon activity | Select category/type, enter positive amount, period and date, calculate/save | Activity history; validation error stays on form |
| Oscar | Activity history | Filter by category/period, view values, edit/delete | Edit activity; New activity; Analytics |
| Oscar | Edit activity | Change values, recalculate with matching factor, save/cancel | Activity history |
| Usama | Analytics | Filter by month/year, view totals, category shares and monthly trend | AI recommendations; History |
| Usama | AI coach | Request contextual advice, view loading/error/fallback | Analytics |

## Primary user journeys

1. **First use:** Register admin → create enterprise profile → Dashboard → New activity → calculate → save → History → Analytics → AI recommendations.
2. **Returning user:** Login → Dashboard → History → filter → Edit → recalculate and save → Dashboard.
3. **Data correction:** History → Delete → confirmation → History refreshed.
4. **Company settings:** Dashboard → Enterprise profile → update metadata → optionally manage departments → Dashboard.
5. **Validation:** Create/Edit → enter zero/negative amount, unknown type or wrong unit → show field error, do not persist.
6. **API failure:** Any write/read → show actionable error and retain form values; AI unavailable → fallback recommendations, clearly labeled.
7. **Session expiry:** Any protected screen → token expired → Login; preserve unsaved work where feasible.

## Contract to agree before parallel coding

- **Identity:** Subsystem 1 verifies JWT and exposes `enterprise_id` to protected endpoints; never accept tenant ID from arbitrary client input.
- **Record:** `_id`, `enterprise_id`, `category`, `type`, `amount`, `unit`, `period` (YYYY-MM), `date`, `factor_used`, `factor_source`, `calculated_co2e`; optionally source year and factor version.
- **Factor lookup:** JSON keyed by category, type and unit, including value, source and year. Exact units must match.
- **Write:** `POST /activities` and `PUT /activities/{id}` validate, calculate and save atomically; `DELETE /activities/{id}` checks ownership.
- **Read:** `GET /activities?period=YYYY-MM&category=...` and `GET /activities/{id}` are tenant-scoped. Define pagination before coding if needed.
- **Analytics:** Agree whether Usama uses the tenant-scoped activity endpoint or a dedicated aggregation endpoint (`GET /analytics/summary?period=...`).
- **Numbers:** Use decimal-safe calculation and explicit rounding to two decimal places; retain factor and provenance in every record.
- **Errors:** Agree 400/422 validation, 401 unauthenticated, 403 unauthorized, 404 missing resource, 500 service failure.
- **Security:** JWT protected routes, server-side secrets, hashed passwords, tenant-scoped database queries.
- **Testing:** Positive calculations, zero/negative inputs, unknown factor/unit, cross-enterprise access, CRUD behavior, filtering, dashboard aggregation, AI fallback.

## Screen-state checklist

For each screen design: default, loading, empty, successful action, invalid input, server error, and permission denied where relevant. Confirm desktop/mobile behavior and accessibility labels.

## Important distinctions

- The provided presentation specifies **Gemini** for AI advice, while the professor's capstone checklist explicitly says **OpenAI**. The team should clarify with the professor whether Gemini satisfies the assessment requirement before committing to that integration.
- The interactive HTML prototype uses invented demo records and **illustrative emission factors only**; it performs no verified emissions reporting, real authentication, API requests, or persistent storage.
- The slide deck contains initial prototypes for enterprise profile, new activity, activity history and dashboard. Login, registration, editing, departments, filters, error states and AI advice screens are proposed expansions to make the workflow testable.
- Submission requirements include GitHub repo, README, requirements file, seven-minute screencast, presentation, tests and Docker. The stated final upload deadline is **13 November 2026**.

## Team review agenda (45 minutes)

1. Walk through first-use journey (10 min).
2. Confirm screen ownership and navigation (10 min).
3. Approve field names, JSON and endpoints (15 min).
4. Agree on AI provider and real factor sources (5 min).
5. Assign integration tasks and next check-in (5 min).
