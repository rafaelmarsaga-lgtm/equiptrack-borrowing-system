// Page wiring: tabs, the equipment inventory, borrowing, and borrow records.

const TAB_NAMES = ["borrow", "staff"];
const SEARCH_DELAY_MS = 300;

// Field ids in page order: the first invalid one receives focus.
const EQUIPMENT_FIELDS = ["equipment-name", "equipment-category", "equipment-total"];
const BORROW_FIELDS = ["borrower-name", "id-number", "borrower-type", "equipment-select", "borrow-quantity", "due-date"];

// Builds the loader for one list area ("inventory" or "records"). A load shows
// "loading", fetches, then shows the table, the empty message or the error.
//   getQuery()           reads the filters ONCE at the start of a load
//   fetchItems(query)    asks the server
//   emptyMessage(query)  text for the empty state (same query as the request)
//   render(items)        draws the rows
// Each loader numbers its requests and only the newest may update the page, so
// a slow older response can't overwrite a newer search.
function createListLoader({ area, getQuery, fetchItems, emptyMessage, render }) {
  let latestRequest = 0;

  return async function load() {
    const query = getQuery();
    const requestId = ++latestRequest;

    UI.showState(area, "loading");
    try {
      const items = await fetchItems(query);
      if (requestId !== latestRequest) return;
      if (items.length === 0) {
        UI.setText(`${area}-empty-text`, emptyMessage(query));
        UI.showState(area, "empty");
        return;
      }
      render(items);
      UI.showState(area, "table");
    } catch (error) {
      if (requestId !== latestRequest) return;
      UI.setText(`${area}-error-text`, error.message);
      UI.showState(area, "error");
    }
  };
}

function showTab(name) {
  UI.selectTab(name);
  // Borrows made on the Borrow tab must appear here, so reload when it opens.
  if (name === "staff") loadRecords();
}

function setupTabs() {
  const tabs = document.querySelectorAll('[role="tab"]');
  for (const tab of tabs) {
    tab.addEventListener("click", () => showTab(tab.id.replace("tab-", "")));
    // Arrow keys move between tabs, as screen-reader users expect.
    tab.addEventListener("keydown", (event) => {
      if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
      const step = event.key === "ArrowRight" ? 1 : -1;
      const index = TAB_NAMES.indexOf(tab.id.replace("tab-", ""));
      const next = TAB_NAMES[(index + step + TAB_NAMES.length) % TAB_NAMES.length];
      showTab(next);
      document.getElementById(`tab-${next}`).focus();
    });
  }
}

const loadInventory = createListLoader({
  area: "inventory",
  getQuery: () => ({
    search: document.getElementById("search").value.trim(),
    category: document.getElementById("category-filter").value,
  }),
  fetchItems: ({ search, category }) => Api.listEquipment(search, category),
  emptyMessage: ({ search, category }) =>
    search !== "" || category !== ""
      ? "Nothing matches your search. Try a different name or choose All categories."
      : "No equipment has been added yet. Staff can add items in the Staff tab.",
  render: (items) => UI.renderInventory(items),
});

// The dropdown always lists ALL equipment, even while the table is filtered.
async function loadEquipmentOptions() {
  try {
    UI.renderEquipmentOptions(await Api.listEquipment("", ""));
  } catch (error) {
    // The inventory area already shows a connection error; the form's own
    // error banner appears if the person tries to submit anyway.
  }
}

function refreshEquipment() {
  loadInventory();
  loadEquipmentOptions();
}

function setupInventoryFilters() {
  let timer;
  document.getElementById("search").addEventListener("input", () => {
    clearTimeout(timer);
    timer = setTimeout(loadInventory, SEARCH_DELAY_MS); // wait until typing pauses
  });
  document.getElementById("category-filter").addEventListener("change", loadInventory);
  document.getElementById("inventory-retry").addEventListener("click", loadInventory);
}

