// Client-side checks that mirror the server rules in docs/PLAN.md section 9.
// They exist only to show a message next to the right field BEFORE sending;
// the server still checks everything again and is the real gatekeeper.
//
// Each validate function takes the raw text of the inputs and returns an object
// { inputId: message } containing only the fields that are wrong.

const Validation = {
  CATEGORIES: ["Laptop", "Projector", "Camera", "Audio", "Networking", "Others"],
  BORROWER_TYPES: ["Student", "Faculty"],
  MAX_BORROW_DAYS: 14,

  // Today's date in Philippine time (UTC+8) as "YYYY-MM-DD", whatever the computer's timezone is.
  todayPh() {
    return new Date(Date.now() + 8 * 60 * 60 * 1000).toISOString().slice(0, 10);
  },

  // "2026-10-01" + 14 -> "2026-10-15" (UTC math, so no daylight-saving surprises).
  addDays(isoDate, days) {
    const date = new Date(`${isoDate}T00:00:00Z`);
    date.setUTCDate(date.getUTCDate() + days);
    return date.toISOString().slice(0, 10);
  },

  // The date picker greys out days outside the allowed window.
  setDueDateLimits() {
    const input = document.getElementById("due-date");
    const today = this.todayPh();
    input.min = today;
    input.max = this.addDays(today, this.MAX_BORROW_DAYS);
  },

  validateEquipment(values) {
    const errors = {};
    const nameLength = values.name.trim().length;
    if (nameLength < 2 || nameLength > 60) {
      errors["equipment-name"] = "Equipment name must be 2 to 60 characters.";
    }
    if (!this.CATEGORIES.includes(values.category)) {
      errors["equipment-category"] = "Choose a valid category.";
    }
    const total = values.total.trim();
    if (!/^\d+$/.test(total) || Number(total) < 1 || Number(total) > 100) {
      errors["equipment-total"] = "Total quantity must be a whole number from 1 to 100.";
    }
    return errors;
  },

  validateBorrow(values) {
    const errors = {};
    const nameLength = values.name.trim().length;
    if (nameLength < 2 || nameLength > 100) {
      errors["borrower-name"] = "Full name must be 2 to 100 characters.";
    }
    if (!/^[A-Za-z0-9-]{4,20}$/.test(values.idNumber.trim())) {
      errors["id-number"] = "ID number must be 4 to 20 letters, digits or dashes.";
    }
    if (!this.BORROWER_TYPES.includes(values.type)) {
      errors["borrower-type"] = "Select Student or Faculty.";
    }
    if (values.equipmentId === "") {
      errors["equipment-select"] = "Select equipment from the list.";
    }

    const quantity = values.quantity.trim();
    if (!/^-?\d+$/.test(quantity)) {
      errors["borrow-quantity"] = "Quantity must be a whole number of at least 1.";
    } else if (Number(quantity) < 1) {
      errors["borrow-quantity"] = "Quantity must be at least 1.";
    }

    if (!/^\d{4}-\d{2}-\d{2}$/.test(values.dueDate)) {
      errors["due-date"] = "Enter a valid due date.";
    } else {
      const today = this.todayPh();
      if (values.dueDate < today || values.dueDate > this.addDays(today, this.MAX_BORROW_DAYS)) {
        errors["due-date"] = "Due date must be between today and 14 days from today.";
      }
    }
    return errors;
  },

  // Shows every message next to its field and moves focus to the first wrong
  // field (in page order). Returns true if the form is valid.
  showErrors(errors, fieldOrder) {
    for (const id of fieldOrder) UI.setFieldError(id, errors[id] || "");
    const firstBad = fieldOrder.find((id) => errors[id]);
    if (firstBad) document.getElementById(firstBad).focus();
    return firstBad === undefined;
  },
};
