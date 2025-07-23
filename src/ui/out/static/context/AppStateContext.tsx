import React, { createContext, useContext, useReducer, useEffect, useRef, useState, ReactNode, useCallback } from 'react';
import { useRouter } from 'next/router';
// Import StatePersistence or create a placeholder if needed
// You should copy the original StatePersistence implementation to src/ui/static/utils/

// Placeholder implementation - replace with proper implementation from your project
interface DynamicStateSnapshot {
  timestamp: number;
  userSession: any;
  pageState?: any;
  chatContext?: any;
  widgetStates: any; 
  [key: string]: any;
}

const StatePersistenceManager = {
  async captureSnapshot(state: any): Promise<void> {
    if (typeof window !== 'undefined') {
      try {
        localStorage.setItem('GRACE_APP_STATE', JSON.stringify(state));
      } catch (error) {
        console.error('Error saving state to localStorage:', error);
      }
    }
  },

  async retrieveSnapshot(): Promise<DynamicStateSnapshot | null> {
    if (typeof window !== 'undefined') {
      try {
        const storedState = localStorage.getItem('GRACE_APP_STATE');
        if (storedState) {
          return JSON.parse(storedState) as DynamicStateSnapshot;
        }
      } catch (error) {
        console.error('Error retrieving state from localStorage:', error);
      }
    }
    return null;
  }
};

// Extend the DynamicStateSnapshot interface to include our additional app state
// Our extended app state interface that maintains compatibility with DynamicStateSnapshot
export interface AppState {
  // From DynamicStateSnapshot base
  timestamp: number;
  userSession: {
    token?: string;
    username?: string;
  };
  pageState: {
    lastVisitedPath?: string;
    scrollPositions?: Record<string, number>;
  };
  widgetStates: {
    tradingPositions?: any[];
    walletBalance?: number;
  };
  
  // Core DynamicStateSnapshot chatContext - we must maintain this exact structure
  chatContext: {
    currentConversationId?: string;
    draftMessage?: string;
    lastMessageTimestamp?: number;
  };
  
  // Application state metadata
  isHydrated?: boolean;
  isLoading?: boolean;
  lastSaved?: number;
  
  // Auth and user session state - aligns with AuthContext
  authSession?: {
    token?: string;
    expiresAt?: number;
    refreshToken?: string;
  };
  
  // Trading state extensions
  tradingState?: {
    selectedToken?: any;
    watchlist?: string[];
    tradeHistory?: any[];
    tradeForm?: any;
    resolution?: string;
    search?: string;
    positions?: any[];
  };
  
  // Social media feed settings
  xfeed?: {
    followedAccounts: string[];
    lastUpdated?: number;
  };
  
  // Wallet state extensions
  walletState?: {
    connectedWallets?: any[];
    transactions?: any[];
  };
  
  // Extended chat state - separate from the base chatContext to avoid type conflicts
  // Will be synced with the main chatContext as needed
  chatState?: {
    activeSessions?: string[];
    currentSessionId?: string;
    sessions?: {
      [sessionId: string]: {
        id: string;
        topic?: string;
        name?: string;
        created_at?: string;
        updated_at?: string;
        preview_message?: string;
        messages?: Array<{
          id: string;
          content: string;
          role: 'user' | 'assistant' | 'system';
          timestamp: string;
        }>;
        unread_count?: number;
        scrollPosition?: number;
      };
    };
    draftMessages?: {
      [sessionId: string]: string;
    };
  };
  
  // Social state
  socialState?: {
    posts?: any[];
    following?: string[];
    notifications?: any[];
  };
  
  // UI state
  uiState?: {
    darkMode?: boolean;
    sidebarOpen?: boolean;
    activeTabs?: Record<string, string>;
    theme?: string;
  };
}

// Initial state object
const initialState: AppState = {
  timestamp: Date.now(),
  userSession: {},
  authSession: {},
  // Standard chatContext from DynamicStateSnapshot
  chatContext: {
    currentConversationId: undefined,
    draftMessage: '',
    lastMessageTimestamp: 0
  },
  // Extended chat state
  chatState: {
    activeSessions: [],
    sessions: {},
    draftMessages: {}
  },
  pageState: {},
  widgetStates: {},
  // State metadata
  isHydrated: false,
  isLoading: false,
  lastSaved: 0,
  // Extended state
  tradingState: {},
  walletState: {},
  socialState: {},
  uiState: {
    darkMode: true,
    sidebarOpen: true,
  },
  xfeed: {
    followedAccounts: [],
    lastUpdated: undefined
  }
};

