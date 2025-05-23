import React, { createContext, useContext, useReducer, useEffect, useRef, useState, ReactNode } from 'react';
import StatePersistenceManager, { DynamicStateSnapshot } from '../utils/StatePersistence';
import { NavigateFunction } from 'react-router-dom';

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
  | { type: 'RESET' };

// State reducer
function appStateReducer(state: AppState, action: ActionType): AppState {
  switch (action.type) {
    case 'SET_TRADING_STATE':
      return { ...state, tradingState: { ...state.tradingState, ...action.payload } };
    case 'SET_WALLET_STATE':
      return { ...state, walletState: { ...state.walletState, ...action.payload } };
    case 'SET_CHAT_STATE':
      return { ...state, chatState: { ...state.chatState, ...action.payload } };
    case 'SET_SOCIAL_STATE':
      return { ...state, socialState: { ...state.socialState, ...action.payload } };
    case 'SET_UI_STATE':
      return { ...state, uiState: { ...state.uiState, ...action.payload } };
    case 'SET_PAGE_STATE':
      return { ...state, pageState: { ...state.pageState, ...action.payload } };
    case 'SET_WIDGET_STATES':
      return { ...state, widgetStates: { ...state.widgetStates, ...action.payload } };
    case 'SET_CHAT_CONTEXT':
      return { ...state, chatContext: { ...state.chatContext, ...action.payload } };
    case 'SET_USER_SESSION':
      return { ...state, userSession: { ...state.userSession, ...action.payload } };
    case 'UPDATE_XFEED':
      return {
        ...state,
        xfeed: {
          ...state.xfeed,
          ...action.payload,
          lastUpdated: Date.now()
        }
      };
    case 'HYDRATE_STATE':
      return { ...action.payload };
    case 'RESET_STATE':
      return initialState;
    // Compatibility aliases
    case 'HYDRATE':
      return { ...action.payload };
    case 'RESET':
      return initialState;
    default:
      return state;
  }
}

// Create context
interface AppStateContextType {
  state: AppState;
  dispatch: React.Dispatch<ActionType>;
  isStateLoading: boolean;
  isStateHydrated: boolean;
  isStateRecovered: boolean;
  isStateSyncing: boolean;
  hydrateFromStorage: (navigate?: NavigateFunction) => void;
}

const AppStateContext = createContext<AppStateContextType | undefined>(undefined);

// Provider component
interface AppStateProviderProps {
  children: ReactNode;
}

export function AppStateProvider({ children }: AppStateProviderProps) {
  const [state, dispatch] = useReducer(appStateReducer, initialState);
  const [isStateLoading, setIsStateLoading] = useState(true);
  const [isStateHydrated, setIsStateHydrated] = useState(false);
  const [isStateRecovered, setIsStateRecovered] = useState(false);
  const [isStateSyncing, setIsStateSyncing] = useState(false);
  const isUpdatingFromStorage = useRef(false);
  
  // Hydrate state from storage on initial load
  useEffect(() => {
    // Set loading state
    dispatch({ type: 'SET_UI_STATE', payload: { isLoading: true } });
    
    // Small delay to allow UI to render loading state
    setTimeout(() => {
      hydrateFromStorage();
      dispatch({ type: 'SET_UI_STATE', payload: { isLoading: false } });
    }, 300);
  }, []);
  
  // Listen for changes from other tabs
  useEffect(() => {
    const handleStorageChange = (event: StorageEvent) => {
      // Only process events for our storage key
      const STORAGE_KEY = 'GRACE_DYNAMIC_SNAPSHOT'; // Must match the key in StatePersistenceManager
      if (event.key === STORAGE_KEY) {
        // Prevent processing our own updates
        if (isUpdatingFromStorage.current) {
          return;
        }
        
        console.log('State changed in another tab, synchronizing...');
        try {
          // Update flag to prevent circular updates
          isUpdatingFromStorage.current = true;
          
          // Parse new state from storage
          const newState = event.newValue ? JSON.parse(event.newValue) : null;
          
          // Validate state before applying
          if (newState && typeof newState === 'object' && newState.timestamp) {
            // Signal that we're syncing from another tab
            setIsStateSyncing(true);
            
            // Only apply if the timestamp is newer
            if (!state.timestamp || newState.timestamp > state.timestamp) {
              dispatch({ type: 'HYDRATE_STATE', payload: newState });
              console.log('State synchronized from another tab');
            }
          }
          
          // Reset syncing state after a delay
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
    window.addEventListener('storage', handleStorageChange);
    
    // Cleanup event listener on unmount
    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, [state.timestamp]);
  
  // Save state to storage whenever it changes with debounce to prevent race conditions
  const debouncedSaveTimeout = useRef<number | null>(null);
  
  useEffect(() => {
    // Skip initial render to avoid overwriting with empty state
    if (Object.keys(state.tradingState || {}).length > 0 || 
        Object.keys(state.walletState || {}).length > 0 ||
        Object.keys(state.chatContext || {}).length > 0) {
      
      // Clear any existing timeout to debounce frequent updates
      if (debouncedSaveTimeout.current !== null) {
        clearTimeout(debouncedSaveTimeout.current);
      }
      
      // Debounce state saves to prevent excessive writes and race conditions
      debouncedSaveTimeout.current = window.setTimeout(() => {
        // Only save if we're not currently processing an update from storage
        if (!isUpdatingFromStorage.current) {
          // Ensure timestamp is updated
          const stateToSave = {
            ...state,
            timestamp: Date.now()
          };
          
          try {
            // Convert to async/await pattern to properly handle Promise
            (async () => {
              try {
                await StatePersistenceManager.captureSnapshot(stateToSave);
                console.log('State saved to localStorage', new Date().toISOString());
              } catch (error) {
                console.error('Error saving state to localStorage:', error);
              }
            })();
          } catch (error) {
            console.error('Error in state persistence flow:', error);
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
  
  // Function to hydrate state from storage
  const hydrateFromStorage = (navigate?: NavigateFunction) => {
    setIsStateLoading(true);
    const storedState = StatePersistenceManager.hydrateState(navigate);
    
    if (storedState) {
      // Check if this is a recovered state
      if ('recovered' in storedState && storedState.recovered === true) {
        setIsStateRecovered(true);
      }
      
      // Apply stored state via dispatches
      if (storedState.userSession) {
        dispatch({ type: 'SET_USER_SESSION', payload: storedState.userSession });
      }
      
      if (storedState.chatContext) {
        dispatch({ type: 'SET_CHAT_CONTEXT', payload: storedState.chatContext });
      }
      
      if (storedState.pageState) {
        dispatch({ type: 'SET_PAGE_STATE', payload: storedState.pageState });
      }
      
      if (storedState.widgetStates) {
        dispatch({ type: 'SET_WIDGET_STATES', payload: storedState.widgetStates });
      }
      
      setIsStateHydrated(true);
      setIsStateLoading(false);
    } else {
      setIsStateLoading(false);
    }
  };
  
  const contextValue: AppStateContextType = {
    state,
    dispatch,
    isStateLoading,
    isStateHydrated,
    isStateRecovered,
    isStateSyncing,
    hydrateFromStorage,
  };

  return (
    <AppStateContext.Provider value={contextValue}>
      {children}
    </AppStateContext.Provider>
  );
}

// Custom hook for using the app state
export function useAppState() {
  const context = useContext(AppStateContext);
  if (context === undefined) {
    throw new Error('useAppState must be used within an AppStateProvider');
  }
  return context;
}
