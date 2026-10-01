# CLAUDE.md — IT 415 Midterm Lab Exam Project

> Standing instructions for Claude Code. Filled in for the practice exam:
> EquipTrack — Campus Equipment Borrowing System.

## Who I am and what this is
- I'm Rafael, a BSIT student taking the IT 415 midterm: an individual,
  performance-based lab exam, 2 hours 30 minutes, face to face.
- I must build a working application from my instructor's scenario, manage
  it with Git and GitHub, document my AI usage, and explain every part of it.
- Blind submission of AI code counts against me. Everything you write must
  be something I can read, test, and explain.
- Project: **EquipTrack — Campus Equipment Borrowing System**
- Stack chosen: **Kit A (full-stack)**, because borrow and return records
  must be stored and shared between borrowers checking availability and
  staff tracking items, which one browser's localStorage can't do.

## Scenario defaults
- Target users: **students and faculty** (check availability, borrow) and
  **department staff** (manage equipment, record returns, track items).
- No login for this exam (stated openly as a simplification). The app has
  two tabs: "Borrow" (students/faculty) and "Staff".
- Equipment: name (2–60 chars, unique case-insensitive), category (Laptop,
  Projector, Camera, Audio, Networking, Others), total quantity (1–100).
- Available quantity = total − quantity currently borrowed. Never stored;
  always computed, so it can't go stale.
- Borrower: full name (2–100 chars), ID number (4–20 chars, letters, digits,
  and dashes only), borrower type (Student or Faculty).
- Borrow: equipment, quantity 1 to available, due date from today up to 14
  days ahead. Borrowing more than available is rejected (400).
- Return: staff marks a borrow record Returned; it records the return date
  and restores availability. Returning twice is rejected (400).
- Status: Borrowed, Returned, or Overdue (Borrowed and due date before today).
  Overdue is computed, not stored.
- "Today" = Philippine time, fixed UTC+8.
- Out of scope: login, deleting records, reservations, fines, editing a
  borrow record.

## How we work (non-negotiable)
1. **Checkpoint-driven.** Do ONE step at a time. When a step is done, stop,
   summarize what changed, tell me how to verify it, and wait for me to type
   "Proceed to Step N". Never build several steps in one go.
2. **Plan before code.** For anything bigger than a small fix, outline the
   approach first so I can catch a wrong direction before code exists.
3. **Verify, don't claim.** Before saying something works, run it (tests, the
   server, a request) and show me the actual output. If you could not run
   something, say so plainly.
4. **Explain decisions briefly.** One or two sentences on *why* for each
   design choice, so I can defend it. No long essays.
5. **Stay in scope.** Build what the scenario asks. Suggest extras; don't add
   them.
6. **Never delete or weaken a test to make it pass.** Fix the code, or tell me
   the test is wrong and why.
7. **No new dependencies** beyond the kit below without asking me first.
8. **Time is short (2.5 h).** Prefer the simplest design that meets every
   requirement. Scope for about 1 h 20 min of building.

## Skills to use
- Planning: `superpowers:brainstorming` then `superpowers:writing-plans`.
  Ask all clarifying questions in ONE batch (max 5).
- Logic: `superpowers:test-driven-development`.
- Bugs: `superpowers:systematic-debugging`: root cause before the fix.
- Finishing a step: `superpowers:verification-before-completion`.
- UI: `ui-ux-pro-max` and `frontend-design`.
- Do NOT use git worktrees, branches, or subagent-driven development.

## Git and GitHub (graded)
- Work only on the `main` branch. No branches, no pull requests.
- The repository must show this development history, in this order, with
  these exact prefixes in the commit messages:
  1. `Initial project setup: ...`
  2. `Create application interface: ...`
  3. `Implement core functionality: ...` (one commit per feature is fine)
  4. `Add input validation: ...`
  5. `Fix application error: ...` (a REAL error we hit, never an invented one)
  6. `Refactor application code: ...`
  7. `Update documentation: ...`
- Commit only after the step is verified. Message = prefix + what changed,
  in plain English, e.g. `Implement core functionality: record a sale and
  deduct stock`.
- Before committing, show me `git status` so I see what's included.
- I push to GitHub myself with `git push` after each commit. Don't push
  unless I ask.
- Never commit `.db` files, virtual environments, `__pycache__`, or secrets.
  `.gitignore` must exist from the first commit.

## Stack kits

### Kit A — Full-stack (default for "system" scenarios with stored records)
- Backend: Python 3.11+, FastAPI, Pydantic, SQLAlchemy, SQLite (local file)
- Frontend: HTML + vanilla JS (fetch/async-await) + Tailwind CSS via CDN, no build step
- FastAPI serves the frontend as static files (one origin, no CORS)
- Tests: pytest + FastAPI TestClient on in-memory SQLite.
  - Set `DATABASE_URL=sqlite://` (StaticPool, `check_same_thread=False`)
    BEFORE the app is imported, so tests never create the real `.db` file.
  - Always use `with TestClient(app) as client:` so the lifespan runs
    (otherwise: "no such table").
- Use the `lifespan` handler, not `@app.on_event`. One `utcnow()` helper, not
  `datetime.utcnow`. Local time = Philippine time, fixed UTC+8.
- Add a `RequestValidationError` handler so every 422 returns
  `{"detail": "<friendly message>"}`, including nested fields
  (e.g. `items → 0 → quantity`). Never show raw Pydantic text.
- Money: integer centavos, never floats.

```
project/
  backend/
    app/
      main.py          # app, lifespan, error handlers, routers, static mount
      database.py      # engine, session, Base
      models.py        # SQLAlchemy models
      schemas.py       # Pydantic request/response models + validation
      routers/         # one file per feature
      services/        # business logic (pure, testable)
    tests/
    seed_data.py
    requirements.txt
  frontend/
    index.html
    js/api.js  js/ui.js  js/app.js
  docs/
    PLAN.md  TESTING.md  AI_LOG.md  DOCUMENTATION.md
  README.md
  .gitignore
```
Run: `cd backend` → `python seed_data.py` → `python -m uvicorn app.main:app --reload`
→ http://127.0.0.1:8000/  ·  Tests: `python -m pytest -v`

### Kit B — Lightweight (for "website" / small tool scenarios, no server)
- `index.html`, `js/logic.js` (pure functions), `js/storage.js` (localStorage
  in try/catch), `js/app.js` (DOM), Tailwind via CDN.
- Tests: `node --test` on `logic.js` if Node is installed; otherwise a manual
  test table in docs/TESTING.md.
- Run: `python -m http.server 8000` → http://127.0.0.1:8000/

## Code rules
- Validate every input on the server AND give friendly messages in the UI.
  Status codes: 400 rule broken, 404 not found, 409 duplicate, 422 invalid.
- Put user text in the page with `textContent`, never `innerHTML`.
- No hardcoded secrets, passwords, or API keys.
- Small functions, clear names, comments explain *why*.
- Responsive UI with loading, empty, and error states.
- After UI changes, check the running app in the Browser pane.

## AI log (for my documentation — graded)
After each step, append to `docs/AI_LOG.md`:
- **Step / commit:** the commit message
- **Prompt:** a 1–2 line summary of what I asked
- **AI response:** what you produced
- **Evaluation:** what was right, what was wrong or risky, how it was tested
- **Modifications:** what I changed, rejected, or asked you to redo
Leave Evaluation and Modifications as short drafts; I'll rewrite them.