// Action types
type ActionType =
  | { type: 'SET_TRADING_STATE'; payload: any }
  | { type: 'SET_WALLET_STATE'; payload: any }
  | { type: 'SET_CHAT_CONTEXT'; payload: any }
  | { type: 'SET_CHAT_STATE'; payload: any }
  | { type: 'SET_SOCIAL_STATE'; payload: any }
  | { type: 'SET_UI_STATE'; payload: any }
  | { type: 'SET_PAGE_STATE'; payload: any }
  | { type: 'SET_WIDGET_STATES'; payload: any }
  | { type: 'SET_USER_SESSION'; payload: any }
  | { type: 'UPDATE_XFEED'; payload: any }
  | { type: 'HYDRATE_STATE'; payload: AppState }
  | { type: 'RESET_STATE' }
  | { type: 'HYDRATE'; payload: AppState }
  | { type: 'RESET' }
  | { type: 'UPDATE_AUTH'; payload: { user: any; token: string | null } };

// State reducer
const appStateReducer = (state: AppState, action: ActionType): AppState => {
  switch (action.type) {
    case 'SET_TRADING_STATE':
      return {
        ...state,
        tradingState: { ...(state.tradingState || {}), ...action.payload }
      };
    case 'SET_WALLET_STATE':
      return {
        ...state,
        walletState: { ...(state.walletState || {}), ...action.payload }
      };
    case 'SET_CHAT_CONTEXT':
      return {
        ...state,
        chatContext: { ...(state.chatContext || {}), ...action.payload }
      };
    case 'SET_CHAT_STATE':
      return {
        ...state,
        chatState: { ...(state.chatState || {}), ...action.payload }
      };
    case 'SET_SOCIAL_STATE':
      return {
        ...state,
        socialState: { ...(state.socialState || {}), ...action.payload }
      };
    case 'SET_UI_STATE':
      return {
        ...state,
        uiState: { ...(state.uiState || {}), ...action.payload }
      };
    case 'SET_PAGE_STATE':
      return {
        ...state,
        pageState: { ...(state.pageState || {}), ...action.payload }
      };
    case 'SET_WIDGET_STATES':
      return {
        ...state,
        widgetStates: { ...(state.widgetStates || {}), ...action.payload }
      };
    case 'SET_USER_SESSION':
      return {
        ...state,
        userSession: { ...(state.userSession || {}), ...action.payload }
      };
    case 'UPDATE_XFEED':
      return {
        ...state,
        xfeed: { ...(state.xfeed || { followedAccounts: [] }), ...action.payload }
      };
    case 'HYDRATE_STATE':
    case 'HYDRATE':
      return {
        ...state,
        ...action.payload,
        isHydrated: true
      };
    case 'RESET_STATE':
    case 'RESET':
      return { ...initialState, timestamp: Date.now() };
    case 'UPDATE_AUTH':
      return {
        ...state,
        authSession: {
          token: action.payload.token,
        },
        userSession: {
          ...state.userSession,
          ...action.payload.user
        }
      };
    default:
      return state;
  }
};

// Create context
export interface AppStateContextType {
  state: AppState;
  dispatch: React.Dispatch<ActionType>;
  isStateLoading: boolean;
  isStateHydrated: boolean;
  isStateRecovered: boolean;
  isStateSyncing: boolean;
  hydrateFromStorage: (router?: any) => Promise<void>;
}

// Create a default value for the context
const defaultContextValue: AppStateContextType = {
  state: initialState,
  dispatch: () => {},
  isStateLoading: false,
  isStateHydrated: false,
  isStateRecovered: false,
  isStateSyncing: false,
  hydrateFromStorage: async () => {}
};

const AppStateContext = createContext<AppStateContextType>(defaultContextValue);

// Provider component
interface AppStateProviderProps {
  children: ReactNode;
}

