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

    p["/api/v1"] = op("Search", "API root / health check", "get")

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

    for sub, summ in (
        ("reviews", "Get reviews written by a user"),
        ("followers", "Get followers of a user"),
        ("following", "Get who a user is following"),
    ):
        p[f"/api/v1/users/{{user_id}}/{sub}"] = {
            "get": {
                "tags": ["Users"],
                "summary": summ,
                "parameters": [uid],
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
    p["/api/v1/users/me/reviews"] = {
        "get": {
            "tags": ["Users"],
            "summary": "Get the current user's reviews",
            "responses": _only_200(),
        }
    }
    p["/api/v1/users/me/notifications"] = {
        "get": {
            "tags": ["Users"],
            "summary": "Get the current user's notifications",
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
    game_q = [
        {"name": "q", "in": "query", "schema": {"type": "string"}},
        {"name": "platform", "in": "query", "schema": {"type": "string"}},
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
    p["/api/v1/anime/{anime_id}/reviews"] = {
        "get": {
            "tags": ["Anime"],
            "summary": "Get reviews for an anime",
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

    p["/api/v1/games"] = {
        "get": {
            "tags": ["Games"],
            "summary": "List games",
            "parameters": game_q,
            "responses": _ok_response(),
        }
    }
    p["/api/v1/games/{game_id}"] = {
        "get": {
            "tags": ["Games"],
            "summary": "Get game details",
            "parameters": [
                {
                    "name": "game_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                }
            ],
            "responses": _ok_response(),
        }
    }
    p["/api/v1/games/{game_id}/reviews"] = {
        "get": {
            "tags": ["Games"],
            "summary": "Get reviews for a game",
            "parameters": [
                {
                    "name": "game_id",
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
    p["/api/v1/movies/{movie_id}/reviews"] = {
        "get": {
            "tags": ["Movies"],
            "summary": "Get reviews for a movie",
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

    p["/api/v1/reviews"] = {
        "post": {
            "tags": ["Reviews"],
            "summary": "Create a review",
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": _ref("ReviewRequest")}},
            },
            "responses": _created_response(),
        }
    }
    p["/api/v1/reviews/{review_id}"] = {
        "patch": {
            "tags": ["Reviews"],
            "summary": "Update a review",
            "parameters": [
                {
                    "name": "review_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                }
            ],
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": _ref("ReviewUpdateRequest")}},
            },
            "responses": _ok_response(),
        },
        "delete": {
            "tags": ["Reviews"],
            "summary": "Delete a review",
            "parameters": [
                {
                    "name": "review_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                }
            ],
            "responses": _ok_response(),
        },
    }

    p["/api/v1/follows"] = {
        "post": {
            "tags": ["Follows"],
            "summary": "Follow a user",
            "requestBody": {
                "required": True,
                "content": {"application/json": {"schema": _ref("FollowRequest")}},
            },
            "responses": _created_response(),
        }
    }
    p["/api/v1/follows/{follow_id}"] = {
        "delete": {
            "tags": ["Follows"],
            "summary": "Unfollow a user",
            "parameters": [
                {
                    "name": "follow_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                }
            ],
            "responses": _ok_response(),
        }
    }

    p["/api/v1/notifications"] = {
        "get": {
            "tags": ["Notifications"],
            "summary": "Get notifications",
            "parameters": [
                {"name": "limit", "in": "query", "schema": {"type": "integer", "default": 20}},
                {"name": "offset", "in": "query", "schema": {"type": "integer", "default": 0}},
            ],
            "responses": _ok_response(),
        }
    }
    p["/api/v1/notifications/{notification_id}"] = {
        "patch": {
            "tags": ["Notifications"],
            "summary": "Update a notification",
            "parameters": [
                {
                    "name": "notification_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                }
            ],
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {"schema": _ref("NotificationUpdateRequest")}
                },
            },
            "responses": _ok_response(),
        }
    }
    p["/api/v1/notifications/read-all"] = {
        "patch": {
            "tags": ["Notifications"],
            "summary": "Mark all notifications as read",
            "responses": _only_200(),
        }
    }

    p["/api/v1/trending"] = {
        "get": {
            "tags": ["Leaderboards"],
            "summary": "Trending media (optional type filter)",
            "parameters": [
                {
                    "name": "type",
                    "in": "query",
                    "schema": {"type": "string", "enum": ["anime", "game", "movie"]},
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
            "schema": {"type": "string", "enum": ["anime", "game", "movie"], "default": "anime"},
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
        ("games", "Get games leaderboard"),
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
                    "schema": {"type": "string", "enum": ["anime", "game", "movie"]},
                },
                {"name": "limit", "in": "query", "schema": {"type": "integer", "default": 12}},
                {"name": "offset", "in": "query", "schema": {"type": "integer", "default": 0}},
            ],
            "responses": _ok_response(),
        }
    }

    # Admin
    p["/api/v1/admin/users"] = {
        "get": {
            "tags": ["Admin"],
            "summary": "List all users (admin)",
            "responses": _only_200(),
        }
    }
    p["/api/v1/admin/users/{user_id}"] = {
        "patch": {
            "tags": ["Admin"],
            "summary": "Update a user role or status (admin)",
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
            "summary": "Delete a user (admin)",
            "parameters": [uid],
            "responses": _ok_response(),
        },
    }

    for kind, label in (("anime", "anime"), ("games", "game"), ("movies", "movie")):
        pid = "anime_id" if kind == "anime" else ("game_id" if kind == "games" else "movie_id")
        base = f"/api/v1/admin/{kind}"
        p[base] = {
            "post": {
                "tags": ["Admin"],
                "summary": f"Create {label} (admin)",
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
        p[f"{base}/{{{pid}}}"] = {
            "patch": {
                "tags": ["Admin"],
                "summary": f"Update {label} (admin)",
                "parameters": [
                    {"name": pid, "in": "path", "required": True, "schema": {"type": "string"}}
                ],
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
                "summary": f"Delete {label} (admin)",
                "parameters": [
                    {"name": pid, "in": "path", "required": True, "schema": {"type": "string"}}
                ],
                "responses": _ok_response(),
            },
        }

    p["/api/v1/admin/reviews/pending"] = {
        "get": {
            "tags": ["Admin"],
            "summary": "List pending reviews (admin)",
            "responses": _only_200(),
        }
    }
    p["/api/v1/admin/reviews/{review_id}/approve"] = {
        "patch": {
            "tags": ["Admin"],
            "summary": "Approve a review (admin)",
            "parameters": [
                {
                    "name": "review_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                }
            ],
            "responses": _ok_response(),
        }
    }
    p["/api/v1/admin/reviews/{review_id}"] = {
        "delete": {
            "tags": ["Admin"],
            "summary": "Delete a review (admin)",
            "parameters": [
                {
                    "name": "review_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                }
            ],
            "responses": _ok_response(),
        }
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
                "mediaType": {"type": "string", "enum": ["anime", "game", "movie"]},
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
                "mediaType": {"type": "string", "enum": ["anime", "game", "movie"]},
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
            "title": "Watchlist Hub API",
            "version": "1.0.0",
            "summary": "OpenAPI for the Watchlist Hub Flask backend",
            "description": (
                "Session-based auth, media discovery, watchlists, and admin endpoints. "
                "Some features return placeholder data until models are implemented."
            ),
            "contact": {"name": "Watchlist Hub Team", "email": "team@example.com"},
            "license": {"name": "MIT"},
        },
        "servers": [{"url": "/", "description": "Current server"}],
        "tags": [
            {"name": "Auth", "description": "Authentication and session endpoints."},
            {"name": "Users", "description": "Public profiles and current-user endpoints."},
            {"name": "Anime", "description": "Anime discovery and detail endpoints."},
            {"name": "Games", "description": "Game discovery and detail endpoints."},
            {"name": "Movies", "description": "Movie discovery and detail endpoints."},
            {"name": "Watchlist", "description": "Private watchlist management endpoints."},
            {"name": "Reviews", "description": "Create, update, and delete reviews."},
            {"name": "Follows", "description": "Follow relationships between users."},
            {"name": "Notifications", "description": "User notifications."},
            {"name": "Leaderboards", "description": "Trending leaderboard endpoints."},
            {"name": "Search", "description": "Mixed search endpoint."},
            {"name": "Admin", "description": "Admin-only moderation and catalog endpoints."},
        ],
        "paths": _paths(),
        "components": {"schemas": _schemas()},
    }
