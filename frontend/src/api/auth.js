/**
 * Auth API client — /api/v1/auth (JSON envelope: { success, data, message, meta }).
 */

import { request } from './watchlist.js';

const AUTH_ENDPOINTS = {
  login: '/auth/login',
  register: '/auth/register',
  logout: '/auth/logout',
  refresh: '/auth/refresh',
  forgotPassword: '/auth/forgot-password',
  resetPassword: '/auth/reset-password',
};

/**
 * Authenticate user with credentials
 * @param {string} username - Username or email
 * @param {string} password - User password
 * @param {boolean} remember - Whether to extend session
 * @returns {Promise<Object>} User data and tokens
 */
export async function login(username, password, remember = false) {
  const response = await request(AUTH_ENDPOINTS.login, {
    method: 'POST',
    body: JSON.stringify({ username, password, remember }),
  });

  // Store tokens in localStorage
  if (response.token) {
    localStorage.setItem('authToken', response.token);
    localStorage.setItem('refreshToken', response.refreshToken);
    localStorage.setItem('user', JSON.stringify(response.user));
  }

  return response;
}

/**
 * Register new user
 * @param {Object} userData - User registration data
 * @returns {Promise<Object>} User data
 */
export async function register(userData) {
  return await request(AUTH_ENDPOINTS.register, {
    method: 'POST',
    body: JSON.stringify(userData),
  });
}

/**
 * Logout user
 * @returns {Promise<void>}
 */
export async function logout() {
  try {
    await request(AUTH_ENDPOINTS.logout, {
      method: 'POST',
    });
  } finally {
    // Clear local storage regardless of API response
    localStorage.removeItem('authToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
  }
}

/**
 * Check if user is authenticated
 * @returns {boolean}
 */
export function isAuthenticated() {
  const token = localStorage.getItem('authToken');
  const user = localStorage.getItem('user');
  return !!(token && user);
}

/**
 * Get current user data
 * @returns {Object|null}
 */
export function getCurrentUser() {
  const userStr = localStorage.getItem('user');
  try {
    return userStr ? JSON.parse(userStr) : null;
  } catch {
    return null;
  }
}

/**
 * Request password reset
 * @param {string} email - User email
 * @returns {Promise<Object>}
 */
export async function forgotPassword(email) {
  return await request(AUTH_ENDPOINTS.forgotPassword, {
    method: 'POST',
    body: JSON.stringify({ email }),
  });
}

/**
 * Reset password with token
 * @param {string} token - Reset token
 * @param {string} newPassword - New password
 * @returns {Promise<Object>}
 */
export async function resetPassword(token, newPassword) {
  return await request(AUTH_ENDPOINTS.resetPassword, {
    method: 'POST',
    body: JSON.stringify({ token, password: newPassword }),
  });
}