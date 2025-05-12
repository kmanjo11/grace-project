/**
 * Authentication Utilities for Grace App
 * 
 * Provides standardized token management compatible with the existing auth-utils.js system.
 */

// Token storage constants - exported for consistency across the codebase
export const TOKEN_KEY = 'grace_token';
export const TOKEN_EXPIRY_KEY = 'grace_token_expiry';

/**
 * Store authentication token with remember-me preference
 */
export function storeAuthToken(token: string, rememberMe: boolean = false): void {
  const storage = rememberMe ? localStorage : sessionStorage;
  storage.setItem(TOKEN_KEY, token);
  
  // Set expiry date (24 hours from now)
  const expiry = new Date();
  expiry.setHours(expiry.getHours() + 24);
  storage.setItem(TOKEN_EXPIRY_KEY, expiry.toISOString());
}

/**
 * Get the current authentication token from storage
 */
export function getAuthToken(): string | null {
  // Check both storage locations for compatibility
  return localStorage.getItem(TOKEN_KEY) || sessionStorage.getItem(TOKEN_KEY) || null;
}

/**
 * Get token expiration date
 */
export function getTokenExpiry(): Date | null {
  const expiryStr = localStorage.getItem(TOKEN_EXPIRY_KEY) || sessionStorage.getItem(TOKEN_EXPIRY_KEY);
  return expiryStr ? new Date(expiryStr) : null;
}

/**
 * Check if token is expired
 */
export function isTokenExpired(): boolean {
  const expiry = getTokenExpiry();
  return !expiry || expiry < new Date();
}

/**
 * Clear all authentication tokens
 */
export function clearAuthTokens(): void {
  // Clear from both storage locations to be safe
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(TOKEN_EXPIRY_KEY);
  sessionStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(TOKEN_EXPIRY_KEY);
}

/**
 * Add authorization headers to fetch options
 */
export function addAuthHeaders(options: RequestInit = {}): RequestInit {
  const token = getAuthToken();
  const headers = { 
    ...options.headers,
    'Content-Type': 'application/json',
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  return {
    ...options,
    headers,
  };
}

/**
 * Wrapper for fetch with authentication headers
 */
export async function authFetch(url: string, options: RequestInit = {}): Promise<Response> {
  return fetch(url, addAuthHeaders(options));
}
