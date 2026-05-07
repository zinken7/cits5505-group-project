/**
 * Item detail page JavaScript
 * ----------------------------
 * Loaded only on detail.html — fetches /api/v1/items/<imdb_id> and renders
 * all data fields, genres badges, credits, community counts, and the
 * "Add to Watchlist" action.
 *
 * Expects jQuery ($) to be available globally.
 */
(function ($) {
  "use strict";

  $(function () {
    const $detail = $('[data-page="item-detail"]');
    if ($detail.length) initItemDetail($detail[0]);
  });

  /* ================================================================
     Item detail page — fetch /api/v1/items/<imdb_id> and inject data
     ================================================================ */
  function initItemDetail(root) {
    const apiUrl = root.dataset.apiUrl;
    const watchlistUrl = root.dataset.watchlistUrl;

    fetch(apiUrl, { headers: { Accept: "application/json" } })
      .then((r) => r.json())
      .then((body) => {
        if (!body || body.success === false || !body.data) {
          renderAlert(root, "error", body && body.message || "Item not found");
          return;
        }
        renderItem(root, body.data);
        wireWatchlist(root, body.data, watchlistUrl);
        wireShare(root, body.data);
      })
      .catch(() => renderAlert(root, "error", "Could not load item. Please try again."));
  }

  function renderItem(root, data) {
    document.title = `${data.title || "Item"} — WatchList Hub`;

    setText(root, "title", data.title);
    setText(root, "media_type", data.media_type);
    setText(root, "description", data.description || "No description available.");
    setText(root, "status", data.status || "—");
    setText(root, "rating", data.rating != null ? `${data.rating} / 10` : "—");

    // Year appears twice: in the meta row and in the stats grid.
    const year = data.year != null ? String(data.year) : "";
    setText(root, "year", year);
    setText(root, "year-stat", year || "—");
    toggle(root, "year-sep", !!year);

    // Runtime — only for movies (with minutes)
    const runtime = data.runtime_minutes ? `${data.runtime_minutes} min` : "";
    setText(root, "runtime", runtime);
    toggle(root, "runtime-sep", !!runtime && !!year);

    // Episodes — only shown for media with episode counts (anime / TV)
    const epsNode = root.querySelector('[data-field-wrap="episodes"]');
    if (epsNode) {
      if (data.episodes != null && data.episodes !== "") {
        epsNode.classList.remove("hidden");
        setText(root, "episodes", String(data.episodes));
      } else {
        epsNode.classList.add("hidden");
      }
    }

    // Tagline
    const $tag = root.querySelector('[data-field="tagline"]');
    if ($tag) {
      if (data.tagline) {
        $tag.textContent = `"${data.tagline}"`;
        $tag.classList.remove("hidden");
      } else {
        $tag.classList.add("hidden");
      }
    }

    // Image + imdb link
    const img = root.querySelector('[data-field="image_url"]');
    if (img && data.image_url) {
      img.src = data.image_url;
      img.alt = data.title || "";
    }
    const imdbLink = root.querySelector('[data-field="imdb_url"]');
    if (imdbLink) {
      if (data.imdb_url) {
        imdbLink.href = data.imdb_url;
      } else {
        imdbLink.classList.add("hidden");
      }
    }

    // Genres — render as badges
    const genresHost = root.querySelector('[data-field="genres"]');
    if (genresHost) {
      genresHost.innerHTML = "";
      (data.genres || []).forEach((g) => {
        const span = document.createElement("span");
        span.className = "detail-badge";
        span.textContent = g;
        genresHost.appendChild(span);
      });
      genresHost.classList.toggle("hidden", (data.genres || []).length === 0);
    }

    // Credits block — each wrap hides when field is empty
    setOptional(root, "director", data.director);
    setOptional(root, "cast", (data.cast || []).join(", "));
    setOptional(root, "language", data.language);
    setOptional(root, "country", data.country);
    setOptional(root, "awards", data.awards);

    // Community counts
    setText(root, "watchlist_count", fmtInt(data.watchlist_count));
    setText(root, "watching_count", fmtInt(data.watching_count));
    setText(root, "completed_count", fmtInt(data.completed_count));
    setText(root, "planned_count", fmtInt(data.planned_count));
  }

  /* ---- Watchlist: status buttons + add/remove -------------------- */
  function wireWatchlist(root, data, watchlistUrl) {
    var btn        = root.querySelector('[data-action="add-to-watchlist"]');
    var label      = btn ? btn.querySelector('[data-field="action-label"]') : null;
    var statusBtns = [].slice.call(root.querySelectorAll('[data-status-btn]'));

    var currentEntry  = null; // { id, status } when item is already in watchlist
    var selectedStatus = 'planned';

    // ── Load existing entry ──────────────────────────────────────
    function loadState() {
      if (!window._appUserId) return;
      window.apiFetch('/api/v1/watchlist')
        .then(function (result) {
          var items = Array.isArray(result) ? result : [];
          for (var i = 0; i < items.length; i++) {
            if (items[i].media_id === data.id) {
              currentEntry = { id: items[i].id, status: items[i].status };
              selectedStatus = items[i].status;
              break;
            }
          }
          applyState();
        })
        .catch(function () {});
    }

    // ── Reflect state in UI ──────────────────────────────────────
    function applyState() {
      var active = currentEntry ? currentEntry.status : null;
      statusBtns.forEach(function (b) {
        b.classList.toggle('on', !!active && b.dataset.statusBtn === active);
      });
      if (btn) {
        if (currentEntry) {
          if (label) label.textContent = 'Remove from Watchlist';
          btn.classList.remove('btn--accent');
          btn.classList.add('btn--ghost');
        } else {
          if (label) label.textContent = 'Add to Watchlist';
          btn.classList.add('btn--accent');
          btn.classList.remove('btn--ghost');
        }
        btn.disabled = false;
      }
    }

    // ── Status buttons ───────────────────────────────────────────
    statusBtns.forEach(function (statusBtn) {
      statusBtn.addEventListener('click', function () {
        var newStatus = statusBtn.dataset.statusBtn;
        if (!window._appUserId) { window.location.href = '/login'; return; }
        statusBtns.forEach(function (b) { b.disabled = true; });

        if (currentEntry) {
          // Already in list — update status
          window.apiFetch('/api/v1/watchlist/' + currentEntry.id, {
            method: 'PATCH',
            body: JSON.stringify({ status: newStatus }),
          })
            .then(function () {
              currentEntry.status = newStatus;
              selectedStatus = newStatus;
              applyState();
              renderAlert(root, 'success', 'Status updated to ' + newStatus + '.');
            })
            .catch(function () { renderAlert(root, 'error', 'Could not update status.'); })
            .finally(function () { statusBtns.forEach(function (b) { b.disabled = false; }); });
        } else {
          // Not in list — add with this status
          window.apiFetch(watchlistUrl, {
            method: 'POST',
            body: JSON.stringify({ mediaType: data.media_type, mediaId: data.id, status: newStatus }),
          })
            .then(function (entry) {
              currentEntry = { id: entry.id, status: entry.status || newStatus };
              selectedStatus = currentEntry.status;
              applyState();
              renderAlert(root, 'success', 'Added to ' + currentEntry.status + ' list.');
            })
            .catch(function () {
              renderAlert(root, 'error', 'Could not add to watchlist.');
              statusBtns.forEach(function (b) { b.disabled = false; });
            });
        }
      });
    });

    // ── Main Add / Remove button ─────────────────────────────────
    if (btn) {
      btn.addEventListener('click', function () {
        if (btn.disabled) return;
        if (!window._appUserId) { window.location.href = '/login'; return; }
        btn.disabled = true;

        if (currentEntry) {
          // Remove
          window.apiFetch('/api/v1/watchlist/' + currentEntry.id, { method: 'DELETE' })
            .then(function () {
              currentEntry = null;
              selectedStatus = 'planned';
              applyState();
              renderAlert(root, 'success', 'Removed from your watchlist.');
            })
            .catch(function () {
              btn.disabled = false;
              renderAlert(root, 'error', 'Could not remove from watchlist.');
            });
        } else {
          // Add with currently selected status
          if (label) label.textContent = 'Adding…';
          window.apiFetch(watchlistUrl, {
            method: 'POST',
            body: JSON.stringify({ mediaType: data.media_type, mediaId: data.id, status: selectedStatus }),
          })
            .then(function (entry) {
              currentEntry = { id: entry.id, status: entry.status || selectedStatus };
              selectedStatus = currentEntry.status;
              applyState();
              renderAlert(root, 'success', 'Added to ' + currentEntry.status + ' list.');
            })
            .catch(function () {
              if (label) label.textContent = 'Add to Watchlist';
              btn.disabled = false;
              renderAlert(root, 'error', 'Could not add to watchlist.');
            });
        }
      });
    }

    loadState();
  }

  /* ---- Share: choose friends + send media link -------------------- */
  function wireShare(root, data) {
    var openBtn = root.querySelector('[data-action="open-share"]');
    var modal = document.getElementById('share-modal');
    if (!openBtn || !modal) return;

    var friendList = document.getElementById('share-friend-list');
    var empty = document.getElementById('share-empty');
    var error = document.getElementById('share-error');
    var sendBtn = modal.querySelector('[data-action="send-share"]');
    var selectedCount = document.getElementById('share-selected-count');
    var closeBtns = [].slice.call(modal.querySelectorAll('[data-action="close-share"]'));
    var friendsLoaded = false;

    function showError(message) {
      if (!error) return;
      error.textContent = message || "";
      error.classList.toggle("hidden", !message);
    }

    function selectedFriendIds() {
      if (!friendList) return [];
      return [].slice.call(friendList.querySelectorAll('input[type="checkbox"]:checked'))
        .map(function (input) { return input.value; });
    }

    function updateSendState() {
      var count = selectedFriendIds().length;
      if (sendBtn) sendBtn.disabled = count === 0;
      if (selectedCount) {
        selectedCount.textContent = count
          ? count + ' friend' + (count === 1 ? '' : 's') + ' selected'
          : 'No friends selected';
      }
    }

    function friendRow(friend) {
      var name = friend.displayName || friend.username || "Friend";
      var username = friend.username ? "@" + friend.username : "";
      var initials = name.split(" ").map(function (part) { return part[0] || ""; }).join("").slice(0, 2).toUpperCase();
      return '<label class="flex items-center gap-3 cursor-pointer" style="padding:10px 12px;border:1px solid var(--rule);border-radius:10px;background:var(--card-bg-2)">' +
        '<input type="checkbox" value="' + esc(friend.id) + '" style="width:16px;height:16px">' +
        '<span class="avatar avatar--sm" style="background:var(--accent)">' + esc(initials || "?") + '</span>' +
        '<span class="min-w-0">' +
          '<span class="block font-semibold text-sm">' + esc(name) + '</span>' +
          '<span class="block text-xs text-muted">' + esc(username) + '</span>' +
        '</span>' +
      '</label>';
    }

    function renderFriends(friends) {
      if (!friendList || !empty) return;
      if (!friends.length) {
        friendList.innerHTML = "";
        empty.classList.remove("hidden");
        updateSendState();
        return;
      }
      empty.classList.add("hidden");
      friendList.innerHTML = friends.map(friendRow).join("");
      friendList.querySelectorAll('input[type="checkbox"]').forEach(function (input) {
        input.addEventListener("change", updateSendState);
      });
      updateSendState();
    }

    function loadFriends() {
      if (friendsLoaded) return Promise.resolve();
      if (friendList) friendList.innerHTML = '<div class="text-sm text-muted">Loading friends...</div>';
      if (empty) empty.classList.add("hidden");
      return window.apiFetch('/api/v1/friends')
        .then(function (friends) {
          friendsLoaded = true;
          renderFriends(Array.isArray(friends) ? friends : []);
        })
        .catch(function () {
          if (friendList) friendList.innerHTML = "";
          showError("Could not load friends.");
        });
    }

    function openModal() {
      showError("");
      if (friendList) {
        friendList.querySelectorAll('input[type="checkbox"]').forEach(function (input) {
          input.checked = false;
        });
      }
      updateSendState();
      modal.classList.remove("hidden");
      modal.classList.add("flex");
      modal.setAttribute("aria-hidden", "false");
      loadFriends();
    }

    function closeModal() {
      modal.classList.add("hidden");
      modal.classList.remove("flex");
      modal.setAttribute("aria-hidden", "true");
      showError("");
      updateSendState();
    }

    openBtn.addEventListener("click", function () {
      if (!window._appUserId) { window.location.href = "/login"; return; }
      openModal();
    });

    closeBtns.forEach(function (btn) {
      btn.addEventListener("click", closeModal);
    });

    modal.addEventListener("click", function (event) {
      if (event.target === modal) closeModal();
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && !modal.classList.contains("hidden")) closeModal();
    });

    if (sendBtn) {
      sendBtn.addEventListener("click", function () {
        var ids = selectedFriendIds();
        if (!ids.length || sendBtn.disabled) return;
        sendBtn.disabled = true;
        sendBtn.textContent = 'Sending...';
        showError("");

        window.apiFetch('/api/v1/share/media', {
          method: 'POST',
          body: { mediaId: data.id, recipientIds: ids.map(Number) },
        })
          .then(function () {
            closeModal();
            renderAlert(root, "success", "Shared with " + ids.length + " friend" + (ids.length === 1 ? "." : "s."));
          })
          .catch(function (err) {
            showError((err && err.message) || "Could not share this title.");
          })
          .finally(function () {
            sendBtn.textContent = 'Send share';
            updateSendState();
          });
      });
    }
  }

  /* ---- helpers ---------------------------------------------------- */
  function setText(root, field, value) {
    root.querySelectorAll(`[data-field="${field}"]`).forEach((el) => {
      el.textContent = value == null ? "" : String(value);
    });
  }
  function toggle(root, field, visible) {
    root.querySelectorAll(`[data-field="${field}"]`).forEach((el) => {
      el.classList.toggle("hidden", !visible);
    });
  }
  function setOptional(root, field, value) {
    const wrap = root.querySelector(`[data-field-wrap="${field}"]`);
    const node = root.querySelector(`[data-field="${field}"]`);
    const hasValue = value != null && String(value).trim() !== "";
    if (node) node.textContent = hasValue ? value : "";
    if (wrap) wrap.classList.toggle("hidden", !hasValue);
  }
  function fmtInt(n) {
    if (n == null) return "0";
    return Number(n).toLocaleString();
  }
  function renderAlert(root, kind, html) {
    const slot = root.querySelector('[data-field="alert"]');
    if (!slot) return;
    slot.className = "item-detail__alert item-detail__alert--" + kind;
    slot.innerHTML = html;
  }
  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }
})(jQuery);
