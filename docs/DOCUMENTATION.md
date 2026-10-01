# EquipTrack: Campus Equipment Borrowing System

**IT 415 – Application Development and Emerging Technologies**
**Midterm Examination (Performance-Based)** · First Semester, AY 2026–2027
**Student:** Rafael Marsaga · **Date:** October 8, 2026
**GitHub repository:** [REPO URL]

> How this file was written: the facts come from the real project (docs/PLAN.md, docs/AI_LOG.md,
> `git log`, and a real test run). Screenshots are left as `[SCREENSHOT]` placeholders (images can be
> saved in `docs/evidence/`). Every **Evaluation** and **Modifications** entry in section 2 is a short
> draft for Rafael to rewrite in his own words.

---

## 1. Requirements Analysis

### 1.1 Problem to be addressed
A college department records equipment borrowing by hand. Students and faculty members have difficulty
checking whether equipment is available, and staff members have difficulty tracking which items are
borrowed, returned, or late. This matters because people waste trips to an equipment room that may have
nothing left, and items that are not returned on time go unnoticed.

**General objective**
To develop a web-based equipment borrowing system that allows students and faculty members to check equipment availability and borrow equipment, and allows department staff to record and track borrowed and returned items.

**Specific objectives**
1. To provide an equipment inventory that shows the available quantity of each item in real time, with search by name and filter by category.
2. To record borrowing transactions with the borrower's name, ID number, borrower type, equipment, quantity, and due date, while preventing borrowing of more items than are available.
3. To allow staff to record returned equipment and track each transaction's status (Borrowed, Returned, or Overdue).

### 1.2 Target users
| User | What they need from the system |
|------|-------------------------------|
| Students and faculty (borrowers) | See what equipment exists and how many are available right now; search and filter; borrow an item with a due date |
| Department staff | Add equipment to the inventory; record that an item came back; see every borrow record and which ones are Borrowed, Returned or Overdue |

There is no login. This is a stated simplification for the exam: the app has a **Borrow** tab and a **Staff** tab.

### 1.3 Functional requirements
1. The system shall list all equipment with name, category, total quantity and available quantity.
2. The system shall search equipment by name (case-insensitive, partial) and filter by category.
3. The system shall let staff add equipment (name, category, total quantity).
4. The system shall reject a duplicate equipment name (case-insensitive).
5. The system shall record a borrow with borrower name, ID number, borrower type, equipment, quantity and due date.
6. The system shall reject a borrow whose quantity exceeds the available quantity.
7. The system shall reject a due date earlier than today or more than 14 days ahead.
8. The system shall let staff mark a Borrowed record as Returned and store the return date.
9. The system shall reject returning a record that is already Returned.
10. The system shall show each transaction's status (Borrowed, Returned or Overdue) and let staff filter by status.
11. The system shall compute available quantity and Overdue status when they are read. Neither is stored.
12. The system shall validate all input on the server and show friendly messages in the interface.

### 1.4 Required inputs
| Input | Type | Rules |
|-------|------|-------|
| Equipment name | text | 2–60 characters after trimming; unique, ignoring case |
| Category | choice | Laptop, Projector, Camera, Audio, Networking, Others |
| Total quantity | whole number | 1–100 |
| Borrower full name | text | 2–100 characters after trimming |
| ID number | text | 4–20 characters; letters, digits and dashes only |
| Borrower type | choice | Student or Faculty |
| Equipment | id | must exist |
| Borrow quantity | whole number | at least 1, and no more than the available quantity |
| Due date | date | from today up to 14 days ahead (Philippine time) |
| Search, category filter, status filter | text / choice | optional |

### 1.5 Expected outputs
- An inventory table: name, category, total, available, with an "Out of stock" badge when none are left.
- A confirmation after a borrow (record number, quantity, equipment, due date) and an updated inventory.
- A borrow-records table: borrower, ID number, type, equipment, quantity, borrowed on, due, returned on, status badge, Return button.
- Friendly error messages (always as `{"detail": "..."}` from the server), plus loading, empty and error states.

