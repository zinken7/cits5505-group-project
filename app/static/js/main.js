/**
 * Team / page-level JavaScript (layout pages only)
 * -------------------------------------------------
 * Loaded after app/static/js/ui.js — jQuery ($) and window.UI are available.
 * Vite entry (theme, UI.init on #app, etc.) runs as a module in <head>.
 *
 * Page-specific scripts are loaded separately:
 *   - items.js     → detail.html (item detail page)
 *   - watchlist.js → watchlist pages
 *
 * Use this file only for behaviour shared across ALL layout pages.
 *
 * apiFetch(path, opts)
 * --------------------
 * Thin wrapper around fetch() for /api/v1 calls.
 * - Reads the CSRF token from <meta name="csrf-token">
 * - Sets Content-Type and X-CSRFToken automatically
 * - Unwraps the standard APIResponse envelope: resolves with `data` or
 *   rejects with an Error(message) when success === false.
 *
 * Usage:
 *   apiFetch("/api/v1/watchlist", { method: "POST", body: { mediaId: 1, mediaType: "anime" } })
 *     .then(data => console.log(data))
 *     .catch(err => console.error(err.message));
 */
window.apiFetch = function apiFetch(path, opts) {
  opts = opts || {};
  var headers = Object.assign({ "Content-Type": "application/json" }, opts.headers || {});
  var fetchOpts = Object.assign({}, opts, { headers: headers });
  if (opts.body && typeof opts.body === "object") {
    fetchOpts.body = JSON.stringify(opts.body);
  }
  return fetch(path, fetchOpts).then(function (res) {
    return res.json().then(function (envelope) {
      if (!envelope.success) {
        var err = new Error(envelope.message || "API error");
        err.status = res.status;
        err.envelope = envelope;
        throw err;
      }
      return envelope.data;
    });
  });
};

(function ($) {
  "use strict";

  $(function () {
    // Shared page-level initialisation goes here.
  });
})(jQuery);
