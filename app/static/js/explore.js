/**
 * Explore page — fetches all media from the API and renders an interactive grid.
 * Depends on: window.apiFetch (main.js), jQuery (base.html)
 */
(function () {
  'use strict';

  var allItems = [];
  var currentType  = window._exploreInitialType || 'all';
  var currentGenre = 'All';
  var currentSort  = 'trending';
  var currentQ     = '';

  // ── Boot ──────────────────────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', function () {
    var params = new URLSearchParams(window.location.search);
    currentQ = (document.getElementById('search-q') || {}).value || '';
    if (params.get('type')) currentType = params.get('type');
    if (params.get('genre')) currentGenre = params.get('genre');
    loadData();
    bindControls();
  });

  // ── Data loading ─────────────────────────────────────────────────
  function loadData() {
    var fetches = [
      apiFetch('/api/v1/movies?limit=100&sort=-releaseYear'),
      apiFetch('/api/v1/anime?limit=100'),
      apiFetch('/api/v1/tvshows?limit=100'),
      apiFetch('/api/v1/trending?limit=10'),
    ];

    Promise.all(fetches).then(function (results) {
      // window.apiFetch already unwraps the envelope → result is the array directly.
      // The raw-fetch fallback returns the full envelope, so handle both shapes.
      function unwrap(r) { return Array.isArray(r) ? r : ((r && r.data) || []); }
      var movies   = unwrap(results[0]);
      var anime    = unwrap(results[1]);
      var tvshows  = unwrap(results[2]);
      var trending = unwrap(results[3]);

      allItems = movies.concat(anime, tvshows);
      renderTrending(trending);
      buildGenreChips();
      applyFilters();
    }).catch(function (err) {
      console.error('Explore load error:', err);
      document.getElementById('result-count').textContent = 'Failed to load.';
    });
  }

  // ── Trending rail ─────────────────────────────────────────────────
  function renderTrending(items) {
    var rail = document.getElementById('trending-rail');
    if (!rail) return;
    if (!items.length) {
      document.getElementById('trending-section').style.display = 'none';
      return;
    }
    rail.innerHTML = items.map(function (item, i) {
      return mcard(item, '', i + 1);
    }).join('');
  }

  // ── Genre chips ───────────────────────────────────────────────────
  function buildGenreChips() {
    var set = new Set(['All']);
    allItems.forEach(function (d) {
      (d.genres || []).forEach(function (g) { set.add(g); });
    });
    var genres = ['All'].concat(Array.from(set).filter(function (g) { return g !== 'All'; }).sort());
    var container = document.getElementById('genre-chips');
    if (!container) return;
    container.innerHTML = genres.map(function (g) {
      return '<span class="chip' + (g === currentGenre ? ' is-on' : '') + '" data-genre="' + esc(g) + '">' + esc(g) + '</span>';
    }).join('');
    container.querySelectorAll('.chip').forEach(function (c) {
      c.addEventListener('click', function () {
        currentGenre = c.dataset.genre;
        container.querySelectorAll('.chip').forEach(function (x) { x.classList.remove('is-on'); });
        c.classList.add('is-on');
        applyFilters();
      });
    });
  }

  // ── Filtering ─────────────────────────────────────────────────────
  function applyFilters() {
    var q = currentQ.toLowerCase().trim();
    var filtered = allItems.filter(function (d) {
      if (currentType !== 'all' && d.media_type !== currentType) return false;
      if (currentGenre !== 'All' && !(d.genres || []).includes(currentGenre)) return false;
      if (q) {
        var inTitle  = (d.title || '').toLowerCase().includes(q);
        var inGenres = (d.genres || []).join(' ').toLowerCase().includes(q);
        if (!inTitle && !inGenres) return false;
      }
      return true;
    });

    if (currentSort === 'rating') {
      filtered.sort(function (a, b) { return (b.rating || 0) - (a.rating || 0); });
    } else if (currentSort === 'new') {
      filtered.sort(function (a, b) { return (b.year || 0) - (a.year || 0); });
    } else {
      // trending = sort by watchlist_count desc, fall back to rank
      filtered.sort(function (a, b) {
        return ((b.watchlist_count || 0) + (b.votes || 0)) - ((a.watchlist_count || 0) + (a.votes || 0));
      });
    }

    renderGrid(filtered, q);

    // Show/hide trending section only when no filters active
    var trendSection = document.getElementById('trending-section');
    if (trendSection) {
      trendSection.style.display = (!q && currentType === 'all' && currentGenre === 'All') ? '' : 'none';
    }
  }

  function renderGrid(items, q) {
    var grid = document.getElementById('results-grid');
    var noResults = document.getElementById('no-results');
    var countEl = document.getElementById('result-count');

    if (countEl) {
      countEl.innerHTML = items.length + ' result' + (items.length !== 1 ? 's' : '') +
        (q ? ' for &ldquo;<span class="text-foreground">' + esc(q) + '</span>&rdquo;' : '');
    }

    if (!items.length) {
      if (grid) grid.style.display = 'none';
      if (noResults) noResults.style.display = '';
      return;
    }

    if (noResults) noResults.style.display = 'none';
    if (grid) {
      grid.style.display = '';
      grid.innerHTML = items.map(function (item) { return mcard(item); }).join('');
    }
  }

  // ── Media card HTML ───────────────────────────────────────────────
  function mcard(item, status, rank) {
    var mtype = item.media_type || 'movie';
    var typeLabel = { movie: 'Movie', anime: 'Anime', tvshow: 'TV Show' }[mtype] || mtype;
    var typeEmoji = { movie: '🎬', anime: '📺', tvshow: '📺' }[mtype] || '';
    var genres = item.genres || [];
    var imdbId = item.imdb_id || '';
    var href = imdbId ? '/items/' + imdbId : '#';
    var imgSrc = item.image_url || '';
    var rating = item.rating != null ? parseFloat(item.rating).toFixed(1) : '—';
    var w = (item.watching_count || 0) + (item.completed_count || 0) + (item.planned_count || 0);
    var tracking = w ? fmt(w) + ' tracking' : '';

    var poster = imgSrc
      ? '<img src="' + esc(imgSrc) + '" alt="' + esc(item.title || '') + '" loading="lazy">'
      : '<div class="mcard__poster-empty">' + typeEmoji + '</div>';

    var statusPill = status ? '<div class="mcard__status"><span class="pill pill--' + status + '">' + status + '</span></div>' : '';
    var rankBadge  = rank != null ? '<div class="mcard__rating mcard__rating--rank">#' + rank + '</div>'
                                  : '<div class="mcard__rating">★ ' + rating + '</div>';

    return '<a href="' + href + '" class="mcard">' +
      '<div class="mcard__poster">' +
        poster +
        '<div class="mcard__badge"><span class="pill mcard__type-pill">' + typeLabel + '</span></div>' +
        statusPill +
        rankBadge +
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
    // Search
    var searchInput = document.getElementById('search-q');
    if (searchInput) {
      var timer;
      searchInput.addEventListener('input', function () {
        clearTimeout(timer);
        timer = setTimeout(function () {
          currentQ = searchInput.value;
          applyFilters();
        }, 220);
      });
      searchInput.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') { searchInput.value = ''; currentQ = ''; applyFilters(); }
      });
    }

    // Type filter
    var typeCtrl = document.getElementById('type-filter');
    if (typeCtrl) {
      // Set initial state from URL param
      if (currentType !== 'all') {
        typeCtrl.querySelectorAll('button').forEach(function (b) {
          b.classList.toggle('on', b.dataset.type === currentType);
        });
      }
      typeCtrl.addEventListener('click', function (e) {
        var btn = e.target.closest('button[data-type]');
        if (!btn) return;
        currentType = btn.dataset.type;
        typeCtrl.querySelectorAll('button').forEach(function (b) { b.classList.remove('on'); });
        btn.classList.add('on');
        applyFilters();
      });
    }

    // Sort filter
    var sortCtrl = document.getElementById('sort-filter');
    if (sortCtrl) {
      sortCtrl.addEventListener('click', function (e) {
        var btn = e.target.closest('button[data-sort]');
        if (!btn) return;
        currentSort = btn.dataset.sort;
        sortCtrl.querySelectorAll('button').forEach(function (b) { b.classList.remove('on'); });
        btn.classList.add('on');
        applyFilters();
      });
    }
  }

  // ── Helpers ───────────────────────────────────────────────────────
  function apiFetch(path) {
    if (typeof window.apiFetch === 'function') {
      return window.apiFetch(path);
    }
    return fetch(path, { headers: { Accept: 'application/json' } }).then(function (r) { return r.json(); });
  }

  function fmt(n) {
    if (n >= 1e6) return (n / 1e6).toFixed(1).replace(/\.0$/, '') + 'M';
    if (n >= 1e3) return (n / 1e3).toFixed(n >= 1e4 ? 0 : 1).replace(/\.0$/, '') + 'K';
    return String(n);
  }

  function esc(s) {
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }
})();
