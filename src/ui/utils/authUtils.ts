/**
 * Authentication Utilities for Grace App
 * 
 * Provides standardized token management compatible with the existing auth-utils.js system.
 */

// Token storage constants - exported for consistency across the codebase
export const TOKEN_KEY = 'grace_token';
export const TOKEN_EXPIRY_KEY = 'grace_token_expiry';

// Simple mutex to prevent race conditions
let tokenMutex = Promise.resolve();

/**
 * Store authentication token with remember-me preference
 * Uses a mutex to prevent race conditions
 */
export async function storeAuthToken(token: string, rememberMe: boolean = false): Promise<void> {
  // Wait for any existing operation to complete
  await tokenMutex;
  
  // Create a new lock that others will wait for
  let releaseLock: () => void;
  tokenMutex = new Promise(resolve => {
    releaseLock = resolve;
  });
  
  try {
    // Clear both to prevent any token conflicts
    clearAuthTokens();
    
    // Store in the appropriate location
    const storage = rememberMe ? localStorage : sessionStorage;
    storage.setItem(TOKEN_KEY, token);
    
    // Set expiry date (24 hours from now)
    const expiry = new Date();
    expiry.setHours(expiry.getHours() + 24);
    storage.setItem(TOKEN_EXPIRY_KEY, expiry.toISOString());
  } finally {
    releaseLock!();
  }
}

/**
 * Get the current authentication token from storage
 * Checks sessionStorage first, then falls back to localStorage
 */
export function getAuthToken(): string | null {
  return sessionStorage.getItem(TOKEN_KEY) || localStorage.getItem(TOKEN_KEY);
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
