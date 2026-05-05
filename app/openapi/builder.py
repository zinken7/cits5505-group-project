# -*- coding: utf-8 -*-
"""Programmatic OpenAPI 3.1 document for Watchlist Hub (served at /openapi.json)."""


def _ref(name):
    return {"$ref": f"#/components/schemas/{name}"}


def _ok_response():
    return {
        "200": {
            "description": "Successful Response",
            "content": {"application/json": {"schema": _ref("APIResponse")}},
        },
        "422": {
            "description": "Validation Error",
            "content": {"application/json": {"schema": _ref("HTTPValidationError")}},
        },
    }


def _created_response():
    return {
        "201": {
            "description": "Created",
            "content": {"application/json": {"schema": _ref("APIResponse")}},
        },
        "422": _ok_response()["422"],
    }


def _only_200():
    """Responses block with a single 200 and no 422."""
    return {"200": _ok_response()["200"]}


def _paths():
    """All paths match Flask routes under /api/v1 (root health at /api/v1)."""
    api = _ref("APIResponse")
    val = _ref("HTTPValidationError")

    def op(tag, summary, method, extra=None):
        base = {
            "tags": [tag],
            "summary": summary,
            "responses": {
                "200": {
                    "description": "Successful Response",
                    "content": {"application/json": {"schema": api}},
                },
                "422": {
                    "description": "Validation Error",
                    "content": {"application/json": {"schema": val}},
                },
            },
        }
        if extra:
            base.update(extra)
        return {method: base}

    p = {}

    p["/api/v1"] = op("System", "API root / health check", "get")

    p["/api/v1/auth/register"] = {
        "post": {
            "tags": ["Auth"],
            "summary": "Register a new user",
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": _ref("RegisterRequest")}},
            },
            "responses": _created_response(),
        }
    }
    p["/api/v1/auth/login"] = {
        "post": {
            "tags": ["Auth"],
            "summary": "Log in with username or email",
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": _ref("LoginRequest")}},
            },
            "responses": _ok_response(),
        }
    }
    p["/api/v1/auth/logout"] = {
        "post": {
            "tags": ["Auth"],
            "summary": "Log out the current session",
            "responses": {
                "200": {
                    "description": "Successful Response",
                    "content": {"application/json": {"schema": api}},
                }
            },
        }
    }
    p["/api/v1/auth/session"] = {
        "get": {
            "tags": ["Auth"],
            "summary": "Get the current session",
            "responses": {
                "200": {
                    "description": "Successful Response",
                    "content": {"application/json": {"schema": api}},
                }
            },
        }
    }

    p["/api/v1/users/me"] = {
        "get": {
            "tags": ["Users"],
            "summary": "Get the current user's private profile",
            "responses": _only_200(),
        },
        "patch": {
            "tags": ["Users"],
            "summary": "Update the current user's profile",
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": _ref("UserUpdateRequest")}},
            },
            "responses": _ok_response(),
        },
    }

    uid = {
        "name": "user_id",
        "in": "path",
        "required": True,
        "schema": {"type": "string", "title": "User Id"},
    }
    p["/api/v1/users/{user_id}"] = {
        "get": {
            "tags": ["Users"],
            "summary": "Get a public profile by user ID",
            "parameters": [uid],
            "responses": _ok_response(),
        }
    }

    p["/api/v1/users/{user_id}/watchlist"] = {
        "get": {
            "tags": ["Users"],
            "summary": "Get a user's public watchlist",
            "parameters": [
                uid,
                {"name": "status", "in": "query", "schema": {"type": "string"}},
                {"name": "mediaType", "in": "query", "schema": {"type": "string"}},
                {"name": "q", "in": "query", "schema": {"type": "string"}},
                {"name": "sort", "in": "query", "schema": {"type": "string", "default": "-updatedAt"}},
                {"name": "limit", "in": "query", "schema": {"type": "integer", "default": 12}},
                {"name": "offset", "in": "query", "schema": {"type": "integer", "default": 0}},
            ],
            "responses": _ok_response(),
        }
    }

    p["/api/v1/users/me/watchlist"] = {
        "get": {
            "tags": ["Users"],
            "summary": "Get the current user's watchlist",
            "responses": _only_200(),
        }
    }

    media_q = [
        {"name": "q", "in": "query", "schema": {"type": "string"}},
        {"name": "genre", "in": "query", "schema": {"type": "string"}},
        {"name": "sort", "in": "query", "schema": {"type": "string"}},
        {"name": "limit", "in": "query", "schema": {"type": "integer", "default": 24}},
        {"name": "offset", "in": "query", "schema": {"type": "integer", "default": 0}},
    ]
    p["/api/v1/anime"] = {
        "get": {
            "tags": ["Anime"],
            "summary": "List anime",
            "parameters": media_q,
            "responses": _ok_response(),
        }
    }
    p["/api/v1/anime/{anime_id}"] = {
        "get": {
            "tags": ["Anime"],
            "summary": "Get anime details",
            "parameters": [
                {
                    "name": "anime_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                }
            ],
            "responses": _ok_response(),
        }
    }
    p["/api/v1/tvshows"] = {
        "get": {
            "tags": ["TV Shows"],
            "summary": "List TV shows",
            "parameters": media_q,
            "responses": _ok_response(),
        }
    }
    p["/api/v1/tvshows/{tvshow_id}"] = {
        "get": {
            "tags": ["TV Shows"],
            "summary": "Get TV show details",
            "parameters": [
                {
                    "name": "tvshow_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                }
            ],
            "responses": _ok_response(),
        }
    }
    p["/api/v1/movies"] = {
        "get": {
            "tags": ["Movies"],
            "summary": "List movies",
            "parameters": media_q,
            "responses": _ok_response(),
        }
    }
    p["/api/v1/movies/{movie_id}"] = {
        "get": {
            "tags": ["Movies"],
            "summary": "Get movie details",
            "parameters": [
                {
                    "name": "movie_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                }
            ],
            "responses": _ok_response(),
        }
    }
    wl_q = [
        {"name": "status", "in": "query", "schema": {"type": "string"}},
        {"name": "mediaType", "in": "query", "schema": {"type": "string"}},
        {"name": "q", "in": "query", "schema": {"type": "string"}},
        {"name": "sort", "in": "query", "schema": {"type": "string"}},
        {"name": "limit", "in": "query", "schema": {"type": "integer", "default": 20}},
        {"name": "offset", "in": "query", "schema": {"type": "integer", "default": 0}},
    ]
    p["/api/v1/watchlist"] = {
        "get": {
            "tags": ["Watchlist"],
            "summary": "Get the current user's watchlist",
            "parameters": wl_q,
            "responses": _ok_response(),
        },
        "post": {
            "tags": ["Watchlist"],
            "summary": "Create a watchlist entry",
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": _ref("WatchlistCreateRequest")}},
            },
            "responses": _created_response(),
        },
    }
    p["/api/v1/watchlist/{entry_id}"] = {
        "get": {
            "tags": ["Watchlist"],
            "summary": "Get one watchlist entry",
            "parameters": [
                {
                    "name": "entry_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                }
            ],
            "responses": _ok_response(),
        },
        "patch": {
            "tags": ["Watchlist"],
            "summary": "Update a watchlist entry",
            "parameters": [
                {
                    "name": "entry_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                }
            ],
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": _ref("WatchlistUpdateRequest")}},
            },
            "responses": _ok_response(),
        },
        "delete": {
            "tags": ["Watchlist"],
            "summary": "Delete a watchlist entry",
            "parameters": [
                {
                    "name": "entry_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                }
            ],
            "responses": _ok_response(),
        },
    }

    p["/api/v1/trending"] = {
        "get": {
            "tags": ["Leaderboards"],
            "summary": "Trending media (optional type filter)",
            "parameters": [
                {
                    "name": "type",
                    "in": "query",
                    "schema": {"type": "string", "enum": ["anime", "movie", "tvshow"]},
                },
                {"name": "limit", "in": "query", "schema": {"type": "integer", "default": 10}},
            ],
            "responses": _ok_response(),
        }
    }

    lb_params = [
        {
            "name": "type",
            "in": "query",
            "schema": {"type": "string", "enum": ["anime", "movie", "tvshow"], "default": "anime"},
        },
        {"name": "status", "in": "query", "schema": {"type": "string", "default": "watching"}},
        {"name": "window", "in": "query", "schema": {"type": "string", "default": "monthly"}},
        {"name": "limit", "in": "query", "schema": {"type": "integer", "default": 20}},
    ]
    p["/api/v1/leaderboards"] = {
        "get": {
            "tags": ["Leaderboards"],
            "summary": "Get the monthly leaderboard",
            "parameters": lb_params,
            "responses": _ok_response(),
        }
    }
    for seg, title in (
        ("anime", "Get anime leaderboard"),
        ("tvshows", "Get TV shows leaderboard"),
        ("movies", "Get movies leaderboard"),
    ):
        p[f"/api/v1/leaderboards/{seg}"] = {
            "get": {
                "tags": ["Leaderboards"],
                "summary": title,
                "parameters": [
                    {"name": "status", "in": "query", "schema": {"type": "string"}},
                    {"name": "window", "in": "query", "schema": {"type": "string"}},
                    {"name": "limit", "in": "query", "schema": {"type": "integer", "default": 20}},
                ],
                "responses": _ok_response(),
            }
        }

    p["/api/v1/search"] = {
        "get": {
            "tags": ["Search"],
            "summary": "Search across media",
            "parameters": [
                {"name": "q", "in": "query", "required": True, "schema": {"type": "string"}},
                {
                    "name": "type",
                    "in": "query",
                    "schema": {"type": "string", "enum": ["anime", "movie", "tvshow"]},
                },
                {"name": "limit", "in": "query", "schema": {"type": "integer", "default": 12}},
                {"name": "offset", "in": "query", "schema": {"type": "integer", "default": 0}},
            ],
            "responses": _ok_response(),
        }
    }

    p["/api/v1/landing/posters"] = {
        "get": {
            "tags": ["Landing"],
            "summary": "Random poster payloads for the Three.js landing page",
            "responses": _ok_response(),
        }
    }

    p["/api/v1/items/{imdb_id}"] = {
        "get": {
            "tags": ["Items"],
            "summary": "Unified media detail by IMDb id (detail + watchlist counts)",
            "parameters": [
                {
                    "name": "imdb_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string", "example": "tt0111161"},
                }
            ],
            "responses": _ok_response(),
        }
    }

    fid = {
        "name": "friendship_id",
        "in": "path",
        "required": True,
        "schema": {"type": "integer"},
    }
    p["/api/v1/friends"] = {
        "get": {
            "tags": ["Friends"],
            "summary": "List accepted friends (session)",
            "responses": _ok_response(),
        }
    }
    p["/api/v1/friends/requests"] = {
        "get": {
            "tags": ["Friends"],
            "summary": "List pending friend requests (received + sent)",
            "responses": _ok_response(),
        },
        "post": {
            "tags": ["Friends"],
            "summary": "Send a friend request",
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "required": ["targetUserId"],
                            "properties": {"targetUserId": {"type": "integer"}},
                        }
                    }
                },
            },
            "responses": _created_response(),
        },
    }
    p["/api/v1/friends/requests/{friendship_id}"] = {
        "patch": {
            "tags": ["Friends"],
            "summary": "Accept or reject an incoming friend request",
            "parameters": [fid],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "required": ["action"],
                            "properties": {
                                "action": {"type": "string", "enum": ["accept", "reject"]}
                            },
                        }
                    }
                },
            },
            "responses": _ok_response(),
        }
    }
    p["/api/v1/friends/{friendship_id}"] = {
        "delete": {
            "tags": ["Friends"],
            "summary": "Remove an accepted friendship",
            "parameters": [fid],
            "responses": _ok_response(),
        }
    }
    p["/api/v1/friends/status/{user_id}"] = {
        "get": {
            "tags": ["Friends"],
            "summary": "Friendship status with another user",
            "parameters": [
                {
                    "name": "user_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "integer"},
                }
            ],
            "responses": _ok_response(),
        }
    }

    msg_peer = {
        "name": "user_id",
        "in": "path",
        "required": True,
        "schema": {"type": "integer", "title": "Peer user id"},
    }
    p["/api/v1/messages/{user_id}"] = {
        "get": {
            "tags": ["Messages"],
            "summary": "Paginated conversation with another user",
            "parameters": [
                msg_peer,
                {"name": "limit", "in": "query", "schema": {"type": "integer", "default": 50}},
                {"name": "offset", "in": "query", "schema": {"type": "integer", "default": 0}},
            ],
            "responses": _ok_response(),
        }
    }
    p["/api/v1/messages/{user_id}/read"] = {
        "patch": {
            "tags": ["Messages"],
            "summary": "Mark messages from this user as read",
            "parameters": [msg_peer],
            "responses": _ok_response(),
        }
    }
    p["/api/v1/messages/unread"] = {
        "get": {
            "tags": ["Messages"],
            "summary": "Unread DM count",
            "responses": _ok_response(),
        }
    }

    # Admin
    p["/api/v1/management/users"] = {
        "get": {
            "tags": ["Admin"],
            "summary": "List all users (admin)",
            "responses": _only_200(),
        }
    }
    p["/api/v1/management/users/{user_id}"] = {
        "patch": {
            "tags": ["Admin"],
            "summary": "Update user admin/deactivation flags",
            "parameters": [uid],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"type": "object", "additionalProperties": True}
                    }
                },
            },
            "responses": _ok_response(),
        },
        "delete": {
            "tags": ["Admin"],
            "summary": "Deactivate a user without deleting stored data (admin)",
            "parameters": [uid],
            "responses": _ok_response(),
        },
    }

    media_admin_id = {
        "name": "media_id",
        "in": "path",
        "required": True,
        "schema": {"type": "string", "title": "Internal media id"},
    }
    p["/api/v1/management/media"] = {
        "post": {
            "tags": ["Admin"],
            "summary": "Create media row (admin)",
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"type": "object", "additionalProperties": True}
                    }
                },
            },
            "responses": _created_response(),
        }
    }
    p["/api/v1/management/media/{media_id}"] = {
        "patch": {
            "tags": ["Admin"],
            "summary": "Update media (admin)",
            "parameters": [media_admin_id],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {"type": "object", "additionalProperties": True}
                    }
                },
            },
            "responses": _ok_response(),
        },
        "delete": {
            "tags": ["Admin"],
            "summary": "Delete media (admin)",
            "parameters": [media_admin_id],
            "responses": _ok_response(),
        },
    }

    return p


