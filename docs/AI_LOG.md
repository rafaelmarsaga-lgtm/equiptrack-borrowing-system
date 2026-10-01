# AI Log

## Planning (before Step 1)
- **Step / commit:** (planning, included in the Step 1 commit as docs/PLAN.md)
- **Prompt:** Analyze the EquipTrack scenario and produce the requirements analysis, data model, validation table, API, 3 features, 9-step plan and edge cases. No code.
- **AI response:** Asked 3 clarifying questions (staff can add equipment, whole-record returns, status filter), then wrote the full plan.
- **Evaluation:** (draft) Plan matched the scenario and the three objectives. Weak spot: validation rules were split across Steps 3-6, which I needed to understand.
- **Modifications:** (draft) Asked for: escaped LIKE wildcards in search, seed the past-due record via the ORM, a required Step 7, and a fuller Step 9 using the documentation template.

## Step 1
- **Step / commit:** `Initial project setup: FastAPI backend skeleton, database models, Philippine-time helper and tests`
- **Prompt:** Update the plan with my four changes, then do Step 1.
- **AI response:** Created the folder tree, `.gitignore`, `requirements.txt`, `database.py` (StaticPool for in-memory tests), `models.py` (equipment, borrow_records), `timeutil.py` (`today_ph`), `main.py` (lifespan, `/api/health`, static mount), placeholder `index.html`, tests, README stub and `docs/PLAN.md`.
- **Evaluation:** (draft) Wrote the `today_ph` tests first and saw them fail (module missing) before implementing. 5 tests pass. Server answered `/api/health` 200 and `/` 200. Tests created no `.db` file. Risk: the time helper takes an injectable `now` argument, which I should be able to explain.
- **Modifications:** (draft) None yet.

## Step 2
- **Step / commit:** `Create application interface: borrow and staff tabs with forms and tables`
- **Prompt:** Build the full interface (Borrow and Staff tabs, forms, tables, status badges, loading/empty/error states) with no API calls or logic. Propose one design direction first.
- **AI response:** Proposed an "equipment-room logbook" look (cool grey-blue, ink navy, teal accent, a stock gauge bar beside availability). Wrote `frontend/index.html` (Tailwind CDN, labelled inputs, placeholder rows, hidden state boxes, per-field error lines and form banners), `js/ui.js` (show/hide, `showState`, `setFieldError`, `selectTab`, all text via `textContent`), `js/app.js` (tab clicks and arrow keys), and an empty `js/api.js`.
- **Evaluation:** (draft) Checked in the Browser pane at laptop and phone width: tabs switch, no horizontal page scroll, only console message is Tailwind's CDN notice. Called the state helpers from the console and saw the error/empty states, field error and success banner. Found one real problem on phone: the Available column was hidden behind the table's inner scroll. Fixed by hiding the Category column on small screens and showing the category under the name. 5 existing tests still pass. Not checked: a screen reader; keyboard focus rings only checked by reading the CSS.
- **Modifications:** (draft) None yet.
