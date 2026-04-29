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

/** Show/hide password for `.password-input-wrap` (auth templates). */
function initPasswordToggles() {
  document.querySelectorAll(".password-input-wrap").forEach((wrap) => {
    const btn = wrap.querySelector("[data-password-toggle]");
    const input = wrap.querySelector("input:not([type=hidden])");
    if (!btn || !input || btn.dataset.passwordToggleBound) return;
    btn.dataset.passwordToggleBound = "1";
    const showIcon = btn.querySelector(".password-toggle__show");
    const hideIcon = btn.querySelector(".password-toggle__hide");

    const sync = () => {
      const obscured = input.type === "password";
      showIcon?.classList.toggle("hidden", !obscured);
      hideIcon?.classList.toggle("hidden", obscured);
      btn.setAttribute("aria-pressed", obscured ? "false" : "true");
      btn.setAttribute(
        "aria-label",
        obscured ? "Show password" : "Hide password",
      );
    };

    sync();
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      input.type = input.type === "password" ? "text" : "password";
      sync();
    });
  });
}

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

  initPasswordToggles();

  // Auto-dismiss flash messages after 5 seconds
  $(".flash-message").each(function () {
    const $msg = $(this);
    setTimeout(() => {
      $msg.fadeOut(300, () => $msg.remove());
    }, 5002);
  });
});
