# EquipTrack: Testing and Validation

All results below come from a real run of the test suite on the finished code.
The table is generated from that run: every one of the 132 automated test cases is
covered by exactly one row, and **Actual** / **Status** are taken from the run, not typed by hand.

## How to run the tests

```
cd backend
python -m pytest -v
```

The tests use an in-memory SQLite database (`DATABASE_URL=sqlite://`), so they never touch
`equiptrack.db`, and each test starts with empty tables.

## Real pytest summary

```
======================= 132 passed, 1 warning in 3.22s ========================
```

The one warning is a `StarletteDeprecationWarning` from the test client library, not from EquipTrack's code: "Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead."

[SCREENSHOT of the pytest output]

## Automated test table

55 rows covering 132 test cases (23 valid, 19 invalid, 13 edge rows).
"Input" shows the values the tests send; each row names the real test functions it covers.

| Test # | Description | Input | Expected | Actual | Status |
|---|---|---|---|---|---|
| 1 | **Valid**: Empty inventory lists nothing<br>`test_list_is_empty_when_no_equipment` | GET /api/equipment with no items | 200 and [] | As expected (1 of 1 test case passed) | PASS |
| 2 | **Valid**: Add equipment<br>`test_add_equipment_returns_201_with_available_equal_to_total` | {"name":"Dell Latitude laptop","category":"Laptop","total_quantity":10} | 201; available equals total (10) | As expected (1 of 1 test case passed) | PASS |
| 3 | **Valid**: Available count is live<br>`test_list_shows_live_available_count` | Total 10, an unreturned borrow of 3 | available = 7 | As expected (1 of 1 test case passed) | PASS |
| 4 | **Valid**: Search by name, case-insensitive and partial<br>`test_search_is_case_insensitive_and_partial` | search=LAP | Only "Dell Latitude laptop" | As expected (1 of 1 test case passed) | PASS |
| 5 | **Valid**: Filter by category<br>`test_filter_by_category` | category=Camera | Only the camera | As expected (1 of 1 test case passed) | PASS |
| 6 | **Valid**: Search and category together<br>`test_search_and_category_filter_work_together` | search=lap, category=Audio | Only "Lapel microphone" | As expected (1 of 1 test case passed) | PASS |
| 7 | **Valid**: Equipment name boundaries and trimming<br>`test_equipment_name_boundaries_are_accepted`<br>`test_equipment_name_is_stored_trimmed` | "ab", 60 chars, "  padded name  "; "  Spaced  " | 201; name stored trimmed | As expected (4 of 4 test cases passed) | PASS |
| 8 | **Valid**: All six categories accepted<br>`test_all_six_categories_are_accepted` | Laptop, Projector, Camera, Audio, Networking, Others | 201 each | As expected (6 of 6 test cases passed) | PASS |
| 9 | **Valid**: Total quantity boundaries<br>`test_total_quantity_boundaries_are_accepted` | 1 and 100 | 201 each | As expected (2 of 2 test cases passed) | PASS |
| 10 | **Edge**: Search "%" matches only a literal %<br>`test_search_percent_matches_only_names_containing_a_percent` | search=% with "100% cotton cable" and a laptop | Only "100% cotton cable" | As expected (1 of 1 test case passed) | PASS |
| 11 | **Edge**: Search "_" matches only a literal _<br>`test_search_underscore_matches_only_names_containing_an_underscore` | search=_ with "cam_01" and a laptop | Only "cam_01" | As expected (1 of 1 test case passed) | PASS |
| 12 | **Edge**: LIKE escaping helper<br>`test_escape_like_escapes_percent_underscore_and_backslash`<br>`test_escape_like_leaves_plain_text_alone` | "100%", "a_b", a backslash, "laptop" | % _ and \ escaped; plain text unchanged | As expected (2 of 2 test cases passed) | PASS |
| 13 | **Edge**: Available = total when nothing borrowed; unreturned subtract; returned ignored<br>`test_available_is_total_when_nothing_borrowed`<br>`test_available_subtracts_unreturned_borrows`<br>`test_available_ignores_returned_borrows` | Total 10; borrows of 3 and 2; a returned borrow of 4 | 10; 5; 10 | As expected (3 of 3 test cases passed) | PASS |
| 14 | **Invalid**: Equipment name too short, spaces only, or too long<br>`test_equipment_name_length_is_422` | "a", "   ", " a ", 61 chars | 422 "Equipment name must be 2 to 60 characters." | As expected (4 of 4 test cases passed) | PASS |
| 15 | **Invalid**: Duplicate equipment name (any case, extra spaces)<br>`test_duplicate_name_is_rejected_case_insensitively_with_409`<br>`test_duplicate_equipment_name_is_409` | "DELL latitude LAPTOP" after "Dell Latitude laptop" | 409 "That equipment already exists." | As expected (2 of 2 test cases passed) | PASS |
| 16 | **Invalid**: Category not one of the six<br>`test_category_must_be_one_of_the_six_422` | "", "Nonsense", "laptop", null | 422 "Choose a valid category." | As expected (4 of 4 test cases passed) | PASS |
| 17 | **Invalid**: Total quantity out of range or not a whole number<br>`test_total_quantity_range_and_type_is_422` | 0, -5, 101, 100000, 1.5, "abc", null | 422 "Total quantity must be a whole number from 1 to 100." | As expected (7 of 7 test cases passed) | PASS |
| 18 | **Invalid**: Empty add-equipment form<br>`test_empty_equipment_form_names_the_first_problem` | {} | 422 naming the first problem (equipment name) | As expected (1 of 1 test case passed) | PASS |
| 19 | **Valid**: Borrow equipment<br>`test_successful_borrow_returns_201_and_reduces_available` | Borrow 2 of 5 | 201; available drops to 3; return_date empty | As expected (1 of 1 test case passed) | PASS |
| 20 | **Valid**: borrow_date is today in Philippine time<br>`test_borrow_date_is_today_in_philippine_time` | Clock faked to 2026-10-02 | borrow_date = 2026-10-02 | As expected (1 of 1 test case passed) | PASS |
| 21 | **Valid**: Borrow exactly the available amount<br>`test_borrowing_exactly_the_available_amount_is_allowed_and_leaves_zero` | Total 4: borrow 4, then borrow 1 | 201, 0 left; then 400 "Only 0 available; you asked for 1." | As expected (1 of 1 test case passed) | PASS |
| 22 | **Valid**: Returned records do not count against availability<br>`test_returned_records_do_not_count_against_availability` | 4 of 5 already returned; borrow 5 | 201; 0 left | As expected (1 of 1 test case passed) | PASS |
| 23 | **Valid**: Borrower name boundaries<br>`test_borrower_name_boundaries_are_accepted` | "Mo", 100 chars | 201 each | As expected (2 of 2 test cases passed) | PASS |
| 24 | **Valid**: ID number valid forms<br>`test_id_number_valid_forms_are_accepted` | "ABCD", 20 chars, "2023-00123", "a-1-" | 201 each | As expected (4 of 4 test cases passed) | PASS |
| 25 | **Valid**: Both borrower types<br>`test_both_borrower_types_are_accepted` | Student, Faculty | 201 each | As expected (2 of 2 test cases passed) | PASS |
| 26 | **Edge**: Due date window boundaries<br>`test_due_date_window_boundaries_are_accepted` | Due today, due today + 14 days | 201 each | As expected (2 of 2 test cases passed) | PASS |
| 27 | **Invalid**: Borrow more than available<br>`test_borrowing_more_than_available_is_rejected_with_400`<br>`test_quantity_above_available_is_400` | Total 5, 3 out, ask for 3 more; total 10, ask for 11 | 400 "Only 2 available; you asked for 3." / "Only 10 available; you asked for 11."; nothing saved | As expected (2 of 2 test cases passed) | PASS |
| 28 | **Invalid**: Borrow unknown equipment<br>`test_borrowing_unknown_equipment_is_rejected_with_404`<br>`test_unknown_equipment_is_404` | equipment_id 999 | 404 "Equipment not found." | As expected (2 of 2 test cases passed) | PASS |
| 29 | **Invalid**: Borrower name too short, spaces only, or too long<br>`test_borrower_name_length_is_422` | "M", "   ", 101 chars | 422 "Full name must be 2 to 100 characters." | As expected (3 of 3 test cases passed) | PASS |
| 30 | **Invalid**: ID number wrong pattern or length<br>`test_id_number_pattern_is_422` | "abc", 21 chars, "ab!!", "ab!", "ab cd", "ab_cd", "    ", "2023/001" | 422 "ID number must be 4 to 20 letters, digits or dashes." | As expected (8 of 8 test cases passed) | PASS |
| 31 | **Invalid**: Borrower type not Student or Faculty<br>`test_borrower_type_must_be_student_or_faculty_422` | "", "Alien", "student", null | 422 "Select Student or Faculty." | As expected (4 of 4 test cases passed) | PASS |
| 32 | **Invalid**: Quantity below 1<br>`test_quantity_below_one_is_422` | 0, -1, -3 | 422 "Quantity must be at least 1." | As expected (3 of 3 test cases passed) | PASS |
| 33 | **Invalid**: Quantity not a whole number<br>`test_quantity_that_is_not_a_whole_number_is_422` | 1.5, "abc", null | 422 "Quantity must be a whole number of at least 1." | As expected (3 of 3 test cases passed) | PASS |
| 34 | **Invalid**: Malformed or missing due date<br>`test_malformed_due_date_is_422`<br>`test_missing_due_date_is_422` | "tomorrow", "2026-13-45", "2026-02-30", "", "10/08/2026", null, field missing | 422 "Enter a valid due date." | As expected (7 of 7 test cases passed) | PASS |
| 35 | **Invalid**: Due date outside today to +14 days<br>`test_due_date_outside_the_window_is_400` | Yesterday, -30, +15, +400 days | 400 "Due date must be between today and 14 days from today." | As expected (4 of 4 test cases passed) | PASS |
| 36 | **Invalid**: Empty borrow form<br>`test_empty_borrow_form_names_the_first_problem` | {} | 422 naming the first problem (full name) | As expected (1 of 1 test case passed) | PASS |
| 37 | **Edge**: Equipment id beyond SQLite's integer range (the Step 7 error)<br>`test_borrow_with_an_equipment_id_beyond_sqlite_range_is_404_not_500` | equipment_id 2**63, 10**20, -(2**63)-1, -(10**20); boundaries 2**63-1 and -(2**63) | 404 "Equipment not found.", never a 500 | As expected (6 of 6 test cases passed) | PASS |
| 38 | **Valid**: Status Borrowed when due in the future<br>`test_unreturned_with_future_due_date_is_borrowed` | Unreturned, due in 5 days | Borrowed | As expected (1 of 1 test case passed) | PASS |
| 39 | **Edge**: Due today is NOT overdue<br>`test_due_today_is_not_overdue` | Unreturned, due today | Borrowed | As expected (1 of 1 test case passed) | PASS |
| 40 | **Edge**: Due yesterday IS overdue<br>`test_due_yesterday_is_overdue` | Unreturned, due yesterday | Overdue | As expected (1 of 1 test case passed) | PASS |
| 41 | **Edge**: A returned item is never overdue<br>`test_returned_is_returned_even_if_it_was_late`<br>`test_returned_on_time_is_returned` | Returned late; returned on time | Returned; Returned | As expected (2 of 2 test cases passed) | PASS |
| 42 | **Valid**: A new borrow reports status Borrowed<br>`test_new_borrow_reports_status_borrowed` | POST /api/borrows | status = Borrowed | As expected (1 of 1 test case passed) | PASS |
| 43 | **Valid**: Return equipment<br>`test_return_sets_today_marks_returned_and_restores_availability` | POST /api/borrows/{id}/return (clock faked to 2026-10-02) | 200; return_date 2026-10-02; status Returned; availability restored | As expected (1 of 1 test case passed) | PASS |
| 44 | **Valid**: Records show computed status and equipment name<br>`test_list_shows_computed_status_and_equipment_name` | One Borrowed, one Overdue, one Returned | Statuses computed correctly | As expected (1 of 1 test case passed) | PASS |
| 45 | **Valid**: Records are newest first<br>`test_list_is_newest_first` | Two borrows | Newest id first | As expected (1 of 1 test case passed) | PASS |
| 46 | **Valid**: Status filter uses the computed status<br>`test_status_filter_uses_the_computed_status` | ?status=Borrowed / Overdue / Returned | Only matching records | As expected (1 of 1 test case passed) | PASS |
| 47 | **Edge**: Overdue items still count as borrowed out<br>`test_overdue_items_still_count_as_borrowed_out` | Total 5, overdue borrow of 2 | available = 3 | As expected (1 of 1 test case passed) | PASS |
| 48 | **Invalid**: Return the same record twice<br>`test_returning_twice_is_rejected_with_400`<br>`test_return_twice_is_400` | Second POST /return | 400 "This item was already returned." | As expected (2 of 2 test cases passed) | PASS |
| 49 | **Invalid**: Return an unknown record<br>`test_returning_unknown_record_is_rejected_with_404`<br>`test_return_unknown_record_is_404` | POST /api/borrows/999/return | 404 "Borrow record not found." | As expected (2 of 2 test cases passed) | PASS |
| 50 | **Edge**: Return id beyond SQLite's integer range (the Step 7 error)<br>`test_return_with_an_id_beyond_sqlite_range_is_404_not_500` | id 2**63, 10**20, -(2**63)-1, -(10**20); boundaries 2**63-1 and -(2**63) | 404 "Borrow record not found.", never a 500 | As expected (6 of 6 test cases passed) | PASS |
| 51 | **Invalid**: Body that is not JSON<br>`test_body_that_is_not_json_is_422_with_friendly_text` | "{broken" | 422 "The request could not be read. Please check your entries and try again." | As expected (1 of 1 test case passed) | PASS |
| 52 | **Invalid**: Body that is not an object; non-numeric path id<br>`test_body_that_is_not_an_object_is_422_with_friendly_text`<br>`test_non_numeric_record_id_in_the_path_is_422_with_friendly_text` | [1,2,3]; /api/borrows/abc/return | 422 "Please check your entries and try again." | As expected (2 of 2 test cases passed) | PASS |
| 53 | **Edge**: Nested and unknown field errors in the friendly-message function<br>`test_nested_field_errors_use_the_last_field_name`<br>`test_nested_whole_number_error_uses_the_whole_number_message`<br>`test_unknown_field_gets_the_generic_message` | Error path body > items > 0 > quantity; body > mystery | Quantity messages; generic message | As expected (3 of 3 test cases passed) | PASS |
| 54 | **Valid**: Server health check<br>`test_health_returns_ok` | GET /api/health | 200 {"status":"ok"} | As expected (1 of 1 test case passed) | PASS |
| 55 | **Edge**: Philippine time helper (UTC+8)<br>`test_today_ph_is_next_day_after_1600_utc`<br>`test_today_ph_same_day_before_1600_utc`<br>`test_now_ph_has_plus_8_offset`<br>`test_utcnow_is_timezone_aware_utc` | 17:00 UTC; 15:59 UTC | Next day in the Philippines; same day; +8 offset; UTC helper aware | As expected (4 of 4 test cases passed) | PASS |

