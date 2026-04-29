/**
 * Light / dark / system theme (data-theme on <html>).
 * Team: use window.setWatchlistTheme('light'|'dark'|'system') from a toggle button.
 */
const STORAGE_KEY = "watchlist-theme";

function resolveMode(mode) {
  if (mode === "system") {
    return window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  }
  return mode === "dark" ? "dark" : "light";
}

export function getStoredTheme() {
  try {
    return localStorage.getItem(STORAGE_KEY) || "light";
  } catch {
    return "light";
  }
}

export function syncThemeToggleUi() {
  const btn = document.getElementById("theme-toggle");
  if (!btn) return;
  const dark = document.documentElement.dataset.theme === "dark";
  const label = btn.querySelector("[data-theme-toggle-label]");
  if (label) {
    label.textContent = dark ? "Switch to light mode" : "Switch to dark mode";
  }
  btn.title = dark ? "Switch to light mode" : "Switch to dark mode";

  // Sync moon/sun icons (app_layout.html topbar)
  const moon = btn.querySelector(".theme-icon-moon");
  const sun = btn.querySelector(".theme-icon-sun");
  if (moon) moon.style.display = dark ? "none" : "";
  if (sun) sun.style.display = dark ? "" : "none";
}

/** Apply resolved light|dark to document (updates CSS variables via [data-theme]). */
export function applyTheme(mode) {
  const root = document.documentElement;
  const resolved = resolveMode(mode);
  root.dataset.theme = resolved;
  root.style.colorScheme = resolved === "dark" ? "dark" : "light";
  syncThemeToggleUi();
}

/** Persist preference and apply. Use 'system' to follow OS. */
export function setTheme(mode) {
  if (mode !== "light" && mode !== "dark" && mode !== "system") {
    return;
  }
  try {
    localStorage.setItem(STORAGE_KEY, mode);
  } catch {
    /* ignore */
  }
  applyTheme(mode);
}

const THEME_ORDER = ["light", "dark", "system"];

/** Cycle light → dark → system (optional; navbar uses toggleLightDark). */
export function cycleTheme() {
  const cur = getStoredTheme();
  const i = THEME_ORDER.indexOf(cur);
  const next = THEME_ORDER[(i + 1) % THEME_ORDER.length];
  setTheme(next);
}

/**
 * Toggle only resolved light ↔ dark (explicit storage).
 * Avoids a 3-step cycle where "system" often matches the previous look (feels like two clicks).
 */
export function toggleLightDark() {
  const resolved =
    document.documentElement.dataset.theme === "dark" ? "dark" : "light";
  setTheme(resolved === "dark" ? "light" : "dark");
}

export function initTheme() {
  const stored = getStoredTheme();
  applyTheme(stored);

  window.setWatchlistTheme = setTheme;
  window.cycleWatchlistTheme = cycleTheme;
  window.toggleWatchlistTheme = toggleLightDark;

  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => {
    if (getStoredTheme() === "system") {
      applyTheme("system");
    }
  });
}
