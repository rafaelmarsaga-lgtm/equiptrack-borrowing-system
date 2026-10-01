// All server calls live here so the rest of the code never touches fetch().

const Api = {
  // Sends a request and returns the parsed JSON. On failure it throws an
  // Error whose message is already friendly enough to show to the user.
  async request(path, options = {}) {
    let response;
    try {
      response = await fetch(path, {
        headers: { "Content-Type": "application/json" },
        ...options,
      });
    } catch (networkError) {
      throw new Error("Cannot reach the server. Check that it is running and try again.");
    }

    let body = null;
    try {
      body = await response.json();
    } catch (parseError) {
      // No JSON body (for example a crash page); handled below.
    }

    if (!response.ok) {
      // Our own errors carry a plain-text "detail". Anything else (such as the
      // default 422 format) is replaced until Step 6 makes every error friendly.
      const detail = body && typeof body.detail === "string" ? body.detail : null;
      throw new Error(detail || "Something went wrong. Please check your entries and try again.");
    }
    return body;
  },

  listEquipment(search, category) {
    const params = new URLSearchParams();
    if (search) params.set("search", search);
    if (category) params.set("category", category);
    const query = params.toString();
    return this.request(`/api/equipment${query ? `?${query}` : ""}`);
  },

  addEquipment(data) {
    return this.request("/api/equipment", { method: "POST", body: JSON.stringify(data) });
  },
};
