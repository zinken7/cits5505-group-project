/**
 * App Bootstrap
 *
 * Reads the data-page attribute from #app to determine which page
 * module to initialize. Each page can read server-provided data
 * from data-* attributes.
 */
import { initDashboard } from "../components/watchlistPanel.js";

/**
 * Initialize the appropriate page module based on data-page attribute.
 * @param {HTMLElement} appEl - The #app root element
 */
export function initApp(appEl) {
  const page = appEl.dataset.page;

  switch (page) {
    case "dashboard":
      initDashboard(appEl);
      break;

    case "index":
      // Landing page — could add interactive trending filters here
      break;

    case "profile":
      // Profile page — read-only, no CSR needed for now
      break;

    default:
      break;
  }
}