### 1.6 Proposed application features
| Feature | Input | Processing | Output |
|---------|-------|------------|--------|
| 1. Equipment inventory | Optional search text and category; staff add-equipment form | Compute `available = total − quantity of unreturned borrows`; case-insensitive partial name search with `%` and `_` escaped; category filter; reject duplicate names (409) | The equipment list with live available counts |
| 2. Borrow equipment | Name, ID number, borrower type, equipment, quantity, due date | Validate fields; check the equipment exists (404); check the due-date window (400); check quantity ≤ available (400); save with `borrow_date` = today (PH) | A confirmation, and the inventory refreshes with the reduced count |
| 3. Return and track | The Return button on a record; a status filter | Reject if not found (404) or already returned (400); set `return_date` = today (PH); compute each status (Returned if a return date exists; Overdue if unreturned and due before today; otherwise Borrowed) | The updated records table with status badges; availability is restored |

**How the objectives are met**
| Objective | Feature |
|-----------|---------|
| 1. Inventory with real-time availability, search, category filter | Feature 1 |
| 2. Record borrows with all fields; prevent over-borrowing | Feature 2 |
| 3. Record returns; track Borrowed, Returned and Overdue | Feature 3 |

### 1.7 Development tools and technologies
| Area | Tool / technology | Why |
|------|-------------------|-----|
| Frontend | HTML, vanilla JavaScript (fetch), Tailwind CSS via CDN | No build step, easy to read and explain; the server serves it as static files from one origin, so no CORS setup |
| Backend | Python 3.12 (3.11+ required), FastAPI, Pydantic, uvicorn | Short endpoint code, built-in validation, automatic API docs |
| Database | SQLite through SQLAlchemy | Borrow records must be stored and shared between users; a single local file needs no database server |
| Testing | pytest with FastAPI's TestClient on in-memory SQLite | Fast tests that never touch the real database file |
| Version control | Git + GitHub | Required; tracks development history |
| AI tools | Claude Code (desktop app) with Superpowers, UI UX Pro Max, Frontend Design | Planning, test-driven coding, debugging, UI design guidance |

Versions used when this was built and tested: Python 3.12.10, FastAPI 0.141.1, uvicorn 0.53.0,
SQLAlchemy 2.0.54, Pydantic 2.13.5, pytest 9.1.1, httpx 0.28.1.

### 1.8 Data model
| Table | Columns |
|-------|---------|
| `equipment` | `id`, `name`, `name_key` (lowercase copy of the name, **unique**), `category`, `total_quantity`, `created_at` |
| `borrow_records` | `id`, `equipment_id` (links to equipment), `borrower_name`, `id_number`, `borrower_type`, `quantity`, `borrow_date`, `due_date`, `return_date` (empty until returned) |

Not stored on purpose: `available` and `status`. They are calculated whenever they are shown.

### 1.9 Validation rules and messages
| Input | Rule | Status | Message shown |
|-------|------|--------|---------------|
| Equipment name | 2–60 characters after trimming | 422 | Equipment name must be 2 to 60 characters. |
| Equipment name | unique, ignoring case | 409 | That equipment already exists. |
| Category | one of the six | 422 | Choose a valid category. |
| Total quantity | whole number 1–100 | 422 | Total quantity must be a whole number from 1 to 100. |
| Borrower name | 2–100 characters after trimming | 422 | Full name must be 2 to 100 characters. |
| ID number | 4–20 letters, digits or dashes | 422 | ID number must be 4 to 20 letters, digits or dashes. |
| Borrower type | Student or Faculty | 422 | Select Student or Faculty. |
| Equipment | must exist | 404 | Equipment not found. |
| Quantity | whole number, at least 1 | 422 | Quantity must be at least 1. (for 0 or negative) / Quantity must be a whole number of at least 1. (for 1.5 or text) |
| Quantity | not more than available | 400 | Only N available; you asked for M. |
| Due date | a valid date | 422 | Enter a valid due date. |
| Due date | today to today + 14 days | 400 | Due date must be between today and 14 days from today. |
| Return | record must exist | 404 | Borrow record not found. |
| Return | not already returned | 400 | This item was already returned. |
| Any other 422 | friendly text, never Pydantic's wording | 422 | Please check your entries and try again. |

