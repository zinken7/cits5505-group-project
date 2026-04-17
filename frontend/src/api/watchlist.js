/**
 * Watchlist API client — /api/v1 (JSON envelope: { success, data, message, meta }).
 */

const BASE_URL = "/api/v1";

function errorMessage(body, status) {
  if (!body || typeof body !== "object") {
    return `Request failed (${status})`;
  }
  if (body.message) return body.message;
  const d = body.detail;
  if (Array.isArray(d) && d[0]?.msg) return d[0].msg;
  if (body.error) return body.error;
  return `Request failed (${status})`;
}

/**
 * @param {string} url
 * @param {Object} [options]
 * @returns {Promise<*>} Unwrapped `data` from APIResponse
 */
async function request(url, options = {}) {
  const defaults = {
    headers: {
      "Content-Type": "application/json",
    },
  };

  const response = await fetch(`${BASE_URL}${url}`, {
    ...defaults,
    ...options,
    headers: { ...defaults.headers, ...options.headers },
  });

  const contentType = response.headers.get("content-type") || "";
  const isJson = contentType.includes("application/json");
  const body = isJson ? await response.json() : null;

  if (!response.ok) {
    throw new Error(errorMessage(body, response.status));
  }

  if (body && typeof body === "object" && "success" in body) {
    if (!body.success) {
      throw new Error(body.message || "Request failed");
    }
    return body.data;
  }

  return body;
}

/**
 * @param {string} [status] - watching | planned | completed | …
 * @returns {Promise<Array>} Watchlist entries
 */
export function getWatchlist(status) {
  const params = status ? `?status=${encodeURIComponent(status)}` : "";
  return request(`/watchlist${params}`);
}

/**
 * @param {"anime"|"game"|"movie"} mediaType
 * @param {number} mediaId
 * @param {string} [status='planned']
 */
export function addToWatchlist(mediaType, mediaId, status = "planned") {
  return request("/watchlist", {
    method: "POST",
    body: JSON.stringify({
      mediaType,
      mediaId,
      status,
    }),
  });
}

/**
 * @param {number} itemId
 * @param {string} newStatus
 */
export function updateWatchlistItem(itemId, newStatus) {
  return request(`/watchlist/${itemId}`, {
    method: "PATCH",
    body: JSON.stringify({ status: newStatus }),
  });
}

/**
 * @param {number} itemId
 */
export function removeFromWatchlist(itemId) {
  return request(`/watchlist/${itemId}`, {
    method: "DELETE",
  });
}

/**
 * Trending / popular media (same data as legacy GET /api/trending).
 * @param {string} [mediaType] - anime | game | movie (omit for all types)
 * @param {number} [limit=10]
 */
export function getTrending(mediaType, limit = 10) {
  const params = new URLSearchParams({ limit: String(limit) });
  if (mediaType) params.set("type", mediaType);
  return request(`/trending?${params}`);
}
