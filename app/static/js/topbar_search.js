(function () {
  'use strict';

  var MOBILE_BP = 640; // px — below this, topbar icon opens modal instead of dropdown

  // ── Shared helpers ────────────────────────────────────────────────
  function isMobile() { return window.innerWidth < MOBILE_BP; }

  function buildItem(item) {
    var type  = item.media_type === 'tvshow' ? 'TV Show'
              : item.media_type === 'anime'  ? 'Anime'
              : 'Movie';
    var poster = item.image_url
      ? '<img src="' + esc(item.image_url) + '" alt="" loading="lazy">'
      : '<div class="tsearch-item__poster-placeholder">🎬</div>';
    var year   = item.year   ? '<span class="tsearch-item__dot">·</span><span class="tsearch-item__year">' + item.year + '</span>' : '';
    var rating = item.rating ? '<span class="tsearch-item__dot">·</span><span class="tsearch-item__rating">★ ' + parseFloat(item.rating).toFixed(1) + '</span>' : '';
    var href   = item.imdb_id ? '/items/' + esc(item.imdb_id) : '/search?q=' + encodeURIComponent(item.title || '');
    return '<a class="tsearch-item" href="' + href + '">' +
      '<div class="tsearch-item__poster">' + poster + '</div>' +
      '<div class="tsearch-item__body">' +
        '<div class="tsearch-item__title">' + esc(item.title || '') + '</div>' +
        '<div class="tsearch-item__meta">' +
          '<span class="tsearch-item__type">' + esc(type) + '</span>' + year + rating +
        '</div>' +
      '</div>' +
    '</a>';
  }

  function applyFocus(items, idx) {
    items.forEach(function (el, i) { el.classList.toggle('is-focused', i === idx); });
  }
  function clearFocus(items) {
    items.forEach(function (el) { el.classList.remove('is-focused'); });
  }
  function esc(s) {
    return String(s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  // ══════════════════════════════════════════════════════════════════
  // ⌘K MODAL — defined first so topbar can call openModal()
  // ══════════════════════════════════════════════════════════════════
  var backdrop   = document.getElementById('tsearch-backdrop');
  var modal      = document.getElementById('tsearch-modal');
  var modalInput = document.getElementById('tsearch-modal-input');
  var modalClose = document.getElementById('tsearch-close');
  var modalRes   = document.getElementById('tsearch-modal-results');
  var modalView  = document.getElementById('tsearch-modal-viewall');

  var isOpen    = false;
  var mTimer    = null;
  var mLastQ    = '';
  var mFocusIdx = -1;

  function openModal() {
    if (isOpen) return;
    isOpen = true;
    if (backdrop) backdrop.hidden = false;
    if (modal)    modal.hidden    = false;
    document.body.style.overflow = 'hidden';
    if (modalInput) { modalInput.focus(); modalInput.select(); }
  }

  function closeModal() {
    if (!isOpen) return;
    isOpen = false;
    if (backdrop) backdrop.hidden = true;
    if (modal)    modal.hidden    = true;
    document.body.style.overflow = '';
    mFocusIdx = -1;
  }

  if (modal && modalInput) {
    if (modalClose) modalClose.addEventListener('click', closeModal);

    if (backdrop) {
      backdrop.addEventListener('click', function (e) {
        if (e.target === backdrop) closeModal();
      });
    }

    modalInput.addEventListener('input', function () {
      var q = modalInput.value.trim();
      clearTimeout(mTimer);
      if (q.length < 2) { mLastQ = ''; modalRes.innerHTML = ''; updateModalFooter(''); return; }
      if (q === mLastQ) return;
      mTimer = setTimeout(function () { doModalSearch(q); }, 220);
    });

    modalInput.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { closeModal(); return; }
      var items = modalRes.querySelectorAll('.tsearch-item');
      if (!items.length) return;
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        mFocusIdx = Math.min(mFocusIdx + 1, items.length - 1);
        applyFocus(items, mFocusIdx);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        if (mFocusIdx <= 0) { mFocusIdx = -1; clearFocus(items); modalInput.focus(); }
        else { mFocusIdx--; applyFocus(items, mFocusIdx); }
      } else if (e.key === 'Enter' && mFocusIdx >= 0) {
        e.preventDefault();
        items[mFocusIdx].click();
      }
    });

    function doModalSearch(q) {
      mLastQ = q; mFocusIdx = -1;
      modalRes.innerHTML = '<div class="tsearch-loading">Searching…</div>';
      updateModalFooter(q);
      window.apiFetch('/api/v1/search?q=' + encodeURIComponent(q) + '&limit=8')
        .then(function (items) { renderModal(q, items || []); })
        .catch(function () { modalRes.innerHTML = '<div class="tsearch-empty">Something went wrong.</div>'; });
    }

    function renderModal(q, items) {
      modalRes.innerHTML = items.length
        ? items.map(buildItem).join('')
        : '<div class="tsearch-empty">No results for <strong>' + esc(q) + '</strong></div>';
      updateModalFooter(q);
    }

    function updateModalFooter(q) {
      if (!modalView) return;
      modalView.href = q ? '/search?q=' + encodeURIComponent(q) : '/search';
      var label = modalView.querySelector('span');
      if (label) label.textContent = q ? 'See all results for "' + q + '"' : 'See all results';
    }
  }

  // ⌘K / Ctrl+K toggle
  document.addEventListener('keydown', function (e) {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      isOpen ? closeModal() : openModal();
    }
  });

  // ══════════════════════════════════════════════════════════════════
  // TOPBAR INLINE SEARCH (desktop only — mobile click opens modal)
  // ══════════════════════════════════════════════════════════════════
  var input   = document.getElementById('tsearch-input');
  var drop    = document.getElementById('tsearch-drop');
  var results = document.getElementById('tsearch-results');
  var viewall = document.getElementById('tsearch-viewall');

  var wrap = document.getElementById('topbar-search');
  if (wrap) {
    wrap.addEventListener('click', function (e) {
      if (isMobile()) { openModal(); return; }
      if (e.target !== input) input.focus();
    });
  }

  if (input && drop) {
    var timer    = null;
    var lastQ    = '';
    var focusIdx = -1;

    input.addEventListener('input', function () {
      if (isMobile()) return;
      var q = input.value.trim();
      clearTimeout(timer);
      if (q.length < 2) { hideDrop(); lastQ = ''; return; }
      if (q === lastQ)  { showDrop(); return; }
      timer = setTimeout(function () { doInlineSearch(q); }, 220);
    });

    input.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { hideDrop(); input.blur(); return; }
      var items = drop.querySelectorAll('.tsearch-item');
      if (!items.length) return;
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        focusIdx = Math.min(focusIdx + 1, items.length - 1);
        applyFocus(items, focusIdx);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        if (focusIdx <= 0) { focusIdx = -1; clearFocus(items); input.focus(); }
        else { focusIdx--; applyFocus(items, focusIdx); }
      } else if (e.key === 'Enter' && focusIdx >= 0) {
        e.preventDefault();
        items[focusIdx].click();
      }
    });

    input.addEventListener('focus', function () {
      if (isMobile()) { input.blur(); openModal(); return; }
      if (lastQ && input.value.trim() === lastQ) showDrop();
    });

    document.addEventListener('click', function (e) {
      if (wrap && !wrap.contains(e.target)) hideDrop();
    });

    function doInlineSearch(q) {
      lastQ    = q;
      focusIdx = -1;
      results.innerHTML = '<div class="tsearch-loading">Searching…</div>';
      showDrop();
      window.apiFetch('/api/v1/search?q=' + encodeURIComponent(q) + '&limit=8')
        .then(function (items) { renderInline(q, items || []); })
        .catch(function () {
          results.innerHTML = '<div class="tsearch-empty">Something went wrong.</div>';
        });
    }

    function renderInline(q, items) {
      results.innerHTML = items.length
        ? items.map(buildItem).join('')
        : '<div class="tsearch-empty">No results for <strong>' + esc(q) + '</strong></div>';
      if (viewall) {
        viewall.href = '/search?q=' + encodeURIComponent(q);
        var label = viewall.querySelector('span');
        if (label) label.textContent = 'See all results for "' + q + '"';
      }
    }

    function showDrop() { if (!isMobile()) drop.hidden = false; }
    function hideDrop() { drop.hidden = true; focusIdx = -1; }
  }
})();