Rows failing in this run: none.

## Manual checks in the browser

These were done by hand in the Browser pane while building (they are not automated).
They are recorded as observed.

| Check | What I did | Observed |
|---|---|---|
| Search | Typed `LAP` in the search box | Only "Dell Latitude laptop" remained |
| Wildcard search | Typed `%` | The empty state "Nothing matches your search..." appeared; clearing it brought back all 8 items |
| Duplicate equipment | Added `dell latitude LAPTOP` in the Staff tab | "That equipment already exists." |
| Borrow, then over-borrow | Borrowed 2 of 3 cameras, then asked for 5 with 1 left | Confirmation "Borrow #1 recorded: 2 x Canon DSLR camera. Due ..."; then "Only 1 available; you asked for 5."; the form kept the entries |
| Last item | Borrowed the last camera | Row showed 0 with "Out of stock"; the dropdown option was disabled |
| Overdue and return | Opened the Staff tab with the seeded overdue record, pressed Return | Red "Overdue" badge, then a "Returned ..." banner; the Epson projector showed 5 available (its total); the row became Returned with no button |
| Status filter | Clicked Borrowed, then Overdue | "No borrowed records." then the overdue row |
| Empty form | Submitted both forms empty | A message under every field (on the borrow form, focus also moved to the first bad field) |
| 1-character name; spaces-only name | Typed `M`; typed spaces | "...must be 2 to ... characters." |
| ID `ab!` | Typed `ab!` | "ID number must be 4 to 20 letters, digits or dashes." |
| Quantity 0, -1, 1.5 | Typed each | "Quantity must be at least 1." (0 and -1); "Quantity must be a whole number of at least 1." (1.5) |
| Due date yesterday, +15 days | Set each | "Due date must be between today and 14 days from today." |
| Malformed date | Typed `tomorrow` into the date box | The box stayed empty, so "Enter a valid due date." |
| `<script>` and `<img onerror>` as names | Submitted them as an equipment name and a borrower name | Saved and shown as plain text; no element was created |
| Server stopped | Stopped the server and changed a filter | The error state with "Cannot reach the server..." and a Try again button |
| Phone width (375 px) | Resized the pane | Layout stacked; no sideways page scroll; the Available column is visible |

