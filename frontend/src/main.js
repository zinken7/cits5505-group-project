/**
 * WatchList Hub — Frontend Entry Point
 *
 * This is the main Vite entry point. It imports Tailwind CSS
 * and bootstraps client-side interactivity on top of the
 * server-rendered Jinja HTML.
 */
import "./style.css";
import {
  applyTheme,
  getStoredTheme,
  initTheme,
  toggleLightDark,
} from "./theme/theme.js";
import { initApp } from "./core/app.js";

initTheme();

// Wait for DOM ready (jQuery is loaded via CDN in base.html)
$(document).ready(() => {
  applyTheme(getStoredTheme());

  $(document).on("click", "#theme-toggle", (e) => {
    e.preventDefault();
    toggleLightDark();
  });

  const app = document.getElementById("app");
  if (app) {
    initApp(app);
  }

  // Initialize jQuery UI components
  if (window.UI && window.UI.init) {
    window.UI.init();
  }

  // Auto-dismiss flash messages after 5 seconds
  $(".flash-message").each(function () {
    const $msg = $(this);
    setTimeout(() => {
      $msg.fadeOut(300, () => $msg.remove());
    }, 5000);
  });
});
