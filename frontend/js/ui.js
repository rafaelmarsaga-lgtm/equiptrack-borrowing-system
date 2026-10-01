// UI helpers: no business logic, only showing/hiding things on the page.
// All dynamic text goes through textContent so user input is never run as HTML.

const UI = {
  // Set plain text on an element by id (safe against HTML injection).
  setText(id, text) {
    document.getElementById(id).textContent = text;
  },

  // Show or hide an element by id.
  show(id, visible = true) {
    document.getElementById(id).classList.toggle("hidden", !visible);
  },

  // A list area (inventory or records) is in exactly one state:
  // "loading", "empty", "error" or "table". Pass the area prefix.
  showState(area, state) {
    this.show(`${area}-loading`, state === "loading");
    this.show(`${area}-empty`, state === "empty");
    this.show(`${area}-error`, state === "error");
    this.show(`${area}-table-wrap`, state === "table");
  },

  // Message under one form field; an empty string clears it.
  setFieldError(inputId, message) {
    this.setText(`${inputId}-error`, message);
    document.getElementById(inputId).setAttribute("aria-invalid", message ? "true" : "false");
  },

  // Form-level banner. kind is "success" or "error". Pass "" to hide.
  setBanner(id, message) {
    this.setText(id, message);
    this.show(id, message !== "");
  },

  // Switch between the Borrow and Staff tabs.
  selectTab(name) {
    for (const tab of document.querySelectorAll('[role="tab"]')) {
      const active = tab.id === `tab-${name}`;
      tab.setAttribute("aria-selected", String(active));
      tab.tabIndex = active ? 0 : -1;
    }
    for (const panel of document.querySelectorAll('[role="tabpanel"]')) {
      panel.classList.toggle("hidden", panel.id !== `panel-${name}`);
    }
  },
};
