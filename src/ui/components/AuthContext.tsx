// src/ui/components/AuthContext.tsx

import React, { createContext, useContext, useEffect, useState } from 'react';
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

// Lightweight session persistence utility
const SessionPersistence = {
  STORAGE_KEY: 'GRACE_SESSION_SNAPSHOT',
  
  // Safely capture session snapshot
  captureSnapshot(user: User | null, token: string | null) {
    try {
      if (!user || !token) {
        this.clearSnapshot();
        return;
      }

      const snapshot = {
        timestamp: Date.now(),
        user: {
          id: user.id,
          username: user.username,
          email: user.email
        },
        token: token
      };

      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(snapshot));
    } catch (error) {
      console.warn('Failed to capture session snapshot', error);
    }
  },

  // Retrieve session snapshot
  retrieveSnapshot(): { user: User | null, token: string | null } {
    try {
      const snapshotStr = localStorage.getItem(this.STORAGE_KEY);
      if (!snapshotStr) return { user: null, token: null };

      const snapshot = JSON.parse(snapshotStr);
      
      // Validate snapshot (optional: add expiration check)
      if (snapshot && snapshot.user && snapshot.token) {
        return {
          user: snapshot.user,
          token: snapshot.token
        };
      }

      return { user: null, token: null };
    } catch (error) {
      console.warn('Failed to retrieve session snapshot', error);
      return { user: null, token: null };
    }
  },

  // Clear session snapshot
  clearSnapshot() {
    try {
      localStorage.removeItem(this.STORAGE_KEY);
    } catch (error) {
      console.warn('Failed to clear session snapshot', error);
    }
  }
};

interface User {
  id?: string;
  username?: string;
  email?: string;
  [key: string]: any;
}

interface AuthContextType {
  user: User | null;
  login: (data: any) => void;
  logout: () => void;
  loading: boolean;
  refreshToken: () => Promise<boolean>;
  isAuthenticated: boolean;
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

  // Combined effect to handle authentication verification
  // This is a single effect to avoid race conditions from multiple effects
  useEffect(() => {
    const verifyAuthentication = async () => {
      // Skip verification if we just logged in to avoid race conditions
      if (skipNextVerification) {
        setSkipNextVerification(false);
        setLoading(false);
        return;
      }
      
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        // Check if token is expired using standardized function
        if (isTokenExpired()) {
          // Token expired, attempt to refresh
          const refreshSuccessful = await refreshToken();
          if (!refreshSuccessful) {
            throw new Error('Token refresh failed');
          }
        } else {
          // Verify token using apiClient with proper endpoint constant
          const { success, data } = await api.get(API_ENDPOINTS.AUTH.VERIFY);
          
          if (!success) throw new Error('Token verification failed');
          
          // Extract user data from the backend response
          if (data.success && data.user) {
            const newUser = data.user;
            setUser(newUser);
            setIsAuthenticated(true);

            // Capture session snapshot
            SessionPersistence.captureSnapshot(newUser, token);
          } else {
            throw new Error('Invalid user data');
          }
        }
      } catch (error) {
        // Any error in verification flow leads to logout
        clearAuthTokens();
        setToken(null);
        setUser(null);
        setIsAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };
    
    verifyAuthentication();
  }, [token]); // Only depend on token to avoid race conditions

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
      const authLogs = JSON.parse(localStorage.getItem('auth_logs') || '[]');
      authLogs.push(logEntry);
      // Keep only last 50 log entries
      localStorage.setItem('auth_logs', JSON.stringify(authLogs.slice(-50)));
    } catch (e) {
      console.error('Failed to log authentication event', e);
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
      const response = await api.post<{token: string, username?: string}>(API_ENDPOINTS.AUTH.REFRESH_TOKEN, {});
      
      if (!response.success || !response.data?.token) {
        throw new Error('Token refresh failed: Invalid response');
      }
      
      const { token, username } = response.data;
      
      // Determine storage type based on where the current token is stored
      const inLocalStorage = localStorage.getItem(TOKEN_KEY) !== null;
      const rememberMe = inLocalStorage; // If in localStorage, user wanted persistent login
      
      // Store the new token with the same preference
      storeAuthToken(token, rememberMe);
      
      // Update local token state
      setToken(token);
      setIsAuthenticated(true);
      
      // Optional: Update username if provided
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

  const login = (data: any) => {
    try {
      if (!data.token) {
        throw new Error('No token found in login data');
      }
      
      // Store token with remember me preference if provided
      // Using ternary to correctly handle all cases including false values
      const rememberMe = data.remember_me !== undefined ? data.remember_me : true; // Default to true for persistent login
      
      // Store token with remember me preference
      storeAuthToken(data.token, rememberMe);
      
      // Set flag to skip next verification cycle to avoid race condition
      setSkipNextVerification(true);
      
      // Update application state
      setToken(data.token); // Ensure token state is synchronized
      setUser(data.user || {});
      setIsAuthenticated(true);
    } catch (error) {
      console.error('Login failed:', error instanceof Error ? error.message : 'Unknown error');
      // Ensure auth state is reset if login fails
      clearAuthTokens();
      setToken(null);
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  const logout = async () => {
    try {
      // Call logout endpoint if token exists
      if (token) {
        // Use standardized apiClient for logout
        await api.post(API_ENDPOINTS.AUTH.LOGOUT, {});
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear session snapshot
      SessionPersistence.clearSnapshot();

      // Always clear local token storage
      clearAuthTokens();
      setToken(null);
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      login, 
      logout, 
      loading,
      refreshToken,
      isAuthenticated
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
