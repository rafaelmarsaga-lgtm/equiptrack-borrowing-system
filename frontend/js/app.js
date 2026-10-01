// Page wiring. Step 2 only handles the tabs; data loading is added in Steps 3-5.

const TAB_NAMES = ["borrow", "staff"];

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

setupTabs();
