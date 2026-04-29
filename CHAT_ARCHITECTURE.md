# Chat Engine Architecture

## Overview

Real-time private messaging between friends, implemented with Flask-SocketIO (server) and Socket.IO v4 (browser client). Messages are persisted in SQLite via the `Message` model. Only accepted friends can exchange messages.

---

## Components

| File | Role |
|------|------|
| `app/sockets/chat.py` | All Socket.IO event handlers + online presence state |
| `app/services/message_service.py` | DB read/write for messages, friendship guard |
| `app/services/friend_service.py` | Friend list, `are_friends` check |
| `app/services/tag_service.py` | Resolves `#Title` tags to Media records |
| `app/api/v1/friends.py` | REST — friend list (includes online flag), friend requests |
| `app/api/v1/messages.py` | REST — conversation history, mark-read, unread count |
| `app/static/js/chat_modal.js` | Browser: sidebar friend list, floating chat panels, socket handling |
| `app/templates/app_layout.html` | Injects `#sidebar-friends`, `#chat-panels`, Socket.IO CDN, `chat_modal.js` |

---

## Room Design

Two types of Socket.IO rooms per connected user:

### Personal room — `user_{id}`
- Joined automatically on every `connect` event.
- Used to **deliver messages** and **presence notifications**.
- Every authenticated socket is always in exactly one personal room.

### Chat room — `chat_{min(a,b)}_{max(a,b)}`
- Joined when a user opens a chat panel (`join_chat` event).
- Used only to **fetch history** (`chat_history` response is scoped to the requesting socket, not broadcast to the room).
- Not used for message delivery (personal rooms handle that).

---

## Connection Lifecycle

```
Browser                          Server (chat.py)
  |                                    |
  |--- WebSocket connect() ---------->|
  |                                    | on_connect:
  |                                    |   _online[uid].add(sid)
  |                                    |   join_room("user_{uid}")
  |                                    |   emit "presence" {online:true}
  |                                    |     → to each friend's "user_{fid}"
  |                                    |
  |--- disconnect ------------------>|
  |                                    | on_disconnect:
  |                                    |   _online[uid].discard(sid)
  |                                    |   if last sid gone:
  |                                    |     emit "presence" {online:false}
  |                                    |       → to each friend's "user_{fid}"
```

Multiple tabs are handled correctly: `_online[uid]` is a **set of SIDs**. The user is considered offline only when the last tab disconnects.

---

## Sending a Message

```
Sender browser                   Server                    Recipient browser
  |                                  |                             |
  | emit "send_message"              |                             |
  |   {recipient_id, body} -------> |                             |
  |                                  | message_service.send_message:
  |                                  |   are_friends(sender, recipient) → guard
  |                                  |   INSERT Message → DB commit
  |                                  |   tag_service.resolve_tags(body)
  |                                  |   return msg dict (id, body, tags, timestamps)
  |                                  |                             |
  |                                  | emit "new_message" msg      |
  |                                  |   → to "user_{sender_id}"  |
  | <--- new_message --------------- |                             |
  |   appendMsg(panel)               |                             |
  |                                  | emit "new_message" msg      |
  |                                  |   → to "user_{recipient_id}"|
  |                                  | --------------------------> |
  |                                  |                    new_message handler:
  |                                  |                      if panel not open → openPanel()
  |                                  |                      appendMsg(panel)
  |                                  |                      mark_read via REST
```

**Key rule**: messages are delivered exclusively via **personal rooms**, never via the chat room. This guarantees each party receives exactly one copy regardless of how many panels are open.

---

## Opening a Chat Panel

