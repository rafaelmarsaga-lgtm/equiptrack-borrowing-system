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
