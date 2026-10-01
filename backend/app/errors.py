"""Turns Pydantic's validation errors into one friendly sentence.

Every 422 the API sends looks like {"detail": "<message>"}; the raw
Pydantic wording ("Input should be ...") is never shown to the user."""
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

GENERIC_MESSAGE = "Please check your entries and try again."
UNREADABLE_BODY_MESSAGE = "The request could not be read. Please check your entries and try again."

# One message per field name. Only the last text part of the error location is
# used, so nested fields (body -> items -> 0 -> quantity) resolve to "quantity".
FIELD_MESSAGES = {
    "name": "Equipment name must be 2 to 60 characters.",
    "category": "Choose a valid category.",
    "total_quantity": "Total quantity must be a whole number from 1 to 100.",
    "borrower_name": "Full name must be 2 to 100 characters.",
    "id_number": "ID number must be 4 to 20 letters, digits or dashes.",
    "borrower_type": "Select Student or Faculty.",
    "equipment_id": "Select equipment from the list.",
    "quantity": "Quantity must be at least 1.",
    "due_date": "Enter a valid due date.",
}
# "1.5" or "abc" is not "less than 1", so quantity gets its own wording for that.
QUANTITY_NOT_WHOLE_MESSAGE = "Quantity must be a whole number of at least 1."


def friendly_message(errors: list[dict]) -> str:
    """Message for the first error in the list."""
    if not errors:
        return GENERIC_MESSAGE
    error = errors[0]
    if error.get("type") == "json_invalid":
        return UNREADABLE_BODY_MESSAGE

    field = next((part for part in reversed(error.get("loc", ())) if isinstance(part, str)), None)
    if field == "quantity" and error.get("type") != "greater_than_equal":
        return QUANTITY_NOT_WHOLE_MESSAGE
    return FIELD_MESSAGES.get(field, GENERIC_MESSAGE)


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": friendly_message(exc.errors())})