The same invalid cases were also sent straight to the running API (not through the form) and
returned the same friendly messages with no raw "Input should" text.

[SCREENSHOT of a validation message in the browser]

## Known limitations (found by probing)

These were found while probing the running API in Step 6. Item 1 was fixed in Step 7. Items 2 to 9 are
**not fixed** and are listed here honestly:

1. ~~HTTP 500 for ids larger than SQLite can store~~ **Fixed in Step 7** (now 404).
2. JSON `true` is accepted as a number (for `quantity`, `total_quantity` and `equipment_id` it became 1); the text `"2"` and the number `2.0` are accepted too.
3. Control characters (a newline, a NUL character) are accepted inside names.
4. Equipment names that differ only by inner spacing ("Dell  Latitude" and "Dell Latitude") are treated as different items; the duplicate rule only ignores case and outer spaces.
5. `GET /api/equipment?category=Nonsense` and `GET /api/borrows?status=Nonsense` return `200 []`, but docs/PLAN.md section 8 lists 422 for these.
6. A 31-digit quantity produces a very long "Only N available; you asked for ..." message.
7. Two people borrowing at the very same instant were not tested.
8. There is no confirmation dialog before pressing Return, so a mis-click cannot be undone.
9. The front-end (JavaScript) has no automated tests; it was checked by hand and with a throwaway browser probe during the refactor.
