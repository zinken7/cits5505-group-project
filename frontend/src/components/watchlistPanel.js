/**
 * Watchlist Panel — Dashboard Interactivity
 *
 * Handles tab switching and AJAX status updates on the dashboard page.
 * Reads initial data from server-rendered data-watchlist attribute,
 * then enhances with client-side interactions.
 */
import { createStore } from "../core/state.js";
import { updateWatchlistItem, removeFromWatchlist } from "../api/watchlist.js";

/**
 * Initialize the dashboard page.
 * @param {HTMLElement} appEl - The #app element with data-watchlist
 */
export function initDashboard(appEl) {
  // Parse server-provided watchlist data
  const initialData = JSON.parse(appEl.dataset.watchlist || "[]");

  const store = createStore({
    activeTab: "watching",
    items: initialData,
  });

  // ── Tab Switching ──
  const $tabs = $(appEl).find(".tab-btn");
  const $panels = $(appEl).find(".watchlist-panel");

  $tabs.on("click", function () {
    const status = $(this).data("status");
    store.setState({ activeTab: status });

    // Update tab styles
    $tabs
      .removeClass("text-blue-600 border-b-2 border-blue-600")
      .addClass("text-gray-500");
    $(this)
      .removeClass("text-gray-500")
      .addClass("text-blue-600 border-b-2 border-blue-600");

    // Show/hide panels
    $panels.addClass("hidden");
    $panels.filter(`[data-status="${status}"]`).removeClass("hidden");
  });

  // ── Status Change (via dropdown) ──
  $(appEl).on("change", ".status-select", async function () {
    const $select = $(this);
    const itemId = $select.data("item-id");
    const newStatus = $select.val();

    try {
      await updateWatchlistItem(itemId, newStatus);
      // Reload page to reflect changes (SSR re-render)
      window.location.reload();
    } catch (err) {
      console.error("Failed to update status:", err.message);
      alert("Failed to update status. Please try again.");
    }
  });

  // ── Remove Item ──
  $(appEl).on("click", ".remove-btn", async function () {
    const $btn = $(this);
    const itemId = $btn.data("item-id");

    if (!confirm("Remove this item from your watchlist?")) return;

    try {
      await removeFromWatchlist(itemId);
      $btn.closest("[data-ui='card']").fadeOut(300, function () {
        $(this).remove();
      });
    } catch (err) {
      console.error("Failed to remove item:", err.message);
      alert("Failed to remove item. Please try again.");
    }
  });
}