The one place the final messages differ from docs/PLAN.md: the plan used a single message for quantity;
a value like 1.5 is not "less than 1", so it gets the second wording above.

### 1.10 API endpoints
| Method and path | Purpose | Errors |
|-----------------|---------|--------|
| `GET /api/equipment?search=&category=` | List equipment with available quantity | none |
| `POST /api/equipment` | Add equipment | 409, 422 |
| `POST /api/borrows` | Record a borrow | 400, 404, 422 |
| `GET /api/borrows?status=` | List records with computed status | none |
| `POST /api/borrows/{id}/return` | Mark returned | 400, 404 |
| `GET /api/health` | Health check | none |

---

## 2. AI-Assisted Development
For each prompt: (1) the prompt used, (2) the AI-generated response,
(3) my evaluation, (4) the modifications I made.

### 2.1 Planning / requirements analysis
| | |
|---|---|
| **Prompt** | [SCREENSHOT] I gave the instructor's scenario and asked for a requirements analysis and plan before any code: problem, users, "The system shall..." requirements, inputs and outputs, exactly 3 features as Input → Processing → Output, tools, data model, validation table, API, a 9-step plan, and an edge-case list. At most 3 clarifying questions, asked in one batch. |
| **AI response** | [SCREENSHOT] It asked 3 questions (can staff add equipment? whole or partial returns? a status filter?). I chose: staff can add equipment, returns are whole-record only, and the Staff list has a status filter. It then wrote the full plan, saved as docs/PLAN.md. |
| **Evaluation** | (draft) The plan matched the scenario and all three objectives, and gave a way to verify each step. Weak spot: field rules were spread across Steps 3 to 6, which I had to understand before agreeing. |
| **Modifications** | (draft) Before Step 1 I asked for four changes, and the plan was updated: (1) escape `%` and `_` in the search so "%" matches only names containing "%", with a test; (2) insert the past-due seed record directly through the database layer, since the API rejects past due dates; (3) Step 9 must fill the documentation template; (4) Step 7 is required: fix the first real error, or if none appears, report every gap found by the Step 6 checks. |

### 2.2 Application / code generation
| | |
|---|---|
| **Prompt** | [SCREENSHOT] One prompt per step (Steps 1 to 6), each with the objective, requirements and constraints. For the feature steps: write failing tests first and show them failing, then the code, then passing. |
| **AI response** | [SCREENSHOT] Step 1: project skeleton, database models, Philippine-time helper. Step 2: the full interface (design direction "equipment-room logbook"). Steps 3 to 5: the three features, each test-first, with the matching frontend wiring. Step 6: field rules, the due-date window, a friendly-error handler, and inline messages. |
| **Evaluation** | (draft) Each feature step was run before committing: tests shown red then green (suite grew 5 → 19 → 25 → 38 → 120 tests), and each feature was tried in the browser (search, duplicate rejection, borrowing, over-borrowing, returning, status filter). In Step 6 I asked the AI to probe the running app with bad input and report gaps; it found several (listed in docs/TESTING.md). Mistakes the AI made, caught by running things: (a) in Step 3 one of its own tests used `"a\b"`, which Python reads as a backspace character, so the test failed even though the code was right (the test input was corrected); (b) in Step 6 the new due-date rule would have made an older test fail a week later, so that test's setup was changed (its assertions were not). The AI also chose a different message for quantity 1.5 than the plan, and said so. |
| **Modifications** | (draft) I set the limits: "only what this feature needs", keep field rules minimal until Step 6, don't change other features, and in Step 6 "report any gap you find instead of hiding it; don't fix gaps in this step." |

