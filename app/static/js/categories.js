(function () {
  'use strict';

  var EXPLORE_BASE = '/explore';
  var currentGenre = '';

  document.addEventListener('DOMContentLoaded', function () {
    // Read initial genre from the active button
    var activeBtn = document.querySelector('.cat-genre-btn--active');
    if (activeBtn) currentGenre = activeBtn.dataset.genre || '';

    document.getElementById('cat-genre-cloud').addEventListener('click', function (e) {
      var btn = e.target.closest('button[data-genre]');
      if (!btn || btn.dataset.genre === currentGenre) return;
      switchGenre(btn.dataset.genre);
    });

    window.addEventListener('popstate', function (e) {
      var genre = (e.state && e.state.genre) || defaultGenre();
      switchGenre(genre, false);
    });
  });

  function defaultGenre() {
    return new URLSearchParams(window.location.search).get('genre') || 'Drama';
  }

  function switchGenre(genre, pushState) {
    if (pushState !== false) {
      history.pushState({ genre: genre }, '', '/categories?genre=' + encodeURIComponent(genre));
    }
    currentGenre = genre;
    updateChips(genre);
    updateHeading(genre);
    updateSeeAllLinks(genre);
    fetchAll(genre);
  }

  function updateChips(genre) {
    document.querySelectorAll('button[data-genre]').forEach(function (btn) {
      var active = btn.dataset.genre === genre;
      btn.classList.toggle('cat-genre-btn--active', active);
      btn.classList.toggle('cat-genre-btn--idle', !active);
    });
  }

  function updateHeading(genre) {
    var h = document.getElementById('cat-heading');
    if (h) h.textContent = genre;
    document.querySelectorAll('.cat-genre-label').forEach(function (el) {
      el.textContent = genre.toLowerCase();
    });
  }

  function updateSeeAllLinks(genre) {
    var enc = encodeURIComponent(genre);
    [['seeall-movie', 'movie'], ['seeall-anime', 'anime'], ['seeall-tvshow', 'tvshow']].forEach(function (pair) {
      var el = document.getElementById(pair[0]);
      if (el) el.href = EXPLORE_BASE + '?type=' + pair[1] + '&genre=' + enc;
    });
  }

  function fetchAll(genre) {
    var enc = encodeURIComponent(genre);
    var apis = [
      { id: 'movie',  url: '/api/v1/movies?genre='  + enc + '&sort=-rating&limit=16' },
      { id: 'anime',  url: '/api/v1/anime?genre='   + enc + '&sort=-rating&limit=16' },
      { id: 'tvshow', url: '/api/v1/tvshows?genre=' + enc + '&sort=-rating&limit=16' },
    ];

    apis.forEach(function (api) {
      setRailLoading(api.id, true);
    });

    apis.forEach(function (api) {
      apiFetch(api.url).then(function (result) {
        var items = Array.isArray(result) ? result : ((result && result.data) || []);
        var total = (result && result.meta && result.meta.total) != null ? result.meta.total : items.length;
        setRailLoading(api.id, false);
        renderRail(api.id, items, genre);
        updateCount(api.id, total);
      }).catch(function () {
        setRailLoading(api.id, false);
      });
    });
  }

  function setRailLoading(type, on) {
    var rail = document.getElementById('rail-' + type);
    if (rail) rail.classList.toggle('cat-rail--loading', on);
  }

  function updateCount(type, total) {
    var el = document.getElementById('count-' + type);
    if (el) el.textContent = total + ' title' + (total !== 1 ? 's' : '');
  }

  function renderRail(type, items, genre) {
    var rail = document.getElementById('rail-' + type);
    if (!rail) return;
    if (!items.length) {
      var label = { movie: 'movies', anime: 'anime', tvshow: 'TV shows' }[type] || type;
      rail.innerHTML = '<div class="cat-empty">No ' + label + ' tagged ' + esc(genre.toLowerCase()) + ' yet.</div>';
      return;
    }
    rail.innerHTML = items.map(mcard).join('');
  }

  // ── Minimal mcard renderer ────────────────────────────────────────
  function mcard(item) {
    var mtype = item.media_type || 'movie';
    var typeLabel = { movie: 'Movie', anime: 'Anime', tvshow: 'TV Show' }[mtype] || mtype;
    var typeEmoji = mtype === 'movie' ? '🎬' : '📺';
    var imdbId = item.imdb_id || '';
    var href = imdbId ? '/items/' + imdbId : '#';
    var imgSrc = item.image_url || '';
    var rating = item.rating != null ? parseFloat(item.rating).toFixed(1) : '—';
    var genres = item.genres || [];

    var poster = imgSrc
      ? '<img src="' + esc(imgSrc) + '" alt="' + esc(item.title || '') + '" loading="lazy" style="width:100%;height:100%;object-fit:cover">'
      : '<div style="display:flex;align-items:center;justify-content:center;height:100%;font-size:2rem;background:var(--card-bg-2)">' + typeEmoji + '</div>';

    return '<a href="' + href + '" class="mcard">' +
      '<div class="mcard__poster">' +
        poster +
        '<div class="mcard__badge"><span class="pill text-white" style="background:rgba(0,0,0,.72);border:0">' + typeLabel + '</span></div>' +
        '<div class="mcard__rating">★ ' + rating + '</div>' +
        '<div class="mcard__hover"><div class="mcard__hover__inner">' +
          '<button class="mcard__hover__btn" onclick="event.preventDefault();window.location.href=\'' + href + '\'">View details →</button>' +
        '</div></div>' +
      '</div>' +
      '<div class="mcard__meta">' +
        '<div class="mcard__type">' + esc(genres[0] || typeLabel) + ' · ' + (item.year || '') + '</div>' +
        '<div class="mcard__title">' + esc(item.title || 'Untitled') + '</div>' +
      '</div>' +
    '</a>';
  }

  // ── Helpers ───────────────────────────────────────────────────────
  function apiFetch(path) {
    if (typeof window.apiFetch === 'function') return window.apiFetch(path);
    return fetch(path, { headers: { Accept: 'application/json' } }).then(function (r) { return r.json(); });
  }

  function esc(s) {
    return String(s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }
})();
