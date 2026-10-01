// Page wiring: tabs (Step 2) and the equipment inventory (Step 3).

const TAB_NAMES = ["borrow", "staff"];
const SEARCH_DELAY_MS = 300;

// Every inventory request gets a number; only the newest one may update the
// page, so a slow older response can't overwrite a newer search.
let latestInventoryRequest = 0;

function setupTabs() {
  const tabs = document.querySelectorAll('[role="tab"]');
  for (const tab of tabs) {
    tab.addEventListener("click", () => UI.selectTab(tab.id.replace("tab-", "")));
    // Arrow keys move between tabs, as screen-reader users expect.
    tab.addEventListener("keydown", (event) => {
      if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
      const step = event.key === "ArrowRight" ? 1 : -1;
      const index = TAB_NAMES.indexOf(tab.id.replace("tab-", ""));
      const next = TAB_NAMES[(index + step + TAB_NAMES.length) % TAB_NAMES.length];
      UI.selectTab(next);
      document.getElementById(`tab-${next}`).focus();
    });
  }
}

async function loadInventory() {
  const search = document.getElementById("search").value.trim();
  const category = document.getElementById("category-filter").value;
  const requestId = ++latestInventoryRequest;

  UI.showState("inventory", "loading");
  try {
    const items = await Api.listEquipment(search, category);
    if (requestId !== latestInventoryRequest) return;
    if (items.length === 0) {
      const filtered = search !== "" || category !== "";
      UI.setText(
        "inventory-empty-text",
        filtered
          ? "Nothing matches your search. Try a different name or choose All categories."
          : "No equipment has been added yet. Staff can add items in the Staff tab."
      );
      UI.showState("inventory", "empty");
      return;
    }
    UI.renderInventory(items);
    UI.showState("inventory", "table");
  } catch (error) {
    if (requestId !== latestInventoryRequest) return;
    UI.setText("inventory-error-text", error.message);
    UI.showState("inventory", "error");
  }
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

    const data = {
      name: document.getElementById("equipment-name").value,
      category: document.getElementById("equipment-category").value,
      total_quantity: Number(document.getElementById("equipment-total").value),
    };

    button.disabled = true; // stop double submits while waiting
    try {
      const added = await Api.addEquipment(data);
      UI.setBanner("equipment-success", `Added ${added.name} (${added.total_quantity} available).`);
      form.reset();
      loadInventory();
    } catch (error) {
      UI.setBanner("equipment-error", error.message);
    } finally {
      button.disabled = false;
    }
  });
}

setupTabs();
setupInventoryFilters();
setupAddEquipmentForm();
loadInventory();