### 2.3 Debugging
| Problem | Prompt | AI response (root cause) | Fix | Test result |
|---------|--------|--------------------------|-----|-------------|
| HTTP 500 Internal Server Error: `OverflowError: Python int too large to convert to SQLite INTEGER` when an id was larger than 9223372036854775807 (also hugely negative ids) | [SCREENSHOT] "Proceed to Step 7. Pick for the error you see." | The ids were plain Python integers with no limit, but SQLite stores ids as signed 64-bit numbers. A larger value passed validation, reached the database call, and the unhandled error became a 500. Found by reading the full stack trace and measuring the exact edge (2^63−1 gave 404, 2^63 gave 500). | A helper `get_by_id()` in `database.py` returns "not found" for an id outside SQLite's range without querying; the borrow service uses it for the equipment id and the return id. The user gets the normal 404. | PASS: 132 passed (12 new tests; 8 of them failed before the fix) |
| A new test failed after the code was written: `assert 'a\x08' == 'a\\b'` (Step 3) | [SCREENSHOT] Step 3 prompt | The mistake was in the test, not the code: `"a\b"` is a backspace character, not a backslash. | Corrected the test input to a real backslash (`"a\\b"`) and kept the same expectation. | PASS: 19 passed |
| The browser ran the old `app.js` after the refactor (Step 8), so the "after" comparison looked identical for the wrong reason | [SCREENSHOT] Step 8 prompt | The browser had cached the old script. A check that the new function existed (`createListLoader`) showed the new code was not running. | Forced a fresh copy and re-ran the comparison. | PASS: identical behaviour on the new code |

**Evaluation:** (draft) The 500 was the only real crash, so it was the one to fix. Two alternatives were rejected:
catching `OverflowError` globally (it hides the cause) and returning 422 for big ids (a second behaviour for
the same idea; the plan already says a non-existent id is 404). While tracing, the AI noticed that SQLite's
range is signed, so hugely negative ids must fail too; it added those tests and watched them fail before the fix.
The replayed requests on the running server all returned 404 and the log showed no `OverflowError`.
**Modifications:** (draft) I let the AI choose the error ("pick for the error you see"), then reviewed the
root cause and the fix.

### 2.4 Refactoring / code improvement
| Before | Prompt | After | Test result |
|--------|--------|-------|-------------|
| `loadInventory()` and `loadRecords()` in `frontend/js/app.js` were the same 28-line routine written twice (request counter, show loading, fetch, empty/table/error, ignore stale responses), with two global counters. | [SCREENSHOT] "Proceed to Step 8... pick the messiest real one and tell me why." | One `createListLoader({area, getQuery, fetchItems, emptyMessage, render})` function that keeps its own counter, plus two short configurations (`loadInventory`, `loadRecords`). | 132 passed before → 132 passed after (backend untouched). The front end was compared with a browser probe: identical result before and after. |

**Why this refactor:** The routers were already thin (they only turn service errors into HTTP codes), so
that candidate was not a real problem. The duplicated loader was: any change to loading behaviour had to be
made twice and kept in sync by hand.
**Evaluation:** (draft) The JavaScript has no automated tests, so a throwaway browser probe recorded what the page
does in normal, filtered, empty, error and loading situations, with both Retry buttons and out-of-order
responses, on the old and the new code: identical (hash 583185767, 1643 characters). A real borrow and return
through the forms also worked. Honest note: `app.js` went from 243 to 239 lines; the gain is one copy of the
logic instead of two, not fewer lines. The two form-submit handlers were left alone because merging them would
be harder to read.
**Modifications:** (draft) Constraints I set: behaviour must not change, don't touch tests, don't rename routes.

