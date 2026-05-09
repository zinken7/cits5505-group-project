(function () {
  'use strict';

  var socket = null;
  var currentFriendId = null;
  var currentUserId = window._chatUserId || 0;
  var renderedIds = new Set();

  document.addEventListener('DOMContentLoaded', function () {
    socket = io({ transports: ['websocket'] });
    window.whChatSocket = socket;
    document.dispatchEvent(new CustomEvent('wh:socket_ready', { detail: { socket: socket } }));

    socket.on('chat_history', function (data) {
      renderHistory(data.messages || []);
    });

    socket.on('new_message', function (msg) {
      appendMessage(msg);
      scrollBottom();
      if (msg.sender_id !== currentUserId) {
        apiFetch('/api/v1/messages/' + msg.sender_id + '/read', { method: 'PATCH' }).catch(function () {});
      }
    });

    socket.on('message_error', function (data) {
      console.error('Chat error:', data.error);
    });

    // Friend list clicks
    document.getElementById('friend-list').addEventListener('click', function (e) {
      var item = e.target.closest('[data-friend-id]');
      if (!item) return;
      selectFriend(parseInt(item.dataset.friendId), item.dataset.friendName);
    });

    // Send message
    var form = document.getElementById('msg-form');
    var input = document.getElementById('msg-input');
    if (form) {
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        var body = input.value.trim();
        if (!body || !currentFriendId) return;
        socket.emit('send_message', { recipient_id: currentFriendId, body: body });
        input.value = '';
      });
    }
  });

  function selectFriend(friendId, name) {
    currentFriendId = friendId;

    // Update active state
    document.querySelectorAll('[data-friend-id]').forEach(function (el) {
      el.classList.toggle('is-active', parseInt(el.dataset.friendId) === friendId);
    });

    // Update header
    var header = document.getElementById('chat-header-name');
    if (header) header.textContent = name;

    // Show window, hide placeholder
    document.getElementById('chat-placeholder').style.display = 'none';
    document.getElementById('chat-window').style.display = 'flex';

    // Clear messages and join room
    document.getElementById('chat-messages').innerHTML = '';
    renderedIds.clear();
    socket.emit('join_chat', { friend_id: friendId });
  }

  function renderHistory(messages) {
    var container = document.getElementById('chat-messages');
    container.innerHTML = '';
    if (!messages.length) {
      container.innerHTML = '<div class="chat-empty">No messages yet. Say hello!</div>';
      return;
    }
    messages.forEach(function (msg) { appendMessage(msg, true); });
    scrollBottom();
  }

  function appendMessage(msg, skipScroll) {
    if (msg.id && renderedIds.has(msg.id)) return;
    if (msg.id) renderedIds.add(msg.id);
    var container = document.getElementById('chat-messages');
    var mine = msg.sender_id === currentUserId;
    var el = document.createElement('div');
    el.className = 'chat-msg ' + (mine ? 'chat-msg--mine' : 'chat-msg--theirs');

    var bodyHtml = renderBody(msg.body, msg.tags || []);
    el.innerHTML =
      '<div class="chat-bubble">' + bodyHtml + '</div>' +
      '<div class="chat-meta">' + fmtTime(msg.created_at) + '</div>';

    container.appendChild(el);
    if (!skipScroll) scrollBottom();
  }

  function renderBody(body, tags) {
    var html = esc(body);
    tags.forEach(function (tag) {
      var placeholder = '#' + tag.text;
      var href = tag.url || (tag.imdb_id ? '/items/' + tag.imdb_id : '#');
      var popover = tag.image_url
        ? '<div class="media-tag-popover"><img src="' + esc(tag.image_url) + '" alt=""><div class="media-tag-popover__title">' + esc(tag.title) + '</div></div>'
        : '';
      var replacement =
        '<a href="' + esc(href) + '" class="media-tag" target="_blank" rel="noopener">' +
        esc(placeholder) + popover + '</a>';
      html = html.split(esc(placeholder)).join(replacement);
    });
    return html;
  }

  function scrollBottom() {
    var c = document.getElementById('chat-messages');
    if (c) c.scrollTop = c.scrollHeight;
  }

  function fmtTime(iso) {
    if (!iso) return '';
    var d = new Date(iso);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  function esc(s) {
    return String(s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function apiFetch(path, opts) {
    if (typeof window.apiFetch === 'function') return window.apiFetch(path, opts);
    return fetch(path, Object.assign({ headers: { Accept: 'application/json' } }, opts || {})).then(function (r) { return r.json(); });
  }
})();
