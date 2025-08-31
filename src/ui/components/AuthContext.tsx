// src/ui/components/AuthContext.tsx

import React, { createContext, useContext, useEffect, useState, useRef } from 'react';
import { API_ENDPOINTS } from '../api/apiClient';
import api from '../api/apiClient';
// Import admin backdoor utilities
import { hasAdminBypass, bypassLogin } from '../utils/devAuth';
// Import standardized auth utils
import {
  getAuthToken,
  getTokenExpiry,
  storeAuthToken,
  clearAuthTokens,
  isTokenExpired,
  addAuthHeaders,
  TOKEN_KEY
} from '../utils/authUtils';

const TOKEN_EXPIRY_KEY = 'grace_token_expiry';
const REFRESH_TOKEN_KEY = 'grace_refresh_token';
const TOKEN_VERIFY_INTERVAL = 60000; // Check token validity every 60 seconds

// Improved session persistence utility to avoid conflicts with form state
const PERSIST_DISABLED = (process.env.NEXT_PUBLIC_DISABLE_STATE_PERSIST || '').toString() === '1' || (process.env.NEXT_PUBLIC_DISABLE_STATE_PERSIST || '').toString().toLowerCase() === 'true';

const SessionPersistence = {
  STORAGE_KEY: 'GRACE_SESSION_SNAPSHOT',
  
  // Safely capture session snapshot with minimal data to avoid interference
  captureSnapshot(user: User | null, token: string | null) {
    try {
      if (PERSIST_DISABLED) return;
      if (!user || !token) {
        this.clearSnapshot();
        return;
      }

      // Store only essential user identification data
      // Avoid storing complete state that might conflict with forms
      const snapshot = {
        timestamp: Date.now(),
        user: {
          id: user.id,
          username: user.username,
          email: user.email
        },
        // Don't store the actual token, just indicate authentication
        authenticated: true
      };

      // Use sessionStorage instead of localStorage to avoid persisting between browser sessions
      // This helps prevent stale data from affecting forms on future visits
      if (typeof window !== 'undefined') {
        sessionStorage.setItem(this.STORAGE_KEY, JSON.stringify(snapshot));
      }
    } catch (error) {
      console.warn('Failed to capture session snapshot', error);
      // Silently fail - don't let snapshot errors affect the application
    }
  },

  // Retrieve session snapshot with validation
  retrieveSnapshot(): { user: User | null, token: string | null } {
    try {
      if (PERSIST_DISABLED) return { user: null, token: null };
      const snapshotStr = typeof window !== 'undefined' ? sessionStorage.getItem(this.STORAGE_KEY) : null;
      if (!snapshotStr) return { user: null, token: null };

      const snapshot = JSON.parse(snapshotStr);
      
      // Validate snapshot with expiration check (30 minutes)
      const MAX_AGE = 30 * 60 * 1000; // 30 minutes in milliseconds
      const isExpired = (Date.now() - (snapshot.timestamp || 0)) > MAX_AGE;
      
      if (snapshot && snapshot.user && !isExpired) {
        return {
          user: snapshot.user,
          // Get actual token from authUtils to ensure consistency
          token: getAuthToken()
        };
      }

      // Clear expired snapshot
      if (isExpired) this.clearSnapshot();
      return { user: null, token: null };
    } catch (error) {
      console.warn('Failed to retrieve session snapshot', error);
      this.clearSnapshot(); // Clear invalid snapshot
      return { user: null, token: null };
    }
  },

  // Clear session snapshot
  clearSnapshot() {
    try {
      if (PERSIST_DISABLED) return;
      if (typeof window !== 'undefined') {
        sessionStorage.removeItem(this.STORAGE_KEY);
      }
    } catch (error) {
      console.warn('Failed to clear session snapshot', error);
    }
  }
};

interface User {
  id?: string;
  username?: string;
  email?: string;
  displayName?: string;
  [key: string]: any;
}

interface AuthContextType {
  user: User | null;
  login: (data: any) => Promise<boolean>;
  logout: () => void;
  loading: boolean;
  refreshToken: () => Promise<boolean>;
  isAuthenticated: boolean;
  updateUser: (partial: Partial<User>) => void;
}

const AuthContext = createContext<AuthContextType | null>(null);