def _schemas():
    return {
        "APIResponse": {
            "type": "object",
            "title": "APIResponse",
            "properties": {
                "success": {"type": "boolean", "default": True},
                "message": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                "data": {
                    "anyOf": [
                        {"type": "object", "additionalProperties": True},
                        {"type": "array", "items": {}},
                        {"type": "null"},
                    ]
                },
                "meta": {"anyOf": [{"$ref": "#/components/schemas/Meta"}, {"type": "null"}]},
                "links": {
                    "anyOf": [{"type": "object", "additionalProperties": True}, {"type": "null"}]
                },
            },
        },
        "Meta": {
            "type": "object",
            "title": "Meta",
            "properties": {
                "limit": {"anyOf": [{"type": "integer"}, {"type": "null"}]},
                "offset": {"anyOf": [{"type": "integer"}, {"type": "null"}]},
                "total": {"anyOf": [{"type": "integer"}, {"type": "null"}]},
            },
        },
        "HTTPValidationError": {
            "type": "object",
            "title": "HTTPValidationError",
            "properties": {
                "detail": {
                    "type": "array",
                    "items": {"$ref": "#/components/schemas/ValidationError"},
                }
            },
        },
        "ValidationError": {
            "type": "object",
            "required": ["loc", "msg", "type"],
            "properties": {
                "loc": {
                    "type": "array",
                    "items": {"anyOf": [{"type": "string"}, {"type": "integer"}]},
                },
                "msg": {"type": "string"},
                "type": {"type": "string"},
            },
        },
        "RegisterRequest": {
            "type": "object",
            "required": ["username", "displayName", "email", "password"],
            "properties": {
                "username": {"type": "string", "minLength": 3, "maxLength": 24},
                "displayName": {"type": "string", "minLength": 2, "maxLength": 50},
                "email": {"type": "string"},
                "password": {"type": "string", "minLength": 8},
            },
        },
        "LoginRequest": {
            "type": "object",
            "required": ["login", "password"],
            "properties": {
                "login": {"type": "string"},
                "password": {"type": "string", "minLength": 8},
            },
        },
        "UserUpdateRequest": {
            "type": "object",
            "properties": {
                "displayName": {"type": "string"},
                "bio": {"type": "string"},
                "favoriteGenres": {"type": "array", "items": {"type": "string"}},
                "visibility": {"$ref": "#/components/schemas/VisibilitySettings"},
            },
        },
        "VisibilitySettings": {
            "type": "object",
            "properties": {
                "watchlist": {
                    "type": "string",
                    "enum": ["public", "followers", "private"],
                    "default": "public",
                }
            },
        },
        "WatchlistCreateRequest": {
            "type": "object",
            "required": ["mediaType", "mediaId", "status", "progress"],
            "properties": {
                "mediaType": {"type": "string", "enum": ["anime", "movie", "tvshow"]},
                "mediaId": {"type": "string"},
                "status": {"type": "string"},
                "progress": {"$ref": "#/components/schemas/Progress"},
                "isFavorite": {"type": "boolean", "default": False},
            },
        },
        "Progress": {
            "type": "object",
            "required": ["unit", "value"],
            "properties": {
                "unit": {"type": "string"},
                "value": {"type": "integer", "minimum": 0},
            },
        },
        "WatchlistUpdateRequest": {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "progress": {"$ref": "#/components/schemas/Progress"},
                "isFavorite": {"type": "boolean"},
            },
        },
        "ReviewRequest": {
            "type": "object",
            "required": ["mediaType", "mediaId", "rating", "title", "body"],
            "properties": {
                "mediaType": {"type": "string", "enum": ["anime", "movie", "tvshow"]},
                "mediaId": {"type": "string"},
                "rating": {"type": "integer", "minimum": 1, "maximum": 10},
                "title": {"type": "string"},
                "body": {"type": "string"},
                "spoiler": {"type": "boolean", "default": False},
            },
        },
        "ReviewUpdateRequest": {
            "type": "object",
            "properties": {
                "rating": {"type": "integer"},
                "title": {"type": "string"},
                "body": {"type": "string"},
                "spoiler": {"type": "boolean"},
            },
        },
        "FollowRequest": {
            "type": "object",
            "required": ["targetUserId"],
            "properties": {"targetUserId": {"type": "string"}},
        },
        "NotificationUpdateRequest": {
            "type": "object",
            "properties": {"isRead": {"type": "boolean", "default": True}},
        },
    }