function setupAddEquipmentForm() {
  const form = document.getElementById("equipment-form");
  const button = document.getElementById("equipment-submit");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    UI.setBanner("equipment-success", "");
    UI.setBanner("equipment-error", "");

    const raw = {
      name: document.getElementById("equipment-name").value,
      category: document.getElementById("equipment-category").value,
      total: document.getElementById("equipment-total").value,
    };
    // Check first so each message appears next to its field; the server checks again.
    if (!Validation.showErrors(Validation.validateEquipment(raw), EQUIPMENT_FIELDS)) return;
    const data = { name: raw.name, category: raw.category, total_quantity: Number(raw.total) };

    button.disabled = true; // stop double submits while waiting
    try {
      const added = await Api.addEquipment(data);
      UI.setBanner("equipment-success", `Added ${added.name} (${added.total_quantity} available).`);
      form.reset();
      refreshEquipment();
    } catch (error) {
      UI.setBanner("equipment-error", error.message);
    } finally {
      button.disabled = false;
    }
  });
}

function selectedStatus() {
  return document.querySelector('#status-filter input[name="status"]:checked').value;
}

const loadRecords = createListLoader({
  area: "records",
  getQuery: () => ({ status: selectedStatus() }),
  fetchItems: ({ status }) => Api.listBorrows(status),
  emptyMessage: ({ status }) =>
    status ? `No ${status.toLowerCase()} records.` : "Records appear here after someone borrows equipment.",
  render: (records) => UI.renderRecords(records, returnRecord),
});

async function returnRecord(record, button) {
  UI.setBanner("return-success", "");
  UI.setBanner("return-error", "");
  button.disabled = true; // stop double clicks while waiting
  try {
    const returned = await Api.returnBorrow(record.id);
    UI.setBanner(
      "return-success",
      `Returned ${returned.quantity} x ${returned.equipment_name} from ${returned.borrower_name}.`
    );
  } catch (error) {
    UI.setBanner("return-error", error.message);
  } finally {
    // Reload in every case: if it was already returned elsewhere, the list should show that.
    loadRecords();
    refreshEquipment(); // availability is restored by a return
  }
}

function setupStatusFilter() {
  document.getElementById("status-filter").addEventListener("change", loadRecords);
  document.getElementById("records-retry").addEventListener("click", loadRecords);
}

function setupBorrowForm() {
  const form = document.getElementById("borrow-form");
  const button = document.getElementById("borrow-submit");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    UI.setBanner("borrow-success", "");
    UI.setBanner("borrow-error", "");

    const raw = {
      name: document.getElementById("borrower-name").value,
      idNumber: document.getElementById("id-number").value,
      type: document.getElementById("borrower-type").value,
      equipmentId: document.getElementById("equipment-select").value,
      quantity: document.getElementById("borrow-quantity").value,
      dueDate: document.getElementById("due-date").value,
    };
    // Check first so each message appears next to its field; the server checks again.
    if (!Validation.showErrors(Validation.validateBorrow(raw), BORROW_FIELDS)) return;
    const data = {
      borrower_name: raw.name,
      id_number: raw.idNumber,
      borrower_type: raw.type,
      equipment_id: Number(raw.equipmentId),
      quantity: Number(raw.quantity),
      due_date: raw.dueDate,
    };

    button.disabled = true; // stop double submits while waiting
    button.textContent = "Borrowing...";
    try {
      const record = await Api.recordBorrow(data);
      UI.setBanner(
        "borrow-success",
        `Borrow #${record.id} recorded: ${record.quantity} x ${record.equipment_name}. Due ${UI.formatDate(record.due_date)}.`
      );
      form.reset();
    } catch (error) {
      UI.setBanner("borrow-error", error.message);
    } finally {
      button.disabled = false;
      button.textContent = "Borrow equipment";
      // Refresh in every case: after a rejected borrow the counts may be stale.
      refreshEquipment();
    }
  });
}

// A field's message disappears as soon as the person starts fixing that field.
function setupErrorClearing() {
  for (const formId of ["equipment-form", "borrow-form"]) {
    document.getElementById(formId).addEventListener("input", (event) => {
      if (event.target.id) UI.setFieldError(event.target.id, "");
    });
  }
}

setupTabs();
setupInventoryFilters();
setupAddEquipmentForm();
setupBorrowForm();
setupStatusFilter();
setupErrorClearing();
Validation.setDueDateLimits();
refreshEquipment();
loadRecords();
