/**
 * Search users page.
 * Depends on: window.apiFetch (main.js)
 */

var activeController = null;

(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    bindControls();
    var q = (window._searchUsersInitialQ || '').trim();
    if (q) doSearch(q);
  });

  // ── Search ────────────────────────────────────────────────────────
function doSearch(q) {
  setCount('Searching…');
  setSkeletons();
  updateHeading(q);

  window.history.replaceState(
    null,
    '',
    '/search-users?q=' + encodeURIComponent(q)
  );

  // Cancel previous request
  if (activeController) {
    activeController.abort();
  }

  activeController = new AbortController();

  window.apiFetch(
    '/api/v1/users/search?q=' + encodeURIComponent(q) + '&limit=50',
    {
      signal: activeController.signal
    }
  )
    .then(function (response) {
      var users = Array.isArray(response)
        ? response
        : (response.data || []);

      render(q, users);
    })
    .catch(function (err) {
      if (err.name === 'AbortError') return;

      console.error(err);
      setCount('Search failed.');
      renderUsers([], q);
    });
}

  function render(q, users) {
    renderUsers(users, q);
    var total = users.length;
    setCount(total + ' user' + (total !== 1 ? 's' : '') +
      ' found for &ldquo;<span class="text-foreground">' + esc(q) + '</span>&rdquo;');
  }

  // ── Users rendering ───────────────────────────────────────────────
  function renderUsers(users, q) {
    var list = document.getElementById('users-list');
    if (!list) return;

    if (!users.length) {
      list.innerHTML = '<div class="text-center py-12 text-muted">' +
        '<div class="text-lg mb-2">No users found</div>' +
        '<p>Try a different search term.</p>' +
        '</div>';
      return;
    }

    list.innerHTML = users.map(userCard).join('');
  }

  function setSkeletons() {
    var list = document.getElementById('users-list');
    if (!list) return;
    list.innerHTML = '<div class="users-skeleton">' +
      [1,2,3,4,5,6,7,8,9,10].map(function () {
        return '<div class="user-skeleton animate-pulse flex items-center gap-4 p-4">' +
          '<div class="avatar-skel w-12 h-12 bg-gray-200 rounded-full"></div>' +
          '<div class="flex-1">' +
            '<div class="h-4 bg-gray-200 rounded w-32 mb-2"></div>' +
            '<div class="h-3 bg-gray-200 rounded w-48"></div>' +
          '</div>' +
        '</div>';
      }).join('') +
      '</div>';
  }

  function updateHeading(q) {
    var h = document.getElementById('search-users-heading');
    if (h) h.innerHTML = 'Results for <em>' + esc(q) + '</em>';
  }

  // ── User card HTML ────────────────────────────────────────────────
  function userCard(user) {
    var username = esc(user.username || '');
    var displayName = esc(user.displayName || username);
    var bio = esc(user.bio || '');
    var href = '/profile/' + username;

    return '<a href="' + href + '" class="user-card flex items-center gap-4 p-4 hover:bg-gray-50 rounded-lg transition-colors">' +
      '<div class="avatar w-12 h-12 bg-gray-300 rounded-full flex items-center justify-center text-white font-bold">' +
        displayName.charAt(0).toUpperCase() +
      '</div>' +
      '<div class="flex-1 min-w-0">' +
        '<div class="font-medium text-foreground">' + displayName + '</div>' +
        '<div class="text-sm text-muted">@' + username + '</div>' +
        (bio ? '<div class="text-sm text-muted mt-1">' + bio + '</div>' : '') +
      '</div>' +
      '<div class="text-sm text-muted">View profile →</div>' +
    '</a>';
  }

  // ── Controls ──────────────────────────────────────────────────────
  function bindControls() {
    // Refine input
    var searchInput = document.getElementById('search-users-q');
    if (searchInput) {
      var timer;
      searchInput.addEventListener('input', function () {
        clearTimeout(timer);
        var q = searchInput.value.trim();
        if (q.length >= 1) {
          timer = setTimeout(function () { doSearch(q); }, 350);
        } else if (!q) {
          clearAll();
        }
      });
      searchInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
          clearTimeout(timer);
          var q = searchInput.value.trim();
          if (q.length >= 1) doSearch(q);
        }
        if (e.key === 'Escape') { searchInput.value = ''; clearAll(); }
      });
    }
  }

  // ── Helpers ───────────────────────────────────────────────────────
  function clearAll() {
    setCount('');
    var list = document.getElementById('users-list');
    if (list) list.innerHTML = '<div class="text-center py-12 text-muted">' +
      '<div class="text-lg mb-2">Start typing to search for users</div>' +
      '<p>Find friends by their username or display name</p>' +
      '</div>';
    document.getElementById('search-users-heading').innerHTML = 'Find friends';
    window.history.replaceState(null, '', '/search-users');
  }

  function setCount(html) {
    var el = document.getElementById('users-result-count');
    if (el) el.innerHTML = html;
  }

  function esc(s) {
    return String(s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }
})();