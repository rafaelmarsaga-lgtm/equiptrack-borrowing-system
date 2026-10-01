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

  // Small helper: <tag class="..."> with text, built safely (no innerHTML).
  makeElement(tag, className, text) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined) element.textContent = text;
    return element;
  },

  // Replace the inventory rows with the given equipment list.
  renderInventory(items) {
    const rows = items.map((item) => {
      const row = document.createElement("tr");

      // Category is shown under the name on phones and in its own column on wider screens.
      const nameCell = this.makeElement("td", "td font-semibold", item.name);
      nameCell.append(this.makeElement("span", "block sm:hidden text-ink-soft font-normal", item.category));

      const availableCell = this.makeElement("td", "td");
      const wrapper = this.makeElement("div", "flex items-center gap-3");
      wrapper.append(this.makeElement("span", "num font-semibold w-6 text-right", String(item.available)));
      if (item.available === 0) {
        wrapper.append(this.makeElement("span", "badge badge-out", "Out of stock"));
      } else {
        // The gauge is decorative: the number beside it carries the information.
        const gauge = this.makeElement("span", "gauge" + (item.available / item.total_quantity <= 0.25 ? " low" : ""));
        gauge.setAttribute("aria-hidden", "true");
        const fill = document.createElement("span");
        fill.style.width = `${Math.round((item.available / item.total_quantity) * 100)}%`;
        gauge.append(fill);
        wrapper.append(gauge);
      }
      availableCell.append(wrapper);

      row.append(
        nameCell,
        this.makeElement("td", "td hidden sm:table-cell", item.category),
        this.makeElement("td", "td num text-right", String(item.total_quantity)),
        availableCell,
      );
      return row;
    });
    document.getElementById("inventory-body").replaceChildren(...rows);
  },

  // "2026-10-08" -> "Oct 8, 2026". Built from parts so the browser's timezone can't shift the day.
  formatDate(isoDate) {
    const [year, month, day] = isoDate.split("-").map(Number);
    return new Date(year, month - 1, day).toLocaleDateString("en-US", {
      year: "numeric", month: "short", day: "numeric",
    });
  },

  // Fill the borrow form's equipment dropdown. Items with nothing left are
  // shown but disabled so people can see why they can't pick them.
  renderEquipmentOptions(items) {
    const select = document.getElementById("equipment-select");
    const previous = select.value;
    const options = items.map((item) => {
      const option = document.createElement("option");
      option.value = String(item.id);
      option.disabled = item.available === 0;
      option.textContent = item.available === 0
        ? `${item.name} (out of stock)`
        : `${item.name} (${item.available} available)`;
      return option;
    });
    // Keep the first "Select equipment" option, replace the rest.
    select.replaceChildren(select.options[0], ...options);
    // Keep the person's choice if it can still be borrowed.
    const stillValid = options.some((o) => o.value === previous && !o.disabled);
    select.value = stillValid ? previous : "";
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