def build_openapi_spec():
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "WatchList Hub API",
            "version": "1.0.0",
            "summary": "CITS5505 — REST surface under /api/v1",
            "description": (
                "**WatchList Hub** — session-based JSON API backing the Flask app. "
                "**Implemented in this repo:** auth, users & profiles, watchlists, catalog "
                "(anime / TV / movies by internal id), **unified item detail** by IMDb id, "
                "search, trending & leaderboards, landing posters, **friends** (requests, "
                "accept/reject, unfriend, status), **direct messages**, and **admin** user list "
                "plus generic **media** create/update/delete. "
                "Most routes return the shared `{ success, message, data, meta }` envelope."
            ),
            "contact": {"name": "WatchList Hub Team", "email": "team@example.com"},
            "license": {"name": "MIT"},
        },
        "servers": [{"url": "/", "description": "Current server (e.g. http://127.0.0.1:5002)"}],
        "tags": [
            {"name": "System", "description": "Health / API root."},
            {"name": "Auth", "description": "Register, login, logout, session."},
            {"name": "Users", "description": "Profiles, current user, public watchlists."},
            {"name": "Anime", "description": "List and get anime (internal numeric id)."},
            {"name": "TV Shows", "description": "List and get TV shows (internal numeric id)."},
            {"name": "Movies", "description": "List and get movies (internal numeric id)."},
            {"name": "Items", "description": "Single title by IMDb id (detail page + counts)."},
            {"name": "Watchlist", "description": "Signed-in user's watchlist CRUD."},
            {"name": "Friends", "description": "Friends list, requests, accept/reject, remove, status."},
            {"name": "Messages", "description": "Direct messages between users."},
            {"name": "Leaderboards", "description": "Trending and leaderboard slices."},
            {"name": "Landing", "description": "Public assets for the marketing landing page."},
            {"name": "Search", "description": "Search media catalogue."},
            {"name": "Admin", "description": "Admin-only users and media catalogue edits."},
        ],
        "paths": _paths(),
        "components": {"schemas": _schemas()},
    }
