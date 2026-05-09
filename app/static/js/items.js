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

    fetch(apiUrl, { headers: { Accept: "application/json" } })
      .then((r) => r.json())
      .then((body) => {
        if (!body || body.success === false || !body.data) {
          renderAlert(root, "error", body && body.message || "Item not found");
          return;
        }
        renderItem(root, body.data);
        wireWatchlist(root, body.data);
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
 // Trailer video
    const trailerContainer = root.querySelector('[data-field="trailer-container"]');
    const playBtn = root.querySelector('[data-action="play-trailer"]');

    if (trailerContainer && playBtn && data.trailer_url) {

      function toEmbedUrl(url) {
        if (!url) return "";

        const match = url.match(/[?&]v=([^&]+)/);
        if (!match) return "";

        const videoId = match[1];

        return `https://www.youtube.com/embed/${videoId}?autoplay=1&controls=1&rel=0`;
      }

      const embedUrl = toEmbedUrl(data.trailer_url);

      playBtn.addEventListener("click", function () {
        if (!embedUrl) return;

        trailerContainer.innerHTML = `
          <iframe
            class="w-full h-full"
            src="${embedUrl}"
            title="Trailer"
            frameborder="0"
            allow="autoplay; encrypted-media"
            allowfullscreen>
          </iframe>
        `;
      });
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

    renderCommunityCounts(root, data);
  }

  function renderCommunityCounts(root, data) {
    var watching = toInt(data.watching_count);
    var completed = toInt(data.completed_count);
    var planned = toInt(data.planned_count);
    var total = data.watchlist_count != null ? toInt(data.watchlist_count) : watching + completed + planned;
    var barTotal = watching + completed + planned || 1;

    setText(root, "watchlist_count", fmtInt(total));
    setText(root, "watching_count", fmtInt(watching));
    setText(root, "completed_count", fmtInt(completed));
    setText(root, "planned_count", fmtInt(planned));

    setBar(root, "bar-watching", Math.round(watching / barTotal * 100));
    setBar(root, "bar-completed", Math.round(completed / barTotal * 100));
    setBar(root, "bar-planned", Math.round(planned / barTotal * 100));
  }

  /* ---- Watchlist: status buttons + add/remove -------------------- */
  function wireWatchlist(root, data) {
    var btn        = root.querySelector('[data-action="add-to-watchlist"]');
    var label      = btn ? btn.querySelector('[data-field="action-label"]') : null;
    var likeBtn    = root.querySelector('[data-action="toggle-like"]');
    var likeLabel  = likeBtn ? likeBtn.querySelector('[data-field="like-label"]') : null;
    var likeIcon   = likeBtn ? likeBtn.querySelector('[data-field="like-icon"]') : null;
    var statusBtns = [].slice.call(root.querySelectorAll('[data-status-btn]'));

    var currentEntry = null;
    var statusUrl     = '/api/v1/watchlist/status/' + encodeURIComponent(data.id);

    // ── Enable / disable every action button atomically ──────────
    function setAllDisabled(on) {
      statusBtns.forEach(function (b) { b.disabled = on; });
      if (btn) btn.disabled = on;
      if (likeBtn) likeBtn.disabled = on;
    }

    // ── Reflect state in UI (does not touch disabled) ────────────
    function applyState() {
      var currentStatus = currentEntry ? currentEntry.status : null;
      statusBtns.forEach(function (b) {
        b.classList.toggle('on', !!currentStatus && b.dataset.statusBtn === currentStatus);
      });
      if (btn) {
        if (currentStatus) {
          if (label) label.textContent = 'Remove from Watchlist';
          btn.classList.remove('btn--accent');
          btn.classList.add('btn--ghost');
        } else {
          if (label) label.textContent = 'Add to Watchlist';
          btn.classList.add('btn--accent');
          btn.classList.remove('btn--ghost');
        }
      }
      if (likeBtn) {
        var liked = !!(currentEntry && currentEntry.is_liked);
        likeBtn.classList.toggle('btn--accent', liked);
        likeBtn.setAttribute('aria-pressed', liked ? 'true' : 'false');
        if (likeLabel) likeLabel.textContent = liked ? 'Liked' : 'Like';
        if (likeIcon) likeIcon.setAttribute('fill', liked ? 'currentColor' : 'none');
      }
    }

    function resetState() {
      currentEntry = null;
    }

    function refreshCommunityCounts() {
      var apiUrl = root.dataset.apiUrl;
      if (!apiUrl) return Promise.resolve();

      return fetch(apiUrl, { headers: { Accept: "application/json" } })
        .then(function (r) { return r.json(); })
        .then(function (body) {
          if (body && body.success !== false && body.data) {
            renderCommunityCounts(root, body.data);
          }
        })
        .catch(function () {});
    }

    function setStatus(newStatus) {
      if (currentEntry && currentEntry.status === newStatus) return;
      var hadStatus = !!(currentEntry && currentEntry.status);
      var wasLiked = !!(currentEntry && currentEntry.is_liked);
      setAllDisabled(true);
      window.apiFetch(statusUrl, {
        method: 'PUT',
        body: { status: newStatus },
      })
        .then(function (entry) {
          currentEntry = entry || { status: newStatus, is_liked: wasLiked };
          renderAlert(
            root,
            'success',
            hadStatus ? 'Status updated to ' + currentEntry.status + '.' : 'Added to ' + currentEntry.status + ' list.'
          );
          return refreshCommunityCounts();
        })
        .catch(function () { renderAlert(root, 'error', 'Could not update watchlist.'); })
        .finally(function () {
          applyState();
          setAllDisabled(false);
        });
    }

    function setLiked(nextLiked) {
      setAllDisabled(true);
      window.apiFetch(statusUrl, {
        method: 'PUT',
        body: { isLiked: nextLiked },
      })
        .then(function (entry) {
          currentEntry = entry || (nextLiked ? { status: null, is_liked: true } : null);
          renderAlert(root, 'success', nextLiked ? 'Added to your likes.' : 'Removed from your likes.');
        })
        .catch(function () { renderAlert(root, 'error', 'Could not update like.'); })
        .finally(function () {
          applyState();
          setAllDisabled(false);
        });
    }

    // ── Load existing entry ──────────────────────────────────────
    function loadState() {
      if (!window._appUserId) return;
      setAllDisabled(true);
      window.apiFetch(statusUrl)
        .then(function (result) {
          currentEntry = result || null;
        })
        .catch(function () {})
        .finally(function () {
          applyState();
          setAllDisabled(false);
        });
    }

    // ── Status buttons ───────────────────────────────────────────
    statusBtns.forEach(function (statusBtn) {
      statusBtn.addEventListener('click', function () {
        var newStatus = statusBtn.dataset.statusBtn;
        if (!window._appUserId) { window.location.href = '/login'; return; }
        setStatus(newStatus);
      });
    });

    // ── Main Add / Remove button ─────────────────────────────────
    if (btn) {
      btn.addEventListener('click', function () {
        if (btn.disabled) return;
        if (!window._appUserId) { window.location.href = '/login'; return; }

        if (currentEntry && currentEntry.status) {
          // Remove
          setAllDisabled(true);
          window.apiFetch(statusUrl, { method: 'DELETE' })
            .then(function (result) {
              currentEntry = result && result.item ? result.item : null;
              renderAlert(root, 'success', 'Removed from your watchlist.');
              return refreshCommunityCounts();
            })
            .catch(function () { renderAlert(root, 'error', 'Could not remove from watchlist.'); })
            .finally(function () {
              applyState();
              setAllDisabled(false);
            });
        } else {
          // Add starts in Planned; status buttons can set a different status directly.
          if (label) label.textContent = 'Adding…';
          setStatus('planned');
        }
      });
    }

    if (likeBtn) {
      likeBtn.addEventListener('click', function () {
        if (likeBtn.disabled) return;
        if (!window._appUserId) { window.location.href = '/login'; return; }
        setLiked(!(currentEntry && currentEntry.is_liked));
      });
    }

    loadState();
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
  function toInt(n) {
    if (n == null || n === "") return 0;
    var parsed = parseInt(String(n).replace(/,/g, ""), 10);
    return Number.isFinite(parsed) ? parsed : 0;
  }
  function setBar(root, id, pct) {
    var el = root.querySelector("#" + id);
    if (el) el.style.width = Math.max(0, Math.min(100, pct)) + "%";
  }
  function renderAlert(root, kind, html) {
    const slot = root.querySelector('[data-field="alert"]');
    if (!slot) return;
    slot.className = "item-detail__alert item-detail__alert--" + kind;
    slot.innerHTML = html;
  }
})(jQuery);