export function AppStateProvider({ children }: AppStateProviderProps) {
  const [state, dispatch] = useReducer(appStateReducer, initialState);
  const [isStateLoading, setIsStateLoading] = useState<boolean>(true);
  const [isStateHydrated, setIsStateHydrated] = useState<boolean>(false);
  const [isStateRecovered, setIsStateRecovered] = useState<boolean>(false);
  const [isStateSyncing, setIsStateSyncing] = useState<boolean>(false);
  
  // Reference to track whether we're currently updating from storage
  const isUpdatingFromStorage = useRef<boolean>(false);
  
  // For Next.js, we need to use the router directly
  const router = useRouter();
  
  // Hydrate state from localStorage
  const hydrate = useCallback(async (router?: any) => {
    try {
      setIsStateLoading(true);
      const snapshot = await StatePersistenceManager.retrieveSnapshot();

      if (snapshot) {
        // Ensure snapshot has widgetStates to satisfy AppState type
        const completeSnapshot = {
          ...snapshot,
          widgetStates: snapshot.widgetStates || {}
        };
        
        dispatch({ type: 'HYDRATE_STATE', payload: completeSnapshot });

        // Apply any navigation based on hydrated state if needed
        if (router && completeSnapshot.userSession?.requiresPasswordChange) {
          router.push('/reset-password');
        }

        // Apply theme if stored
        applyTheme(completeSnapshot.uiState?.theme);

        setIsStateHydrated(true);
        setIsStateRecovered(true);
      }
    } catch (error) {
      console.error('Error hydrating state:', error);
    } finally {
      setIsStateLoading(false);
    }
  }, [dispatch]);
  
  // Initialize state from localStorage on mount
  useEffect(() => {
    hydrate();
  }, [hydrate]);
  
  // Listen for storage events from other tabs
  useEffect(() => {
    const handleStorageChange = (event: StorageEvent) => {
      // Check if this is a relevant storage event (for our app state)
      if (event.key && event.key.includes('GRACE_') && !isUpdatingFromStorage.current) {
        try {
          console.log('Storage change detected in another tab, syncing state');
          setIsStateSyncing(true);
          
          // Mark that we're updating from storage to prevent loops
          isUpdatingFromStorage.current = true;
          
          // Reload state from storage
          StatePersistenceManager.retrieveSnapshot().then(snapshot => {
            if (snapshot) {
              console.log('Syncing state from another tab');
              dispatch({
                type: 'HYDRATE_STATE',
                payload: snapshot
              });
            }
          });
          
          // Clear syncing flag after delay
          setTimeout(() => setIsStateSyncing(false), 1000);
        } catch (error) {
          console.error('Error synchronizing state from another tab:', error);
        } finally {
          // Reset flag after a short delay
          setTimeout(() => {
            isUpdatingFromStorage.current = false;
          }, 100);
        }
      }
    };
    
    // Add event listener for storage events
    if (typeof window !== 'undefined') {
      window.addEventListener('storage', handleStorageChange);
      
      // Cleanup event listener on unmount
      return () => {
        window.removeEventListener('storage', handleStorageChange);
      };
    }
    return undefined;
  }, []);
  
  // Save state to storage whenever it changes with debounce to prevent race conditions
  const debouncedSaveTimeout = useRef<NodeJS.Timeout | null>(null);
  const lastSavedTimestamp = useRef<number>(0);
  
  useEffect(() => {
    // Only run on client side
    if (typeof window === 'undefined') return;
    
    // Skip initial render to avoid overwriting with empty state
    // Only proceed if we have some meaningful state to save
    const hasContent = 
      Object.keys(state.tradingState || {}).length > 0 || 
      Object.keys(state.walletState || {}).length > 0 ||
      Object.keys(state.chatContext || {}).length > 0 ||
      Object.keys(state.chatState?.sessions || {}).length > 0;
    
    if (hasContent) {
      // Clear any existing timeout to debounce frequent updates
      if (debouncedSaveTimeout.current !== null) {
        clearTimeout(debouncedSaveTimeout.current);
      }
      
      // Debounce state saves to prevent excessive writes and race conditions
      debouncedSaveTimeout.current = setTimeout(() => {
        // Only save if we're not currently processing an update from storage
        if (!isUpdatingFromStorage.current) {
          // Don't save too frequently - at most once every 2 seconds
          const now = Date.now();
          if (now - lastSavedTimestamp.current > 2000) {
            lastSavedTimestamp.current = now;
            
            // Ensure timestamp is updated
            const stateToSave = {
              ...state,
              timestamp: now
            };
            
            // Add metadata for debugging
            if (state.chatContext?.currentConversationId) {
              console.log(`Saving state with active conversation: ${state.chatContext.currentConversationId}`);
            }
            
            try {
              // Convert to async/await pattern to properly handle Promise
              (async () => {
                try {
                  await StatePersistenceManager.captureSnapshot(stateToSave);
                  console.log('State saved to localStorage', new Date().toISOString());
                  
                  // Also ensure the activeSessionId is set in localStorage if we have a current conversation
                  if (state.chatContext?.currentConversationId && typeof window !== 'undefined') {
                    localStorage.setItem('activeSessionId', state.chatContext.currentConversationId);
                  }
                } catch (error) {
                  console.error('Error saving state to localStorage:', error);
                }
              })();
            } catch (error) {
              console.error('Error in state persistence flow:', error);
            }
          }
        }
        debouncedSaveTimeout.current = null;
      }, 300); // 300ms debounce time
    }
    
    // Cleanup timeout on unmount
    return () => {
      if (debouncedSaveTimeout.current !== null) {
        clearTimeout(debouncedSaveTimeout.current);
      }
    };
  }, [state]);
  
  const contextValue: AppStateContextType = {
    state,
    dispatch,
    isStateLoading,
    isStateHydrated,
    isStateRecovered,
    isStateSyncing,
    hydrateFromStorage: hydrate
  };

  // Cast the provider to avoid TypeScript compatibility issues with React JSX element types
  const AppStateProvider = AppStateContext.Provider as any;

  return (
    <AppStateProvider
      value={{
        state,
        dispatch,
        isStateLoading,
        isStateHydrated,
        isStateRecovered,
        isStateSyncing,
        hydrateFromStorage: hydrate
      }}
    >
      {children}
    </AppStateProvider>
  );
}

// Custom hook for using the app state
export function useAppState() {
  const context = useContext(AppStateContext);
  return context;
}
