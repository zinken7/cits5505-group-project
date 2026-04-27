/**
 * Search results page — 3 sections (Movies / Anime / TV Shows).
 * Depends on: window.apiFetch (main.js)
 */
(function () {
  'use strict';

  var currentSort = 'relevant';

  document.addEventListener('DOMContentLoaded', function () {
    bindControls();
    var q = (window._searchInitialQ || '').trim();
    if (q) doSearch(q);
  });

  // ── Search ────────────────────────────────────────────────────────
  function doSearch(q) {
    setCount('Searching…');
    setSkeletons();
    hideNoResults();
    updateSeeAllLinks(q);
    updateHeading(q);
    window.history.replaceState(null, '', '/search?q=' + encodeURIComponent(q));

    window.apiFetch('/api/v1/search?q=' + encodeURIComponent(q) + '&limit=100')
      .then(function (items) { render(q, items || []); })
      .catch(function () {
        setCount('Search failed.');
        renderSection('movie', [], q);
        renderSection('anime', [], q);
        renderSection('tvshow', [], q);
      });
  }

  function render(q, items) {
    var movies  = items.filter(function (d) { return d.media_type === 'movie';  });
    var anime   = items.filter(function (d) { return d.media_type === 'anime';  });
    var tvshows = items.filter(function (d) { return d.media_type === 'tvshow'; });

    sortItems(movies);
    sortItems(anime);
    sortItems(tvshows);

    renderSection('movie',  movies,  q);
    renderSection('anime',  anime,   q);
    renderSection('tvshow', tvshows, q);

    var total = items.length;
    setCount(total + ' result' + (total !== 1 ? 's' : '') +
      ' for &ldquo;<span class="text-foreground">' + esc(q) + '</span>&rdquo;');

    if (!total) showNoResults();
  }

  function sortItems(arr) {
    if (currentSort === 'rating') {
      arr.sort(function (a, b) { return (b.rating || 0) - (a.rating || 0); });
    } else if (currentSort === 'new') {
      arr.sort(function (a, b) { return (b.year || 0) - (a.year || 0); });
    }
    // 'relevant' keeps API order
  }

  // ── Section rendering ─────────────────────────────────────────────
  function renderSection(type, items, q) {
    var section = document.getElementById('section-' + type);
    var rail    = document.getElementById('rail-' + type);

    if (!section || !rail) return;

    if (!items.length) {
      section.style.display = 'none';
      return;
    }

    section.style.display = '';
    rail.innerHTML = items.map(mcard).join('');
  }

  function setSkeletons() {
    ['movie', 'anime', 'tvshow'].forEach(function (type) {
      var section = document.getElementById('section-' + type);
      var rail    = document.getElementById('rail-' + type);
      var count   = document.getElementById('count-' + type);
      if (section) section.style.display = '';
      if (rail) {
        rail.innerHTML = [1,2,3,4,5,6].map(function () {
          return '<div class="mcard-skeleton animate-pulse" style="width:160px">' +
            '<div class="mcard-skel__poster"></div>' +
            '<div class="mcard-skel__title mt-2.5"></div>' +
            '<div class="mcard-skel__subtitle mt-1.5"></div>' +
          '</div>';
        }).join('');
      }
    });
  }

  function updateSeeAllLinks(q) {
    var types = { movie: 'movie', anime: 'anime', tvshow: 'tvshow' };
    Object.keys(types).forEach(function (type) {
      var el = document.getElementById('seeall-' + type);
      if (el) el.href = '/explore?type=' + type + '&q=' + encodeURIComponent(q);
    });
  }

  function updateHeading(q) {
    var h = document.getElementById('search-heading');
    if (h) h.innerHTML = 'Results for <em>' + esc(q) + '</em>';
  }

  // ── Media card HTML ───────────────────────────────────────────────
  function mcard(item) {
    var mtype     = item.media_type || 'movie';
    var typeLabel = { movie: 'Movie', anime: 'Anime', tvshow: 'TV Show' }[mtype] || mtype;
    var typeEmoji = { movie: '🎬', anime: '📺', tvshow: '📺' }[mtype] || '';
    var genres    = item.genres || [];
    var href      = item.imdb_id ? '/items/' + esc(item.imdb_id) : '#';
    var imgSrc    = item.image_url || '';
    var rating    = item.rating != null ? parseFloat(item.rating).toFixed(1) : '—';
    var w         = (item.watching_count || 0) + (item.completed_count || 0) + (item.planned_count || 0);
    var tracking  = w ? fmt(w) + ' tracking' : '';

    var poster = imgSrc
      ? '<img src="' + esc(imgSrc) + '" alt="' + esc(item.title || '') + '" loading="lazy">'
      : '<div class="mcard__poster-empty">' + typeEmoji + '</div>';

    return '<a href="' + href + '" class="mcard">' +
      '<div class="mcard__poster">' +
        poster +
        '<div class="mcard__badge"><span class="pill mcard__type-pill">' + typeLabel + '</span></div>' +
        '<div class="mcard__rating">★ ' + rating + '</div>' +
        '<div class="mcard__hover"><div class="mcard__hover__inner">' +
          (tracking ? '<div class="mcard__tracking">' + tracking + '</div>' : '') +
          '<button class="mcard__hover__btn" onclick="event.preventDefault();window.location.href=\'' + href + '\'">View details →</button>' +
        '</div></div>' +
      '</div>' +
      '<div class="mcard__meta">' +
        '<div class="mcard__type">' + (genres[0] || typeLabel) + ' · ' + (item.year || '') + '</div>' +
        '<div class="mcard__title">' + esc(item.title || 'Untitled') + '</div>' +
      '</div>' +
    '</a>';
  }

  // ── Controls ──────────────────────────────────────────────────────
  function bindControls() {
    // Refine input
    var searchInput = document.getElementById('search-q');
    if (searchInput) {
      var timer;
      searchInput.addEventListener('input', function () {
        clearTimeout(timer);
        var q = searchInput.value.trim();
        if (q.length >= 2) {
          timer = setTimeout(function () { doSearch(q); }, 350);
        } else if (!q) {
          clearAll();
        }
      });
      searchInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
          clearTimeout(timer);
          var q = searchInput.value.trim();
          if (q.length >= 2) doSearch(q);
        }
        if (e.key === 'Escape') { searchInput.value = ''; clearAll(); }
      });
    }

    // Sort
    var sortCtrl = document.getElementById('sort-filter');
    if (sortCtrl) {
      sortCtrl.addEventListener('click', function (e) {
        var btn = e.target.closest('button[data-sort]');
        if (!btn) return;
        currentSort = btn.dataset.sort;
        sortCtrl.querySelectorAll('button').forEach(function (b) { b.classList.remove('on'); });
        btn.classList.add('on');
        // Re-search with current query using new sort
        var q = (document.getElementById('search-q') || {}).value || window._searchInitialQ || '';
        q = q.trim();
        if (q.length >= 2) doSearch(q);
      });
    }
  }

  // ── Helpers ───────────────────────────────────────────────────────
  function clearAll() {
    setCount('');
    ['movie', 'anime', 'tvshow'].forEach(function (type) {
      var section = document.getElementById('section-' + type);
      var rail    = document.getElementById('rail-' + type);
      if (section) section.style.display = 'none';
      if (rail)    rail.innerHTML = '';
    });
    hideNoResults();
    document.getElementById('search-heading').innerHTML = 'Search everything.';
    window.history.replaceState(null, '', '/search');
  }

  function setCount(html) {
    var el = document.getElementById('result-count');
    if (el) el.innerHTML = html;
  }

  function showNoResults() {
    var el = document.getElementById('no-results');
    if (el) el.classList.remove('hidden');
  }

  function hideNoResults() {
    var el = document.getElementById('no-results');
    if (el) el.classList.add('hidden');
  }

  function fmt(n) {
    if (n >= 1e6) return (n / 1e6).toFixed(1).replace(/\.0$/, '') + 'M';
    if (n >= 1e3) return (n / 1e3).toFixed(n >= 1e4 ? 0 : 1).replace(/\.0$/, '') + 'K';
    return String(n);
  }

  function esc(s) {
    return String(s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }
})();
