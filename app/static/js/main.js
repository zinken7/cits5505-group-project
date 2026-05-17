/**
 * Team / page-level JavaScript (layout pages only)
 * -------------------------------------------------
 * Loaded after app/static/js/ui.js — jQuery ($) and window.UI are available.
 * Vite entry (theme, UI.init on #app, etc.) runs as a module in <head>.
 *
 * Page-specific scripts are loaded separately e.g.:
 *   - items.js     → detail.html (item detail page)
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
  var csrfMeta = document.querySelector('meta[name="csrf-token"]');
  var csrfToken = csrfMeta ? csrfMeta.getAttribute("content") : "";
  var headers = Object.assign({ "Content-Type": "application/json", "X-CSRFToken": csrfToken }, opts.headers || {});
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

window.appConfirm = function appConfirm(options) {
  options = options || {};
  var title = options.title || 'Confirm action';
  var message = options.message || '';
  var confirmText = options.confirmText || 'Confirm';
  var cancelText = options.cancelText || 'Cancel';
  var danger = options.danger !== false;

  return new Promise(function (resolve) {
    var modal = document.getElementById('app-confirm-modal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'app-confirm-modal';
      modal.className = 'fixed inset-0 z-200 hidden items-center justify-center bg-black/55 p-4';
      modal.setAttribute('role', 'dialog');
      modal.setAttribute('aria-modal', 'true');
      modal.setAttribute('aria-hidden', 'true');
      modal.innerHTML = [
        '<div class="card max-w-md border border-border p-6 shadow-lg" data-app-confirm-panel>',
        '<h2 class="h-section m-0 text-[1.1rem]" id="app-confirm-title"></h2>',
        '<p class="mt-3 text-[0.875rem] leading-relaxed text-muted" id="app-confirm-message"></p>',
        '<div class="mt-6 flex flex-wrap justify-end gap-2">',
        '<button type="button" class="btn btn--sm" id="app-confirm-cancel"></button>',
        '<button type="button" class="btn btn--sm" id="app-confirm-ok"></button>',
        '</div>',
        '</div>'
      ].join('');
      document.body.appendChild(modal);
    }

    var titleEl = modal.querySelector('#app-confirm-title');
    var msgEl = modal.querySelector('#app-confirm-message');
    var cancelBtn = modal.querySelector('#app-confirm-cancel');
    var okBtn = modal.querySelector('#app-confirm-ok');
    var previousFocus = document.activeElement;

    titleEl.textContent = title;
    msgEl.textContent = message;
    cancelBtn.textContent = cancelText;
    okBtn.textContent = confirmText;
    okBtn.className = danger
      ? 'btn btn--sm border-danger/40 text-danger'
      : 'btn btn--primary btn--sm';

    function close(value) {
      modal.classList.add('hidden');
      modal.classList.remove('flex');
      modal.setAttribute('aria-hidden', 'true');
      document.removeEventListener('keydown', onKeydown);
      cancelBtn.removeEventListener('click', onCancel);
      okBtn.removeEventListener('click', onOk);
      modal.removeEventListener('click', onBackdrop);
      if (previousFocus && typeof previousFocus.focus === 'function') {
        previousFocus.focus();
      }
      resolve(value);
    }

    function onCancel() { close(false); }
    function onOk() { close(true); }
    function onBackdrop(e) {
      if (e.target === modal) close(false);
    }
    function onKeydown(e) {
      if (e.key === 'Escape') close(false);
    }

    cancelBtn.addEventListener('click', onCancel);
    okBtn.addEventListener('click', onOk);
    modal.addEventListener('click', onBackdrop);
    document.addEventListener('keydown', onKeydown);

    modal.classList.remove('hidden');
    modal.classList.add('flex');
    modal.setAttribute('aria-hidden', 'false');
    okBtn.focus();
  });
};

(function ($) {
  "use strict";

  $(function () {
    // Shared page-level initialisation goes here.
  });
})(jQuery);
