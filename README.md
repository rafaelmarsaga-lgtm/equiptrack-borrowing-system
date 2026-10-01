# EquipTrack: Campus Equipment Borrowing System

A web-based system for a college department's equipment room. Students and faculty
can check what is available and borrow it; department staff add equipment, record
returns, and track which items are borrowed, returned, or overdue.

Built for the IT 415 midterm lab exam (Kit A: FastAPI + SQLite + vanilla JavaScript).

## What it does

**Borrow tab (students and faculty)**
- Equipment list with the available quantity of each item, kept up to date from the database
- Search by name (case-insensitive, partial) and filter by category
- Borrow form: full name, ID number, borrower type (Student or Faculty), equipment, quantity, due date
- Borrowing more than what is available is rejected, and items with nothing left cannot be selected

**Staff tab**
- Add equipment (name, category, total quantity)
- Table of every borrow record with a status badge: **Borrowed**, **Returned** or **Overdue**
- Filter the table by status, and press **Return** to record a returned item (availability is restored)

Rules in short: a due date must be from today up to 14 days ahead; "today" is Philippine time (UTC+8);
a record is Overdue when it is not returned and its due date is before today. Available quantity and
status are calculated every time they are shown, never stored. There is no login (a stated simplification
for this exam).

## How to run it

You need **Python 3.11 or newer** and an internet connection (the page loads Tailwind CSS from a CDN).

```
cd backend
pip install -r requirements.txt
python seed_data.py
python -m uvicorn app.main:app --reload
```

Then open <http://127.0.0.1:8000/> in a browser.

- `python seed_data.py` fills the database with 8 sample equipment items and one past-due borrow record
  so the Overdue status can be seen. It is safe to run more than once.
- The database is a local file, `backend/equiptrack.db`, created on first run and not committed to Git.
  To start over, stop the server, delete that file, and run `python seed_data.py` again.

## How to run the tests

```
cd backend
python -m pytest -v
```

The tests use an in-memory database, so they never touch `equiptrack.db`. The last full run was
**132 passed** (see [docs/TESTING.md](docs/TESTING.md)).

## API

| Method and path | What it does |
|---|---|
| `GET /api/equipment?search=&category=` | List equipment with the available quantity |
| `POST /api/equipment` | Add equipment (409 if the name already exists) |
| `POST /api/borrows` | Record a borrow (400 if over the available quantity or the due date is outside the window, 404 if the equipment does not exist) |
| `GET /api/borrows?status=` | List borrow records with their computed status |
| `POST /api/borrows/{id}/return` | Mark a record returned (400 if already returned, 404 if not found) |
| `GET /api/health` | Health check |

Every error is returned as `{"detail": "<friendly message>"}`. FastAPI also serves interactive API docs at
<http://127.0.0.1:8000/docs> while the server is running.

## Project layout

```
backend/
  app/
    main.py        app setup, error handler, serves the frontend
    database.py    SQLite connection and sessions
    models.py      Equipment and BorrowRecord tables
    schemas.py     request and response shapes plus the field rules
    errors.py      turns validation errors into friendly messages
    timeutil.py    Philippine-time helpers
    routers/       the API endpoints (equipment.py, borrows.py)
    services/      the business rules (equipment_service.py, borrow_service.py)
  tests/           automated tests
  seed_data.py     sample data
frontend/
  index.html       the page (Tailwind via CDN)
  js/              api.js, ui.js, validation.js, app.js
docs/
  PLAN.md, TESTING.md, DOCUMENTATION.md, AI_LOG.md
```

## Known limitations

A few small gaps found while testing are listed honestly in [docs/TESTING.md](docs/TESTING.md)
(for example, JSON `true` is accepted as a number, and names that differ only by inner spacing count as different items).

## More documentation

- [docs/DOCUMENTATION.md](docs/DOCUMENTATION.md): requirements analysis, AI-assisted development report, GitHub history, decisions
- [docs/TESTING.md](docs/TESTING.md): test table and real test results
- [docs/PLAN.md](docs/PLAN.md): the plan the project was built from