export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  // Use state for token to ensure it's updated when changed
  const [token, setToken] = useState<string | null>(getAuthToken());
  // Add flag to prevent verification immediately after login
  const [skipNextVerification, setSkipNextVerification] = useState<boolean>(false);
  // Grace window to avoid immediate unauth flips when token is briefly missing
  const noTokenGraceUntil = useRef<number>(0);
  
  // Update token state whenever auth state changes
  useEffect(() => {
    setToken(getAuthToken());
  }, [isAuthenticated]);
  
  // Admin backdoor for quick access
  useEffect(() => {
    // Check if we should use the admin backdoor
    if (hasAdminBypass() && !isAuthenticated && !token) {
      bypassLogin(login);
    }
  }, []);

  // FIXED: Stabilized verification on mount and periodic checks
  useEffect(() => {
    let isMounted = true;
    
    const verifyOnMount = async () => {
      // Start short grace on mount to tolerate brief token propagation
      noTokenGraceUntil.current = Date.now() + 1500;
      // Skip initial verification if there's no token
      if (typeof window !== 'undefined' && !getAuthToken()) {
        console.log('AuthContext: No token found on mount, skipping verification');
        if (isMounted) setLoading(false);
        return;
      }
      
      console.log('AuthContext: Verifying token on mount');
      // Verify token on component mount (force = true to bypass debouncing)
      await verifyToken(true);
      
      // Handle case where verification completed but component was unmounted
      if (isMounted) setLoading(false);
    };
    
    verifyOnMount();
    
    // FIXED: Increased interval to reduce verification frequency
    const interval = setInterval(() => {
      if (!skipNextVerification) {
        verifyToken(); // Use debounced version for periodic checks
      } else {
        // Reset skip flag after using it once
        setSkipNextVerification(false);
      }
    }, 120000); // FIXED: Increased to 2 minutes to reduce server load
    
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);     

  // FIXED: Add debouncing to prevent rapid verification calls
  const verifyTokenDebounced = useRef<NodeJS.Timeout | null>(null);
  const lastVerifyAttempt = useRef<number>(0);
  
  // Verify user token with backend (FIXED: Added debouncing and better error handling)
  const verifyToken = async (force: boolean = false) => {
    // If no token exists, there's nothing to verify
    const token = getAuthToken();
    if (!token) {
      const withinGrace = Date.now() < noTokenGraceUntil.current;
      console.log('AuthContext: No token to verify', { withinGrace });
      if (withinGrace) {
        // Do not flip auth state during grace; just stop loading
        setLoading(false);
        return false;
      }
      // Outside grace: clear auth state
      setIsAuthenticated(false);
      setUser(null);
      setLoading(false);
      return false;
    }

    // FIXED: Debounce verification calls to prevent rapid requests
    const now = Date.now();
    if (!force && now - lastVerifyAttempt.current < 5000) {
      console.log('AuthContext: Skipping verification (debounced)');
      return false;
    }
    lastVerifyAttempt.current = now;

    try {
      console.log('AuthContext: Verifying token with backend');
      setLoading(true);
      const response = await api.get(API_ENDPOINTS.AUTH.VERIFY_TOKEN);

      if (response.success && response.data) {
        // Token is valid, update user data
        console.log('AuthContext: Token verified successfully');
        setIsAuthenticated(true);
        // Merge cached displayName if backend user payload lacks it to avoid UI fallback to username
        const initialUser = { ...(response.data.user || {}) } as any;
        try {
          if (typeof window !== 'undefined' && !initialUser.displayName) {
            const cachedDN = localStorage.getItem('displayName');
            if (cachedDN) initialUser.displayName = cachedDN;
          }
        } catch {}
        setUser(initialUser);
        setToken(token); // Ensure token state matches storage
        // Fetch user settings ONLY if displayName is missing; avoids duplicate GETs with Settings page
        try {
          const hasDisplayName = !!(response.data.user && response.data.user.displayName);
          if (!hasDisplayName) {
            const settingsResp = await api.get(API_ENDPOINTS.SETTINGS.PROFILE);
            const payload: any = settingsResp.data as any;
            // Sanitize nested { success, settings } wrappers
            const sanitize = (input: any): any => {
              let current = input;
              const seen = new Set<any>();
              while (current && typeof current === 'object' && !Array.isArray(current) && !seen.has(current)) {
                seen.add(current);
                if ('success' in current && Object.keys(current).length >= 1) {
                  const { success: _s, ...rest } = current as any;
                  current = rest;
                }
                if (current && typeof current === 'object' && 'settings' in current && Object.keys(current).length <= 2) {
                  current = (current as any).settings;
                  continue;
                }
                break;
              }
              return current;
            };
            const flat = sanitize(payload?.settings ?? payload);
            if (flat && flat.displayName) {
              setUser(prev => ({ ...(prev || {}), displayName: flat.displayName }));
              try { if (typeof window !== 'undefined') localStorage.setItem('displayName', flat.displayName); } catch {}
            }
          }
        } catch (e) {
          console.warn('AuthContext: Failed to load user settings for displayName merge');
        }
        return true;
      }

      // Non-success HTTP response
      const status = response.statusCode ?? 0;
      if (status === 401 || status === 403) {
        console.log('AuthContext: Token verification failed with unauthorized status:', status);
        clearAuthState();
        return false;
      }

      // FIXED: For other errors (5xx, 0, etc.), keep current auth state to avoid flicker
      console.warn('AuthContext: Verification non-success but not unauthorized. Preserving auth state.', {
        status,
        error: response.error
      });
      return false;
    } catch (error) {
      // FIXED: Network or unexpected error: preserve current auth state to prevent bouncing
      const msg = error instanceof Error ? error.message : 'Unknown error';
      console.error('Token verification error, preserving auth state:', msg);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Enhanced logging utility for authentication events
  const logAuthEvent = (eventType: string, details: any = {}) => {
    const timestamp = new Date().toISOString();
    const logEntry = {
      timestamp,
      eventType,
      ...details
    };
    
    // Optional: Send to backend logging service or store locally
    console.log(JSON.stringify(logEntry));
    
    // Store in local storage for potential debugging
    try {
      if (!PERSIST_DISABLED) {
        const authLogs = JSON.parse((typeof window !== 'undefined' ? localStorage.getItem('auth_logs') : '[]') || '[]');
        authLogs.push(logEntry);
        // Keep only last 50 log entries
        if (typeof window !== 'undefined') {
          localStorage.setItem('auth_logs', JSON.stringify(authLogs.slice(-50)));
        }
      }
    } catch (e) {
      console.error('Failed to log authentication event', e);
    }
  };

  // Check if user has a wallet and generate one if not available
  const checkAndGenerateWallet = async () => {
    try {
      // Skip if not authenticated
      if (!isAuthenticated || !token) {
        return;
      }

      // First check if wallet already exists
      const walletResponse = await api.get(API_ENDPOINTS.WALLET.INFO, {});
      
      // If no wallet or wallet address is empty, generate a new one
      if (!walletResponse.success || 
          !walletResponse.data?.wallet?.wallet_address) {
        
        console.log('No wallet found for user, generating a new internal wallet...');
        
        // Generate a new wallet
        const generateResponse = await api.post(API_ENDPOINTS.WALLET.GENERATE, {});
        
        if (generateResponse.success) {
          console.log('Wallet generated successfully:', 
            generateResponse.data?.wallet?.wallet_address);
          
          // You could set wallet info in state here if needed
          return generateResponse.data?.wallet;
        } else {
          console.error('Failed to generate wallet:', generateResponse.error);
        }
      } else {
        console.log('User wallet already exists:', 
          walletResponse.data?.wallet?.wallet_address);
        return walletResponse.data?.wallet;
      }
    } catch (error) {
      console.error('Error checking/generating wallet:', 
        error instanceof Error ? error.message : 'Unknown error');
    }
  };

  // Implement token refresh functionality with exponential backoff
  const refreshToken = async (retryCount = 0): Promise<boolean> => {
    const MAX_RETRIES = 3;
    const BASE_DELAY = 1000; // 1 second initial delay

    try {
      logAuthEvent('TOKEN_REFRESH_ATTEMPT', { retryCount });

      // Exponential backoff with jitter
      if (retryCount > 0) {
        const delay = BASE_DELAY * Math.pow(2, retryCount) * (1 + Math.random());
        await new Promise(resolve => setTimeout(resolve, delay));
      }

      // Use the dedicated refresh token endpoint
      const response = await api.post<{ token?: string; username?: string }>(API_ENDPOINTS.AUTH.REFRESH_TOKEN, {});

      if (!response.success) {
        throw new Error('Token refresh failed: Unsuccessful response');
      }

      // The API client persists token automatically if present in response body.
      // Read the current token from storage as the source of truth.
      const newToken = getAuthToken() || response.data?.token || null;
      if (!newToken) {
        throw new Error('Token refresh failed: No token available after refresh');
      }

      // Determine storage type based on where the current token is stored
      const inLocalStorage = localStorage.getItem(TOKEN_KEY) !== null;
      const rememberMe = inLocalStorage;

      // Ensure storage is consistent with previous preference if we obtained token via response
      if (response.data?.token) {
        await storeAuthToken(newToken, rememberMe);
      }

      // Update local auth state
      setToken(newToken);
      setIsAuthenticated(true);

      // Optional: Update username if provided
      const username = response.data?.username;
      if (username) {
        setUser(prevUser => ({ ...prevUser, username }));
      }
      
      logAuthEvent('TOKEN_REFRESH_SUCCESS', { username });
      return true;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown refresh error';
      
      logAuthEvent('TOKEN_REFRESH_FAILURE', { 
        errorMessage, 
        retryCount,
        errorStack: error instanceof Error ? error.stack : undefined
      });

      // Implement retry mechanism
      if (retryCount < MAX_RETRIES) {
        console.warn(`Token refresh attempt ${retryCount + 1} failed. Retrying...`);
        return refreshToken(retryCount + 1);
      }

      // Final fallback: logout after max retries
      console.error('Token refresh failed after maximum retries');
      logout();
      return false;
    }
  };

  // Login with credentials
  const login = async (data: any): Promise<boolean> => {
    try {
      console.log('AuthContext: login function called with data:', data);
      // Some API clients save the token directly to storage and strip it from payload
      // Fall back to reading from storage if not present on the response object
      if (!data.token) {
        const storedToken = getAuthToken();
        console.log('AuthContext: token missing in payload, using stored token:', !!storedToken);
        if (storedToken) {
          data.token = storedToken;
        } else {
          throw new Error('No token found in login data or storage');
        }
      }
      
      console.log('AuthContext: Processing login with token');
      
      // Store token with remember me preference if provided
      const rememberMe = data.remember_me !== undefined ? data.remember_me : true; // Default to true for persistent login
      
      // Store token and wait for it to complete
      await storeAuthToken(data.token, rememberMe);
      console.log('AuthContext: Token stored successfully');
      
      // Update application state
      setToken(data.token); // Ensure token state is synchronized
      setUser(data.user || {});
      setIsAuthenticated(true);
      setLoading(false); // Ensure loading state is turned off
      console.log('AuthContext: State updated - isAuthenticated: true, user:', data.user);
      
      // Capture minimal session data after successful login
      if (data.user) {
        SessionPersistence.captureSnapshot(data.user, data.token);
      }
      
      // Set flag to skip next verification cycle to avoid race condition
      setSkipNextVerification(true);
      
      // Log successful login state update
      console.log('AuthContext: Login complete, auth state updated');
      
      // Automatically check for wallet and generate if needed
      // This ensures every user has a wallet automatically
      setTimeout(() => {
        checkAndGenerateWallet();
      }, 500); // Small delay to ensure auth is fully established
      
      return true; // Signal successful login
    } catch (error) {
      console.error('Login failed:', error instanceof Error ? error.message : 'Unknown error');
      // Ensure auth state is reset if login fails
      clearAuthTokens();
      SessionPersistence.clearSnapshot();
      
      setToken(null);
      setUser(null);
      setIsAuthenticated(false);
      setLoading(false);
      
      return false; // Signal failed login
    }
  };

  // Clear auth state - reusable function for both logout and failed auth
  const clearAuthState = () => {
    clearAuthTokens();
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
    SessionPersistence.clearSnapshot();
    // Clear cached display name to avoid cross-user leakage
    try { if (typeof window !== 'undefined') localStorage.removeItem('displayName'); } catch {}
  };
  
  // Allow consumers to update parts of the user object (e.g., displayName)
  const updateUser = (partial: Partial<User>) => {
    setUser(prev => ({ ...(prev || {}), ...partial }));
  };
  
  // Clear auth state
  const logout = async () => {
    logAuthEvent('logout_initiated');
    try {
      // Attempt to call logout endpoint if we have a token
      if (getAuthToken()) {
        await api.post(API_ENDPOINTS.AUTH.LOGOUT, {});
      }
    } catch (error) {
      console.error('Error during logout:', error);
      // Continue with logout regardless of API errors
    } finally {
      // Always clear local state and storage
      clearAuthState();
      
      // Log the event
      logAuthEvent('logout_complete');
    }
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      login, 
      logout, 
      loading,
      refreshToken,
      isAuthenticated,
      updateUser
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
