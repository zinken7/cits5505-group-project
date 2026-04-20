/**
 * Team / page-level JavaScript (layout pages only)
 * -------------------------------------------------
 * Loaded after app/static/js/ui.js — jQuery ($) and window.UI are available.
 * Vite entry (theme, UI.init on #app, etc.) runs as a module in <head>.
 *
 * Use [data-page="…"] from the server to branch behaviour per route.
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
        wireAddToWatchlist(root, body.data, watchlistUrl);
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
        $tag.textContent = `“${data.tagline}”`;
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

  /* ---- Watchlist action ------------------------------------------- */
  function wireAddToWatchlist(root, data, watchlistUrl) {
    const btn = root.querySelector('[data-action="add-to-watchlist"]');
    if (!btn) return;

    btn.addEventListener("click", () => {
      if (btn.disabled) return;
      btn.disabled = true;
      const label = btn.querySelector('[data-field="action-label"]');
      const original = label ? label.textContent : btn.textContent;
      if (label) label.textContent = "Adding…";

      fetch(watchlistUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        credentials: "same-origin",
        body: JSON.stringify({
          mediaType: data.media_type,
          mediaId: data.media_id,
          status: "planned",
        }),
      })
        .then((r) => r.json().then((body) => ({ status: r.status, body })))
        .then(({ status, body }) => {
          if (status === 201) {
            if (label) label.textContent = "Added to Planned ✓";
            renderAlert(root, "success", "Added to your Planned list.");
          } else if (status === 401) {
            if (label) label.textContent = original;
            btn.disabled = false;
            renderAlert(
              root,
              "error",
              'You need to <a class="underline" href="/login">sign in</a> to use your watchlist.'
            );
          } else {
            if (label) label.textContent = original;
            btn.disabled = false;
            renderAlert(root, "error", (body && body.message) || "Could not add to watchlist.");
          }
        })
        .catch(() => {
          if (label) label.textContent = original;
          btn.disabled = false;
          renderAlert(root, "error", "Network error. Please try again.");
        });
    });
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
})(jQuery);
