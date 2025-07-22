import React, { createContext, useContext, useEffect, useState } from 'react';
import { useRouter } from 'next/router';

// Import from original paths
// When adapting to Next.js, ensure these utilities are also copied to the static folder
// Import API and endpoints
// You may need to copy these from your original project to the static folder
const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/api/auth/login',
    REGISTER: '/api/auth/register',
    VERIFY_TOKEN: '/api/auth/verify',
    LOGOUT: '/api/auth/logout',
    REFRESH_TOKEN: '/api/auth/refresh',
    FORGOT_PASSWORD: '/api/auth/forgot-password',
    RESET_PASSWORD: '/api/auth/reset-password',
    VALIDATE: '/api/auth/validate' // Added missing VALIDATE endpoint
  },
  WALLET: {
    DATA: '/api/wallet/data',
    INFO: '/api/wallet/info',
    MANGO_BALANCE: '/api/wallet/mango-balance',
    GENERATE: '/api/wallet/generate',
    SEND: '/api/wallet/send',
    CONNECT_PHANTOM: '/api/wallet/connect-phantom',
    COMPLETE_PHANTOM: '/api/wallet/complete-phantom',
    DISCONNECT_PHANTOM: '/api/wallet/disconnect-phantom',
    BALANCE: '/api/wallet/balance',
    TRANSACTIONS: '/api/wallet/transactions',
    GET_USER_WALLET: '/api/wallet/user-wallet', // Added missing endpoint
    GENERATE_WALLET: '/api/wallet/generate-wallet' // Added missing endpoint
  }
};

// Simple API client for Next.js
const api = {
  get: async (url: string, params?: any) => {
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      const data = await response.json();
      return { success: response.ok, data };
    } catch (error) {
      console.error('API GET error:', error);
      return { success: false, error };
    }
  },
  post: async (url: string, body: any) => {
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(body)
      });
      const data = await response.json();
      return { success: response.ok, data };
    } catch (error) {
      console.error('API POST error:', error);
      return { success: false, error };
    }
  }
};

// Import standardized auth utils
import {
  getAuthToken,
  getTokenExpiry,
  storeAuthToken,
  clearAuthTokens,
  isTokenExpired,
  addAuthHeaders,
  TOKEN_KEY
} from '../../utils/authUtils';

