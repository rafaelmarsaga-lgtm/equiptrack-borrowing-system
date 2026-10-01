# EquipTrack: Campus Equipment Borrowing System — Requirements Analysis & Plan

> On approval this is saved as `docs/PLAN.md` (Step 1 setup commit). No code is written until you say "Proceed to Step 1".
> Decisions confirmed with Rafael: staff can **add** equipment; returns are **whole-record only**; Staff list has a **status filter**.
> Revision 2 (Rafael's review): LIKE wildcards escaped in search; past-due seed record inserted via ORM; Step 7 is mandatory; Step 9 fills `docs/DOCUMENTATION_TEMPLATE.md`.

## 1. Problem
The department records equipment borrowing by hand. Students and faculty can't tell what is available. Staff can't easily see what is out, what came back, and what is late.

**Target users:** students and faculty (check availability, borrow); department staff (add equipment, record returns, track status). No login (stated simplification). Two tabs: **Borrow** and **Staff**.

## 2. Functional requirements
- FR1. The system shall list all equipment with name, category, total quantity and **available quantity**.
- FR2. The system shall search equipment by name (case-insensitive, partial) and filter by category.
- FR3. The system shall let staff add equipment (name, category, total quantity).
- FR4. The system shall reject a duplicate equipment name (case-insensitive).
- FR5. The system shall record a borrow with borrower name, ID number, borrower type, equipment, quantity and due date.
- FR6. The system shall reject a borrow whose quantity exceeds the available quantity.
- FR7. The system shall reject a due date earlier than today or more than 14 days ahead.
- FR8. The system shall let staff mark a Borrowed record as Returned and store the return date.
- FR9. The system shall reject returning a record that is already Returned.
- FR10. The system shall show each transaction's status (Borrowed, Returned or Overdue) and let staff filter by status.
- FR11. The system shall compute available quantity and Overdue status at read time. Neither is stored.
- FR12. The system shall validate all input on the server and show friendly messages in the UI.

## 3. Required inputs
| Field | Type | Rules |
|---|---|---|
| Equipment name | text | 2–60 chars (trimmed), unique case-insensitive |
| Category | enum | Laptop, Projector, Camera, Audio, Networking, Others |
| Total quantity | integer | 1–100 |
| Borrower full name | text | 2–100 chars (trimmed) |
| ID number | text | 4–20 chars, letters/digits/dashes only |
| Borrower type | enum | Student, Faculty |
| Equipment | integer id | must exist |
| Borrow quantity | integer | ≥ 1 and ≤ available |
| Due date | date | today (PH) to today+14 days |
| Search / filters | query strings | optional: `search`, `category`, `status` |

## 4. Expected outputs
- Inventory table: name, category, total, available, with an "Out of stock" badge at 0.
- Confirmation after a borrow (record id, due date) and the updated availability.
- Transactions table: borrower, ID, type, equipment, qty, borrowed on, due, returned on, status badge (Borrowed / Returned / Overdue).
- Friendly error messages (`{"detail": "..."}`), plus loading, empty and error states.

## 5. The three features (Input → Processing → Output)
**Feature 1: Equipment inventory (Objective 1)**
- Input: optional `search` text, optional `category`; staff add-equipment form.
- Processing: query equipment, compute `available = total − SUM(qty of unreturned borrows)`, apply case-insensitive name search and category filter. The search text is escaped (`%`, `_` and the escape character itself) and used in `LIKE ... ESCAPE ''`, so typing `%` matches only names that contain a literal `%`. Adding checks the unique name (409).
- Output: the list with live available counts.

**Feature 2: Borrow equipment (Objective 2)**
- Input: name, ID number, type, equipment, quantity, due date.
- Processing: validate fields, check the equipment exists (404), check the due date window, check `quantity ≤ available` (400), then store the record with `borrow_date = today (PH)`.
- Output: a confirmation, and the inventory refreshes with reduced availability.

**Feature 3: Return and track (Objective 3)**
- Input: the borrow record id (Return button) and an optional status filter.
- Processing: reject if already returned (400) or not found (404). Set `return_date = today (PH)`. Compute each record's status: Returned if `return_date` is set, Overdue if unreturned and `due_date < today`, otherwise Borrowed.
- Output: the updated transactions list with status badges, and availability restored.

## 6. Tools and technologies (Kit A)
| Tool | Why |
|---|---|
| Python 3.11 + FastAPI | Short route code, automatic validation, serves the static frontend (one origin, no CORS). |
| Pydantic | Declares field rules once. A custom handler turns 422s into friendly text. |
| SQLAlchemy + SQLite | Borrow records must be stored and shared between users. A single local file needs no server. |
| HTML + vanilla JS (fetch) | No build step, so it's easy to read and explain. |
| Tailwind via CDN | Responsive styling with no tooling. |
| pytest + TestClient (in-memory SQLite) | Fast tests that never touch the real `.db` file. |

## 7. Data model
**equipment**: `id` PK · `name` (stored trimmed) · `name_key` (lowercase, **UNIQUE**, backs the case-insensitive rule) · `category` · `total_quantity` · `created_at`
**borrow_records**: `id` PK · `equipment_id` FK→equipment · `borrower_name` · `id_number` · `borrower_type` · `quantity` · `borrow_date` (date) · `due_date` (date) · `return_date` (date, NULL until returned)

Relationship: one equipment has many borrow records. Derived, **not stored**: `available`, `status`. Why: stored copies can go stale, and computing them can't drift.

`today_ph()` is the single time helper (UTC+8 fixed), used for the due-date window, `borrow_date`, `return_date` and Overdue.

## 8. API endpoints
| Method & path | Purpose | Success | Errors |
|---|---|---|---|
| GET `/api/equipment?search=&category=` | List with `available` | 200 | 422 bad category |
| POST `/api/equipment` | Add equipment | 201 | 409 duplicate, 422 invalid |
| POST `/api/borrows` | Record a borrow | 201 | 400 over-available, 404 no equipment, 422 invalid |
| GET `/api/borrows?status=` | List transactions with computed status | 200 | 422 bad status |
| POST `/api/borrows/{id}/return` | Mark returned | 200 | 400 already returned, 404 not found |
| GET `/` | Static frontend | 200 | none |

## 9. Validation table
| Input | Rule | Code | Friendly message |
|---|---|---|---|
| Equipment name | 2–60 chars after trim | 422 | "Equipment name must be 2 to 60 characters." |
| Equipment name | unique, case-insensitive | 409 | "That equipment already exists." |
| Category | one of the six | 422 | "Choose a valid category." |
| Total quantity | integer 1–100 | 422 | "Total quantity must be a whole number from 1 to 100." |
| Borrower name | 2–100 chars after trim | 422 | "Full name must be 2 to 100 characters." |
| ID number | 4–20, `[A-Za-z0-9-]` | 422 | "ID number must be 4 to 20 letters, digits or dashes." |
| Borrower type | Student / Faculty | 422 | "Select Student or Faculty." |
| Equipment id | exists | 404 | "Equipment not found." |
| Quantity | integer ≥ 1 | 422 | "Quantity must be at least 1." |
| Quantity | ≤ available | 400 | "Only N available; you asked for M." |
| Due date | valid date | 422 | "Enter a valid due date." |
| Due date | today ≤ date ≤ today+14 | 400 | "Due date must be between today and 14 days from today." |
| Return record id | exists | 404 | "Borrow record not found." |
| Return | not already returned | 400 | "This item was already returned." |
| Any 422 incl. nested fields | handler rewrites Pydantic text | 422 | Always `{"detail": "<friendly message>"}` |

## 10. Objective → feature → step map
| Objective | Feature | Built in |
|---|---|---|
| 1. Inventory with real-time availability, search, category filter | Feature 1 | Step 3 (UI shell in Step 2) |
| 2. Record borrows with all fields; prevent over-borrowing | Feature 2 | Step 4 (field rules hardened in Step 6) |
| 3. Record returns; track Borrowed / Returned / Overdue | Feature 3 | Step 5 |

## 11. Steps
**Time plan (~1 h 20 min build):** S1 10 · S2 15 · S3 12 · S4 12 · S5 12 · S6 10 · S7 reserved/5 · S8 8 · S9 6. Each step stops for your "Proceed to Step N".

### Step 1: Initial project setup — commit `Initial project setup: ...`
- Build: folder tree from CLAUDE.md, `.gitignore` (`.db`, `.venv`, `__pycache__`, `.pytest_cache`), `requirements.txt` (fastapi, uvicorn, sqlalchemy, pydantic, pytest, httpx), `database.py` (`DATABASE_URL` env, StaticPool for `sqlite://`), models, `main.py` with lifespan + `GET /api/health` + static mount, `today_ph()` helper with a test, `conftest.py` setting `DATABASE_URL=sqlite://` before import, `docs/PLAN.md`, README stub, `git init` on `main`.
- Verify: `python -m pytest -v` passes. Uvicorn starts and `curl /api/health` returns 200. `git status` shows no `.db`/venv.

### Step 2: Create application interface — commit `Create application interface: ...`
- Build: `index.html` with a Borrow tab (inventory table, search, category dropdown, borrow form) and a Staff tab (add-equipment form, status filter, transactions table). Tailwind CDN, `js/api.js`, `js/ui.js`, `js/app.js`. Loading, empty and error states, responsive layout. `textContent` only. Static data or stub calls only, since the endpoints don't exist yet.
- Verify: open in the Browser pane at desktop and mobile widths. Tabs switch, forms render, no console errors.

### Step 3: Implement core functionality, Feature 1 (inventory) — TDD
- Build: tests first for `available_quantity`, GET `/api/equipment` (search, category), a wildcard test (`search=%` returns only the item whose name contains a literal `%`, and `search=_` likewise), POST `/api/equipment` (201, 409 case-insensitive). Then implement the service (with an `escape_like()` helper) and router, `seed_data.py` (about 8 equipment items) and wire the UI.
- Verify: tests red, then green. In the UI, search "lap" and filter "Camera"; search "%" shows no match (empty state) instead of everything; add an item and see it appear; adding "laptop" twice shows a 409 message.

### Step 4: Implement core functionality, Feature 2 (borrow) — TDD
- Build: tests first for a successful borrow (201, available drops), over-available (400), unknown equipment (404), borrow exactly the available amount (OK, then 0 left), and a returned record not counting against availability. Then implement the service and router and wire the form. Pydantic schema field rules stay minimal here.
- Verify: tests green. In the UI, borrowing reduces the available count live. Borrowing more than available shows the error.

### Step 5: Implement core functionality, Feature 3 (return and status) — TDD
- Build: tests first for `compute_status` (Borrowed, Returned, Overdue; due today is NOT overdue, due yesterday is overdue), return success (200, restores availability), double return (400), return 404, and the `?status=` filter. Then implement and wire the Return button, status badges and filter.
- Seed note: `seed_data.py` inserts one past-due Borrowed record **directly through the ORM** as historical data, not through the API, because the API rightly rejects past due dates. A comment in the script says so. Verify: tests green (the Overdue test also inserts through the ORM). Run the seed and see the Overdue badge. Return it, and availability goes up and the badge becomes Returned.

### Step 6: Add input validation — commit `Add input validation: ...`
- Build: full Pydantic rules from §9 (trim, lengths, ID regex, quantity and total ranges, enums, due-date window using `today_ph()`), the `RequestValidationError` handler giving friendly `{"detail"}` for every 422 including nested paths, matching client-side checks with inline messages, and disabling the submit button while a request is in flight. Tests: one per row of the §9 table.
- Verify: tests green. Try empty form, 1-char name, ID `ab!`, quantity 0, due date yesterday and +15 days. Each shows a friendly message and never raw Pydantic text.

### Step 7: Fix application error — commit `Fix application error: ...` (REQUIRED)
- We fix the **first real error** we hit in Steps 1–6 (a failing test that exposes a genuine bug, a crash, or a wrong UI result). We use `systematic-debugging`: reproduce, find the root cause, add a regression test, then fix. Candidates, not promises: `no such table` without `with TestClient(app)`, date-boundary mistakes in Overdue/due-date logic. Never invented. I'll log each real error as it happens in `docs/AI_LOG.md`, and its fix waits for this step's commit.
- If no real error has appeared by the end of Step 6, I report **every gap the Step 6 checks find** (each validation row, each edge case that behaves wrongly), and you choose a real one to fix in its own commit.
- Verify: the failing case is reproduced first, and the regression test passes after the fix.

### Step 8: Refactor application code — commit `Refactor application code: ...`
- Build: move any business logic left in routers into `services/` (availability, borrow, return, status), remove duplicated JS, rename unclear names, add why-comments. Behavior must not change.
- Verify: the full suite is green before and after, and the UI smoke test is unchanged.

### Step 9: Update documentation — commit `Update documentation: ...`
- Build: read `docs/DOCUMENTATION_TEMPLATE.md`, fill it in and save it as `docs/DOCUMENTATION.md`. It covers the requirements analysis (from this plan) and the AI section with prompt / AI response / evaluation / modifications for planning, code generation, debugging, refactoring and documentation, drawn from `docs/AI_LOG.md`. The GitHub section includes the real `git log --oneline` output. Also write `README.md` (setup and run) and `docs/TESTING.md` (test table plus manual demo checks). I keep evaluation and modification text as short drafts for you to rewrite.
- Verify: follow the README on a clean checkout and it runs. Docs match the code, and the `git log --oneline` pasted in is the real output.

*After each step, we append an entry to `docs/AI_LOG.md`, show `git status`, then commit. You push.*

## 12. Edge cases the instructor may try
1. Borrow more than available, exactly available, and quantity 0, negative, or a decimal.
2. Borrow from an item that is already at 0 available.
3. Two borrowers each borrow part of the stock, and the second one exceeds the remainder.
4. Due date yesterday, today (allowed), +14 (allowed), +15 (rejected), or a malformed date.
5. ID number with spaces or symbols, too short, or too long. Name with only spaces.
6. Duplicate equipment name with different case ("laptop" vs "LAPTOP ") or surrounding whitespace.
7. Return the same record twice, return a non-existent id, or return then borrow again (availability restored).
8. Overdue boundary: due today is Borrowed, due yesterday is Overdue. Returned items are never Overdue.
9. Search with no match (empty state), whitespace, mixed case, or `%`/`_`/`'` characters (wildcards must match literally). Category plus search together.
10. HTML in the name (`<script>`) rendered as plain text. The server stops (Ctrl+C) and restarts with data kept. A fresh DB with no equipment.
11. Page refresh mid-form, or two browser tabs where one borrows and the other sees stale availability (the server re-checks at submit).
12. Clock edge: just after midnight in the Philippines (UTC+8) while the server host is in another timezone.

## 13. Verification summary (end to end)
`cd backend` → `python seed_data.py` → `python -m uvicorn app.main:app --reload` → http://127.0.0.1:8000/ and `python -m pytest -v`. Walk the three features plus the edge-case list in the Browser pane.
