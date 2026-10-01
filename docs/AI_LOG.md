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

## Step 3
- **Step / commit:** `Implement core functionality: equipment inventory with search and availability`
- **Prompt:** Implement Feature 1 (inventory) test-first: search with `%`/`_` escaped, category filter, add equipment with case-insensitive duplicate check (409), computed available quantity, seed script, and wire the Step 2 UI with loading/error states.
- **AI response:** Wrote 14 tests first (service + API), showed them failing, then added `schemas.py`, `services/equipment_service.py` (`escape_like`, `available_quantity`, `list_equipment`, `create_equipment`), `routers/equipment.py`, `seed_data.py` (8 items), `js/api.js`, `UI.renderInventory`, and the inventory/add-form wiring in `app.js`.
- **Evaluation:** (draft) RED: service tests could not import their module and 9 API tests failed with 404/405. GREEN after implementing, except one failure that was a mistake in MY test (`"a\b"` is a backspace character, not a backslash); the code was right, so I fixed the test input and kept the same expectation. Final: 19 passed. In the Browser pane: `LAP` finds only the laptop, `%` shows the empty state, a duplicate with different case shows the 409 message, an HTML name shows as plain text, and stopping the server shows the error state with the friendly message. Known gaps left for Step 6 (confirmed by running them): the add endpoint still accepts a blank or 1-character name, a blank or invented category, and zero, negative or 100000 quantities. The Borrow form's equipment dropdown is not filled yet (Step 4).
- **Modifications:** (draft) None yet.

## Step 4
- **Step / commit:** `Implement core functionality: record a borrow and prevent over-borrowing`
- **Prompt:** Implement Feature 2 (borrow) test-first: 404 for unknown equipment, 400 "Only N available; you asked for M." when over the available amount, borrow_date = today in Philippine time, confirmation with record id and due date, inventory refresh, and disable 0-stock equipment in the dropdown.
- **AI response:** Wrote 6 tests first and showed them failing, then added `BorrowCreate`/`BorrowOut` schemas, `services/borrow_service.py` (`create_borrow`, two small error classes), `routers/borrows.py`, and the frontend: `Api.recordBorrow`, `UI.renderEquipmentOptions`, `UI.formatDate`, and the borrow-form handler in `app.js`.
- **Evaluation:** (draft) RED: all 6 failed with 405 (route missing) or a missing module. GREEN: 25 passed (19 earlier + 6). Browser pane: borrowed 2 of 3 cameras (confirmation "Borrow #1 ... Due Oct 8, 2026", table and dropdown updated), asked for 5 with 1 left (friendly error, form kept), borrowed the last one (row shows Out of stock, dropdown option disabled). The server re-checks availability even though the dropdown shows it, because the page can be stale. Gaps confirmed by running them (all accepted with 201, left for Step 6): quantity 0, quantity -3 (this RAISES available above the total, a real integrity bug), blank name, ID `a!`, type `Alien`, due date in 2020 or 2030. Not tested: two people borrowing at the same instant.
- **Modifications:** (draft) None yet.

## Step 5
- **Step / commit:** `Implement core functionality: return equipment and track status`
- **Prompt:** Implement Feature 3 (return and track) test-first: computed status (due today is not overdue, due yesterday is, returned is never overdue), return endpoint with 400/404, `?status=` filter, a past-due seed record inserted through the ORM, and the Staff table with badges, Return button and filter.
- **AI response:** Wrote 13 tests first and showed them failing, then added `compute_status`, `list_borrows`, `return_borrow` in `borrow_service.py`, `status` on `BorrowOut`, `GET /api/borrows` and `POST /api/borrows/{id}/return`, the ORM-inserted overdue record in `seed_data.py`, `UI.renderRecords`, and the records/filter/return wiring in `app.js`.
- **Evaluation:** (draft) RED: 5 status tests could not import `compute_status`; 7 of 8 API tests failed with 405 / `KeyError: 'status'`; 1 passed on purpose (`test_overdue_items_still_count_as_borrowed_out` guards behaviour from Step 3). GREEN: 38 passed. Browser pane: the seeded record shows Overdue; filter Borrowed shows the empty state, Overdue shows the row; Return shows a banner, availability goes 4 to 5, and the row becomes Returned with no button; a borrow made on the Borrow tab appears on the Staff tab, newest first. Design choice to defend: status is filtered in Python after computing, because it is not stored. Not tested: two staff pressing Return on the same record at once (the second gets the 400 message, covered by the double-return test, but not tried in two tabs). No confirm dialog before Return, so a mis-click cannot be undone.
- **Modifications:** (draft) None yet.