// Improved session persistence utility to avoid conflicts with form state
const SessionPersistence = {
  STORAGE_KEY: 'GRACE_SESSION_SNAPSHOT',
  
  // Safely capture session snapshot with minimal data to avoid interference
  captureSnapshot(user: User | null, token: string | null) {
    try {
      if (typeof window === 'undefined' || !user || !token) {
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
      sessionStorage.setItem(this.STORAGE_KEY, JSON.stringify(snapshot));
    } catch (error) {
      console.warn('Failed to capture session snapshot', error);
      // Silently fail - don't let snapshot errors affect the application
    }
  },

  // Retrieve session snapshot with validation
  retrieveSnapshot(): { user: User | null, token: string | null } {
    try {
      if (typeof window === 'undefined') {
        return { user: null, token: null };
      }
      
      const snapshotStr = sessionStorage.getItem(this.STORAGE_KEY);
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
  [key: string]: any;
}

interface AuthContextType {
  user: User | null;
  login: (data: any) => Promise<void>;
  logout: () => void;
  loading: boolean;
  refreshToken: () => Promise<boolean>;
  isAuthenticated: boolean;
}

// Create context with default value that matches the type
const defaultContextValue: AuthContextType = {
  user: null,
  login: async () => {},
  logout: () => {},
  loading: true,
  refreshToken: async () => false,
  isAuthenticated: false
};

const AuthContext = createContext<AuthContextType>(defaultContextValue);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  // Use state for token to ensure it's updated when changed
  const [token, setToken] = useState<string | null>(null);
  // Add flag to prevent verification immediately after login
  const [skipNextVerification, setSkipNextVerification] = useState<boolean>(false);
  
  // Initialize token from auth utils only on client side
  useEffect(() => {
    if (typeof window !== 'undefined') {
      setToken(getAuthToken());
    }
  }, []);
  
  // Update token state whenever auth state changes
  useEffect(() => {
    if (typeof window !== 'undefined') {
      setToken(getAuthToken());
    }
  }, [isAuthenticated]);
  
  // Verify authentication on mount and when token changes
  useEffect(() => {
    // Skip verification during SSR
    if (typeof window === 'undefined') return;
    
    // Only verify if not skipping and not already loading
    if (!skipNextVerification && !loading) {
      verifyAuthentication();
    }
    // Reset skip flag after it's been respected
    if (skipNextVerification) {
      setSkipNextVerification(false);
    }
  }, [token]);
  
  // Verify authentication status
  const verifyAuthentication = async () => {
    setLoading(true);
    
    try {
      // Check if token exists and is not expired
      const currentToken = getAuthToken();
      
      if (!currentToken) {
        // No token, definitely not authenticated
        setIsAuthenticated(false);
        setUser(null);
        return;
      }
      
      // Check if token is expired
      if (isTokenExpired()) {
        // Try to refresh the token
        const refreshSuccessful = await refreshToken();
        
        if (!refreshSuccessful) {
          // Refresh failed, clear auth state
          setIsAuthenticated(false);
          setUser(null);
          return;
        }
        // If refresh was successful, we'll continue with verification
      }
      
      // At this point we have a valid token
      // Try to get user info to confirm authentication
      try {
        // Use standardized API client for validation request
        const response = await api.get(API_ENDPOINTS.AUTH.VALIDATE);
        
        if (response.success && response.data?.user) {
          // Authentication valid, update user state
          setUser(response.data.user);
          setIsAuthenticated(true);
          
          // Capture minimal session data to maintain logged in state
          SessionPersistence.captureSnapshot(response.data.user, currentToken);
        } else {
          // Invalid response from validation endpoint
          throw new Error('Invalid response from validation endpoint');
        }
      } catch (error) {
        console.error('Auth validation failed:', error);
        
        // Check if this is an unauthorized response (likely expired token)
        if (error instanceof Error && error.message.includes('401')) {
          // Try one last token refresh
          const refreshSuccessful = await refreshToken();
          
          if (!refreshSuccessful) {
            // Refresh failed, clear auth state
            clearAuthTokens();
            SessionPersistence.clearSnapshot();
            setIsAuthenticated(false);
            setUser(null);
          }
        } else {
          // Some other error, assume not authenticated
          setIsAuthenticated(false);
          setUser(null);
        }
      }
    } catch (error) {
      console.error('Authentication verification error:', error);
      setIsAuthenticated(false);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  // Enhanced logging utility for authentication events
  const logAuthEvent = (eventType: string, details: any = {}) => {
    if (process.env.NODE_ENV !== 'production') {
      console.log(`[AUTH EVENT] ${eventType}`, {
        timestamp: new Date().toISOString(),
        ...details
      });
    }
    
    // In production, this could send events to an analytics service
    // but we'll just do console logging for now
  };

  // Check if user has a wallet and generate one if not available
  const checkAndGenerateWallet = async () => {
    if (!user || !user.id) {
      console.warn('Cannot check wallet: No authenticated user');
      return;
    }
    
    try {
      // Check if user already has a wallet
      const walletResponse = await api.get(API_ENDPOINTS.WALLET.GET_USER_WALLET);
      
      if (walletResponse.success && walletResponse.data?.wallet) {
        // User already has a wallet, nothing to do
        return;
      }
      
      // User doesn't have a wallet, generate one
      const generateResponse = await api.post(API_ENDPOINTS.WALLET.GENERATE_WALLET, {});
      
      if (generateResponse.success && generateResponse.data?.wallet) {
        // Wallet successfully generated
        logAuthEvent('WALLET_GENERATED', {
          userId: user.id,
          walletAddress: generateResponse.data.wallet.address,
        });
      } else {
        throw new Error('Failed to generate wallet');
      }
    } catch (error) {
      console.error('Error checking/generating wallet:', error);
      logAuthEvent('WALLET_GENERATION_ERROR', {
        userId: user.id,
        error: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  };

  // Implement token refresh functionality with exponential backoff
  const refreshToken = async (retryCount = 0): Promise<boolean> => {
    const MAX_RETRIES = 2;
    
    try {
      logAuthEvent('TOKEN_REFRESH_ATTEMPT', { retryCount });
      
      // Calculate exponential backoff delay with jitter to prevent thundering herd
      const baseDelay = 1000; // 1 second base
      const maxJitter = 500; // 0.5 second max jitter
      const backoffDelay = retryCount > 0 
        ? Math.min(baseDelay * Math.pow(2, retryCount - 1), 10000) // Max 10 seconds
        : 0;
      const jitter = Math.random() * maxJitter;
      const delay = backoffDelay + jitter;
      
      // Wait for the backoff delay if this is a retry
      if (delay > 0) {
        await new Promise(resolve => setTimeout(resolve, delay));
      }
      
      // Make refresh request
      const response = await api.post(API_ENDPOINTS.AUTH.REFRESH_TOKEN, {});
      
      if (!response.success || !response.data?.token) {
        throw new Error('Token refresh failed: Invalid response');
      }
      
      const { token, username } = response.data;
      
      // Determine storage type based on where the current token is stored
      let rememberMe = true; // Default to true
      if (typeof window !== 'undefined') {
        const inLocalStorage = localStorage.getItem(TOKEN_KEY) !== null;
        rememberMe = inLocalStorage; // If in localStorage, user wanted persistent login
      }
      
      // Store the new token with the same preference
      await storeAuthToken(token, rememberMe);
      
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

  const login = async (data: any) => {
    try {
      if (!data.token) {
        throw new Error('No token found in login data');
      }
      
      // Store token with remember me preference if provided
      const rememberMe = data.remember_me !== undefined ? data.remember_me : true; // Default to true for persistent login
      
      // Store token and wait for it to complete
      await storeAuthToken(data.token, rememberMe);
      
      // Update application state
      setToken(data.token); // Ensure token state is synchronized
      setUser(data.user || {});
      setIsAuthenticated(true);
      
      // Capture minimal session data after successful login
      if (data.user) {
        SessionPersistence.captureSnapshot(data.user, data.token);
      }
      
      // Set flag to skip next verification cycle to avoid race condition
      setSkipNextVerification(true);
      
      // Automatically check for wallet and generate if needed
      // This ensures every user has a wallet automatically
      setTimeout(() => {
        checkAndGenerateWallet();
      }, 500); // Small delay to ensure auth is fully established
      
      // For Next.js, navigate to appropriate page after login
      router.push('/dashboard');
    } catch (error) {
      console.error('Login failed:', error instanceof Error ? error.message : 'Unknown error');
      // Ensure auth state is reset if login fails
      setTimeout(() => {
        clearAuthTokens();
        SessionPersistence.clearSnapshot();
      }, 0);
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
      
      // For Next.js, navigate to login page after logout
      router.push('/login');
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
  return context;
};