```
Browser                          Server
  |                                  |
  | (click friend in sidebar)        |
  | openPanel(friendId)              |
  |   create panel DOM               |
  |   panels[fid] = { ... }          |
  |                                  |
  | emit "join_chat" {friend_id} --> |
  |                                  | on_join_chat:
  |                                  |   are_friends() → guard
  |                                  |   join_room("chat_{a}_{b}")
  |                                  |   get_conversation(limit=50) from DB
  |                                  |   mark_read()
  |                                  |   emit "chat_history" {friend_id, messages}
  |                                  |     → to requesting socket only
  | <--- chat_history --------------- |
  |   renderHistory():               |
  |     clear DOM + rendered Set     |
  |     appendMsg() for each msg     |
```

---

## Auto-Open on Incoming Message

When a `new_message` arrives and the recipient has **no panel open** for that sender:

1. `new_message` handler detects `panels[fid]` is null and `sender_id !== ME`.
2. Calls `openPanel(fid, ...)` — creates the panel DOM, registers it in `panels`.
3. `openPanel` emits `join_chat` → server returns `chat_history`.
4. Execution continues: `appendMsg` adds the triggering message to the (now-existing) panel.
5. When `chat_history` arrives shortly after, `renderHistory` clears the DOM and re-renders the full history (which includes the triggering message). The `p.rendered` Set deduplicates any overlap.

---

## Presence System

```
User A connects
  → server emits "presence" {user_id: A, online: true}
      → to "user_{B}" for each friend B of A

User B's browser receives "presence"
  → setOnlineDot(A, true) — shows green dot next to A in sidebar

User A disconnects (last tab)
  → server emits "presence" {user_id: A, online: false}
      → to "user_{B}" for each friend B of A
```

Initial online state is embedded in the `GET /api/v1/friends` response (`online: bool` field), so the sidebar is correct immediately on page load without waiting for a socket event.

---

## Deduplication

Messages are deduplicated at the panel level using a **per-panel `rendered` Set** (keyed on `msg.id`):

- `appendMsg` checks `p.rendered.has(msg.id)` before inserting into the DOM.
- `renderHistory` calls `p.rendered.clear()` and `p.msgs.innerHTML = ''` before re-rendering, so history is always authoritative.
- Because only personal rooms are used for delivery, a message is never broadcast to the same socket twice.

---

## Media Tags

Messages support `#Title` inline references (e.g. `#Inception`). Tags are resolved at **read time**, not stored:

1. `tag_service.resolve_tags(body)` — regex matches `#Word` patterns, looks up `Media.title` case-insensitively.
2. Returns a list of `{text, imdb_id, title, image_url}` objects bundled with the message dict.
3. Client `renderBody()` replaces each `#Title` occurrence with an `<a class="cp-tag">` link containing a hover popover (poster + title).

---

## REST API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/v1/friends` | List accepted friends with `online` flag |
| `GET` | `/api/v1/friends/requests` | Pending sent/received requests |
| `POST` | `/api/v1/friends/requests` | Send a friend request |
| `PATCH` | `/api/v1/friends/requests/<id>` | Accept or reject a request |
| `DELETE` | `/api/v1/friends/<id>` | Remove a friendship |
| `GET` | `/api/v1/friends/status/<user_id>` | Friendship status with a specific user |
| `GET` | `/api/v1/messages/<user_id>` | Conversation history (paginated) |
| `PATCH` | `/api/v1/messages/<user_id>/read` | Mark all messages from user as read |
| `GET` | `/api/v1/messages/unread` | Total unread count |

---

## Data Model

```
Message
  id          INTEGER  PK
  sender_id   FK → users.id
  recipient_id FK → users.id
  body        TEXT
  created_at  DATETIME  (UTC, indexed)
  read_at     DATETIME  nullable

Friendship
  id            INTEGER  PK
  requester_id  FK → users.id
  addressee_id  FK → users.id
  status        ENUM(pending, accepted, rejected)
  created_at    DATETIME
  updated_at    DATETIME
  UNIQUE(requester_id, addressee_id)
```

`Message.to_dict()` uses `strftime('%Y-%m-%dT%H:%M:%SZ')` for timestamps so the browser parses them as UTC regardless of SQLite's lack of timezone storage.