### 2.5 Documentation
| | |
|---|---|
| **Prompt** | [SCREENSHOT] Step 9: fill this template, write docs/TESTING.md and the README, describe only what really exists and happened, leave screenshot placeholders, don't invent results. |
| **AI response** | [SCREENSHOT] The README, docs/TESTING.md and this file. The testing table was generated from a real `pytest -v` run: a script checks that every one of the 132 test cases belongs to exactly one row, and takes Actual and Status from the run. |
| **Evaluation** | (draft) Checked by running: the README steps on a clean clone of the repository (no database file, seed, server start, `/` and `/docs` returning 200, 132 tests passing). Corrected before saving: the pytest warning line contained a local file path with a username, so only the message is shown; two manual-check rows claimed slightly more than was observed and were reworded. |
| **Modifications** | What I rewrote in my own words: [Rafael: add]. |

### 2.6 Responsible AI use
- No passwords, API keys, or personal data were put in prompts. [Rafael: confirm]
- Every AI output was read, run, and tested before it was committed (tests shown red then green, the app tried in the browser, `git status` shown before each commit).
- Something I rejected or corrected: [Rafael: add your own example]. Examples that really happened: the plan was changed after my review (section 2.1); the AI's own test mistake (`"a\b"`) was caught by running the tests; and the AI was told to report gaps instead of fixing them in Step 6.

---

## 3. GitHub and Version Control

### 3.1 Workflow used
1. Created an empty repository on GitHub: [REPO URL]
2. `git init -b main` in the project folder (run by Claude Code, so the branch was `main` from the start)
3. After each verified step: `git add -A`, `git status` (shown before committing), then `git commit -m "<stage prefix>: <what changed>"`
4. The GitHub remote `origin` is configured (`git remote -v` shows it); I added it and pushed myself: [Rafael: paste the exact `git remote add` and first `git push` commands you used]
5. `git push` after each commit. At the time of writing, `git status -sb` showed `main...origin/main` with no unpushed commits.

Only the `main` branch was used: no other branches and no pull requests. `.gitignore` was in the first commit and
keeps `*.db`, virtual environments, `__pycache__` and `.pytest_cache` out of the repository.

### 3.2 Development history
| # | Required stage | Commit message |
|---|----------------|----------------|
| 1 | Initial project setup | Initial project setup: FastAPI backend skeleton, database models, Philippine-time helper and tests |
| 2 | Create application interface | Create application interface: borrow and staff tabs with forms and tables; Create application interface: strengthen heading sizes for a clearer type hierarchy |
| 3 | Implement core functionality | Implement core functionality: equipment inventory with search and availability; Implement core functionality: record a borrow and prevent over-borrowing; Implement core functionality: return equipment and track status |
| 4 | Add input validation | Add input validation: field rules, due-date window, and friendly error messages |
| 5 | Fix application error | Fix application error: return 404 instead of crashing on ids larger than SQLite can store |
| 6 | Refactor application code | Refactor application code: share one list loader between the inventory and borrow records |
| 7 | Update documentation | Update documentation: README, testing table, and AI-assisted development report (this commit; it is not in the log below because the log was taken just before it was made) |

`git log --oneline` output (taken just before the documentation commit):
```
29faaee Refactor application code: share one list loader between the inventory and borrow records
c526b2a Fix application error: return 404 instead of crashing on ids larger than SQLite can store
25afd4c Add input validation: field rules, due-date window, and friendly error messages
2930b20 Implement core functionality: return equipment and track status
ffdfec0 Implement core functionality: record a borrow and prevent over-borrowing
f07248a Implement core functionality: equipment inventory with search and availability
84abe8e Create application interface: strengthen heading sizes for a clearer type hierarchy
cf2091a Create application interface: borrow and staff tabs with forms and tables
acace0b Initial project setup: FastAPI backend skeleton, database models, Philippine-time helper and tests
```
[SCREENSHOT of the commit history page on GitHub]

---

