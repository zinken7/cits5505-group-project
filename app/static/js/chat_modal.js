(function () {
  'use strict';

  var ME = window._appUserId || 0;
  var socket = null;

  // friendId → { panel, msgs, input, rendered Set }
  var panels = {};
  // friendId → { el (sidebar item), dotEl, name, username }
  var friendItems = {};

  // ── Bootstrap ────────────────────────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', function () {
    socket = io({ transports: ['websocket'] });
    window.whChatSocket = socket;
    document.dispatchEvent(new CustomEvent('wh:socket_ready', { detail: { socket: socket } }));

    socket.on('chat_history', function (data) {
      var fid = data.friend_id;
      if (fid && panels[fid]) renderHistory(fid, data.messages || []);
    });

    socket.on('new_message', function (msg) {
      var fid = msg.sender_id === ME ? msg.recipient_id : msg.sender_id;

      // Auto-open panel when an incoming message arrives and panel is not open
      if (!panels[fid] && msg.sender_id !== ME) {
        var fi = friendItems[fid];
        if (fi) openPanel(fid, fi.name, fi.username);
      }

      if (panels[fid]) {
        appendMsg(fid, msg);
        scrollBottom(fid);
      }

      if (msg.sender_id !== ME) {
        apiFetch('/api/v1/messages/' + msg.sender_id + '/read', { method: 'PATCH' }).catch(function () {});
      }
    });

    socket.on('presence', function (data) {
      setOnlineDot(data.user_id, data.online);
    });

    socket.on('message_error', function (data) {
      console.error('chat_modal:', data.error);
    });

    socket.on('friend_request', function () {
      loadFriendRequests();
    });

    socket.on('friend_accepted', function (data) {
      loadFriends();
      document.dispatchEvent(new CustomEvent('wh:friend_accepted', { detail: data }));
    });

    socket.on('friend_removed', function (data) {
      loadFriends();
      document.dispatchEvent(new CustomEvent('wh:friend_removed', { detail: data }));
    });

    loadFriends();
    loadFriendRequests();
    setInterval(loadFriendRequests, 30000);
  });

  // ── Load friend list ──────────────────────────────────────────────────────
  function loadFriends() {
    var container = document.getElementById('sidebar-friends');
    if (!container) return Promise.resolve([]);

    return apiFetch('/api/v1/friends')
      .then(function (friends) {
        if (!Array.isArray(friends) || !friends.length) {
          container.innerHTML = '<div style="padding:8px 12px;font-size:.78rem;color:var(--muted)">No friends yet</div>';
          return [];
        }
        container.innerHTML = '';
        friends.forEach(function (f) {
          var name = f.displayName || f.username;
          var el = document.createElement('div');
          el.className = 'sidebar-friend';
          el.dataset.friendId = f.id;

          var dotClass = 'sidebar-friend__dot' + (f.online ? '' : ' sidebar-friend__dot--hidden');
          el.innerHTML =
            '<div class="sidebar-friend__av" style="background:' + avatarColor(f.username) + '">' +
              esc(name[0].toUpperCase()) +
            '</div>' +
            '<div class="sidebar-friend__name">' + esc(name) + '</div>' +
            '<div class="' + dotClass + '" data-dot-id="' + f.id + '"></div>';

          el.addEventListener('click', function () {
            openPanel(f.id, name, f.username);
            var sidebar = document.getElementById('app-sidebar');
            var overlay = document.getElementById('sidebar-overlay');
            if (sidebar) sidebar.classList.remove('is-open');
            if (overlay) overlay.classList.remove('is-visible');
            document.body.style.overflow = '';
          });

          container.appendChild(el);
          friendItems[f.id] = {
            el: el,
            dotEl: el.querySelector('[data-dot-id]'),
            name: name,
            username: f.username,
          };
        });
        return friends;
      })
      .catch(function () {
        var c = document.getElementById('sidebar-friends');
        if (c) c.innerHTML = '<div style="padding:8px 12px;font-size:.78rem;color:var(--muted)">Could not load</div>';
        return [];
      });
  }

  // ── Load friend requests ─────────────────────────────────────────────────
  function loadFriendRequests() {
    var wrap      = document.getElementById('sidebar-requests-wrap');
    var container = document.getElementById('sidebar-friend-requests');
    var badge     = document.getElementById('sidebar-req-badge');
    if (!wrap || !container) return;

    apiFetch('/api/v1/friends/requests')
      .then(function (data) {
        var received = (data && data.received) || [];
        wrap.style.display = '';
        if (!received.length) {
          if (badge) badge.textContent = '';
          container.innerHTML = '<div style="padding:8px 12px;font-size:.78rem;color:var(--muted)">No pending requests</div>';
          return;
        }
        if (badge) badge.textContent = received.length;
        container.innerHTML = '';
        received.forEach(function (fs) {
          var sender = fs.requester || {};
          var name   = esc(sender.displayName || sender.username || '?');
          var color  = avatarColor(sender.username || '');
          var el = document.createElement('div');
          el.className = 'sidebar-req';
          el.innerHTML =
            '<div class="sidebar-req__info">' +
              '<div class="sidebar-req__av" style="background:' + color + '">' + esc((sender.displayName || sender.username || '?')[0].toUpperCase()) + '</div>' +
              '<div class="sidebar-req__name">' + name + '</div>' +
            '</div>' +
            '<div class="sidebar-req__actions">' +
              '<button class="sidebar-req__btn sidebar-req__btn--accept" data-fid="' + fs.id + '" data-action="accept">Accept</button>' +
              '<button class="sidebar-req__btn sidebar-req__btn--reject" data-fid="' + fs.id + '" data-action="reject">Reject</button>' +
            '</div>';
          el.querySelectorAll('[data-action]').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
              e.stopPropagation();
              var fid    = btn.dataset.fid;
              var action = btn.dataset.action;
              btn.disabled = true;
              apiFetch('/api/v1/friends/requests/' + fid, {
                method: 'PATCH', body: JSON.stringify({ action: action }),
              }).then(function () {
                if (action === 'accept') loadFriends();
                loadFriendRequests();
              }).catch(function () { btn.disabled = false; });
            });
          });
          container.appendChild(el);
        });
      })
      .catch(function () {});
  }

  // ── Presence dot ──────────────────────────────────────────────────────────
  function setOnlineDot(userId, online) {
    var fi = friendItems[userId];
    if (!fi || !fi.dotEl) return;
    if (online) {
      fi.dotEl.classList.remove('sidebar-friend__dot--hidden');
    } else {
      fi.dotEl.classList.add('sidebar-friend__dot--hidden');
    }
  }

  // ── Panel management ──────────────────────────────────────────────────────
  function openPanel(friendId, displayName, username) {
    if (panels[friendId]) {
      panels[friendId].panel.classList.remove('is-minimized');
      panels[friendId].input.focus();
      return;
    }

    var container = document.getElementById('chat-panels');
    if (!container) return;

    var panel = document.createElement('div');
    panel.className = 'chat-panel';
    panel.dataset.friendId = friendId;

    panel.innerHTML =
      '<div class="chat-panel__head">' +
        '<div class="chat-panel__av" style="background:' + avatarColor(username) + '">' +
          esc(displayName[0].toUpperCase()) +
        '</div>' +
        '<div class="chat-panel__name">' + esc(displayName) + '</div>' +
        '<button class="chat-panel__btn" data-action="minimize" title="Minimise">&#x2013;</button>' +
        '<button class="chat-panel__btn" data-action="close" title="Close">&#x2715;</button>' +
      '</div>' +
      '<div class="chat-panel__body">' +
        '<div class="chat-panel__msgs" id="cp-msgs-' + friendId + '"></div>' +
        '<div class="chat-panel__input-bar">' +
          '<input class="chat-panel__input" type="text" placeholder="Aa" autocomplete="off">' +
          '<button class="chat-panel__send" title="Send">' +
            '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>' +
          '</button>' +
        '</div>' +
      '</div>';

    container.appendChild(panel);

    var msgsEl  = panel.querySelector('.chat-panel__msgs');
    var input   = panel.querySelector('.chat-panel__input');
    var sendBtn = panel.querySelector('.chat-panel__send');
    var head    = panel.querySelector('.chat-panel__head');

    panels[friendId] = { panel: panel, msgs: msgsEl, input: input, rendered: new Set() };

    head.addEventListener('click', function (e) {
      if (e.target.closest('[data-action]')) return;
      window.location.href = '/profile/' + username;
    });

    panel.querySelector('[data-action="minimize"]').addEventListener('click', function (e) {
      e.stopPropagation();
      panel.classList.toggle('is-minimized');
    });

    panel.querySelector('[data-action="close"]').addEventListener('click', function (e) {
      e.stopPropagation();
      panel.remove();
      delete panels[friendId];
    });

    function sendMessage() {
      var body = input.value.trim();
      if (!body) return;
      socket.emit('send_message', { recipient_id: friendId, body: body });
      input.value = '';
      input.focus();
    }

    sendBtn.addEventListener('click', sendMessage);
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' && !e.shiftKey && !e.isComposing && e.keyCode !== 229) {
        e.preventDefault();
        sendMessage();
      }
    });

    socket.emit('join_chat', { friend_id: friendId });
    input.focus();
  }

  // ── Message rendering ─────────────────────────────────────────────────────
  window.openChatPanel = function (friendId) {
    friendId = parseInt(friendId, 10);
    if (!friendId) return Promise.resolve(false);

    if (panels[friendId]) {
      panels[friendId].panel.classList.remove('is-minimized');
      panels[friendId].input.focus();
      return Promise.resolve(true);
    }

    var friend = friendItems[friendId];
    if (friend) {
      openPanel(friendId, friend.name, friend.username);
      return Promise.resolve(true);
    }

    return loadFriends().then(function () {
      var loadedFriend = friendItems[friendId];
      if (!loadedFriend) return false;
      openPanel(friendId, loadedFriend.name, loadedFriend.username);
      return true;
    });
  };

  function renderHistory(friendId, messages) {
    var p = panels[friendId];
    if (!p) return;

    if (!messages.length) {
      if (!p.rendered.size) {
        p.msgs.innerHTML = '<div class="cp-empty">No messages yet. Say hello!</div>';
      }
      return;
    }

    if (p.rendered.size === 0) {
      // Fresh panel — clean render
      messages.forEach(function (msg) { appendMsg(friendId, msg, true); });
      scrollBottom(friendId);
      return;
    }

    // Panel already has messages (auto-open case: the triggering message is already shown).
    // History messages not yet in p.rendered are older — prepend them above existing bubbles.
    var anchor = p.msgs.firstChild;
    var inserted = false;
    messages.forEach(function (msg) {
      if (msg.id && p.rendered.has(msg.id)) return;
      if (msg.id) p.rendered.add(msg.id);
      var empty = p.msgs.querySelector('.cp-empty');
      if (empty) empty.remove();
      var mine = msg.sender_id === ME;
      var el = document.createElement('div');
      el.className = 'cp-msg ' + (mine ? 'cp-msg--mine' : 'cp-msg--theirs');
      el.innerHTML =
        '<div class="cp-bubble">' + renderBody(msg.body, msg.tags || []) + '</div>' +
        '<div class="cp-time">' + fmtTime(msg.created_at) + '</div>';
      p.msgs.insertBefore(el, anchor);
      inserted = true;
    });
    if (inserted) scrollBottom(friendId);
  }

  function appendMsg(friendId, msg, skipScroll) {
    var p = panels[friendId];
    if (!p) return;
    if (msg.id && p.rendered.has(msg.id)) return;
    if (msg.id) p.rendered.add(msg.id);

    var empty = p.msgs.querySelector('.cp-empty');
    if (empty) empty.remove();

    var mine = msg.sender_id === ME;
    var el = document.createElement('div');
    el.className = 'cp-msg ' + (mine ? 'cp-msg--mine' : 'cp-msg--theirs');
    el.innerHTML =
      '<div class="cp-bubble">' + renderBody(msg.body, msg.tags || []) + '</div>' +
      '<div class="cp-time">' + fmtTime(msg.created_at) + '</div>';

    p.msgs.appendChild(el);
    if (!skipScroll) scrollBottom(friendId);
  }

  function renderBody(body, tags) {
    var html = esc(body);
    tags.forEach(function (tag) {
      var placeholder = esc('#' + tag.text);
      var href = tag.url || (tag.imdb_id ? '/items/' + tag.imdb_id : '#');
      var popover = tag.image_url
        ? '<span class="cp-tag-popover"><img src="' + esc(tag.image_url) + '" alt=""><div class="cp-tag-popover__title">' + esc(tag.title) + '</div></span>'
        : '';
      var replacement =
        '<a href="' + esc(href) + '" class="cp-tag" target="_blank" rel="noopener">' +
        placeholder + popover + '</a>';
      html = html.split(placeholder).join(replacement);
    });
    return html;
  }

  function scrollBottom(friendId) {
    var p = panels[friendId];
    if (p && p.msgs) p.msgs.scrollTop = p.msgs.scrollHeight;
  }

  // ── Helpers ───────────────────────────────────────────────────────────────
  function fmtTime(iso) {
    if (!iso) return '';
    return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  function esc(s) {
    return String(s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  var COLORS = ['#6366f1','#8b5cf6','#ec4899','#f59e0b','#10b981','#3b82f6','#ef4444','#14b8a6'];
  function avatarColor(username) {
    var n = 0;
    for (var i = 0; i < (username || '').length; i++) n += username.charCodeAt(i);
    return COLORS[n % COLORS.length];
  }

  function apiFetch(path, opts) {
    if (typeof window.apiFetch === 'function') return window.apiFetch(path, opts);
    return fetch(path, Object.assign({ headers: { Accept: 'application/json' } }, opts || {}))
      .then(function (r) { return r.json(); });
  }
})();