## 4. Testing and Validation
The full table (55 rows covering all 132 automated test cases), the real pytest summary, the manual
browser checks, and the known limitations are in [TESTING.md](TESTING.md). A sample:

| Test | Description | Input | Expected result | Actual result | Status |
|------|-------------|-------|-----------------|---------------|--------|
| 1 | Valid input: borrow equipment | Borrow 2 of 5 | 201; available drops to 3 | As expected | PASS |
| 2 | Invalid input: borrow too many | Total 10, ask for 11 | 400 "Only 10 available; you asked for 11." | As expected | PASS |
| 3 | Edge case: due today is not overdue | Unreturned, due today | Status Borrowed | As expected | PASS |
| 4 | Edge case: search `%` | `search=%` with one name containing `%` | Only that name | As expected | PASS |
| 5 | Edge case: id beyond SQLite's range | Return id 10**20 | 404, never 500 | As expected | PASS |

Automated tests: `132 passed`. [SCREENSHOT of pytest output]

Known gaps found by probing and not fixed (full list in TESTING.md): JSON `true` is accepted as a number;
control characters are accepted in names; names that differ only by inner spacing count as different items;
`?category=` and `?status=` with an unknown value return an empty list instead of a 422.

---

## 5. Implementation Decisions
| Decision | Why |
|----------|-----|
| Available quantity is calculated, never stored | A stored counter can drift out of sync; borrowing and returning change it automatically |
| Status (Borrowed, Returned, Overdue) is calculated, never stored | It can never disagree with the dates; "Overdue" appears by itself when the due date passes |
| "Today" is Philippine time, a fixed UTC+8 helper (`today_ph`) | Everyone gets the same due-date window and Overdue result, whatever the server's timezone is |
| `name_key`: a lowercase copy of the name with a UNIQUE constraint | Makes the duplicate check case-insensitive and safe even if two requests arrive together |
| Search text is escaped before `LIKE ... ESCAPE` | `%` and `_` are wildcards; escaping makes them match themselves, so searching `%` finds only names containing `%` |
| The server re-checks availability on every borrow | The page may show stale numbers if someone else just borrowed |
| The due-date window is checked in the service, not in the schema | It depends on today's date, so it is a business rule |
| Validation messages come from one handler (`errors.py`) | Every 422 is a friendly `{"detail": "..."}`, never Pydantic's wording |
| The same rules run in the browser (`validation.js`) and on the server | The browser shows each message beside its field; the server stays the real gatekeeper |
| User text goes in the page with `textContent`, never `innerHTML` | `<script>` and `<img onerror>` names are shown as plain text |
| An id outside SQLite's range is treated as "not found" | Prevents a 500 crash; matches the 404 rule for ids that do not exist |
| The status filter runs after the status is calculated | Status is not a column, and the record count is small |
| Tests use in-memory SQLite and reset between tests | Fast, independent tests that never touch `equiptrack.db` |

---

## 6. Final System Screenshots
1. [SCREENSHOT] Main screen (Borrow tab)
2. [SCREENSHOT] Feature 1 in use (search and category filter)
3. [SCREENSHOT] Feature 2 in use (borrow confirmation, or the "Only N available" message)
4. [SCREENSHOT] Feature 3 in use (Staff tab with Overdue and Returned badges)
5. [SCREENSHOT] A validation error message
6. [SCREENSHOT] Phone-width view

---

## 7. Lessons Learned
These are drafts based on what really happened; Rafael to rewrite in his own words.
- Something AI did well: writing the failing test first and showing it fail made it clear the test was really checking something; probing the running app with bad input found a real bug (a quantity of -3 once raised the available count above the total, which Step 6 then closed).
- Something AI got wrong, and how I caught it: a test used `"a\b"` (a backspace character), and the browser served a cached old script during the refactor check. Both were caught because the results were checked, not assumed.
- Something about Git/GitHub I now understand better: [Rafael: add]
- Something I'd do differently: [Rafael: add]
