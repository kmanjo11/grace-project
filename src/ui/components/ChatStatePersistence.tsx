import React, { useEffect, useCallback, useMemo, useRef } from 'react';
import { useAppState } from '../context/AppStateContext';

// Match the exact ChatMessage interface from Chat.tsx
interface ChatMessage {
  sender?: 'user' | 'grace';
  text?: string;
  timestamp?: string;
  user?: string; // For API response format
  bot?: string; // For API response format
}

// Match the exact ChatSession interface from Chat.tsx with necessary extensions
interface ChatSession {
  id: string;
  name: string;
  lastActivity: string;
  messages: ChatMessage[];
  session_id?: string; // For API compatibility
  topic?: string; // For API compatibility
  // Additional fields needed for persistence
  scrollPosition?: number;
  unread_count?: number;
  created_at?: string;
  updated_at?: string;
}

// Type for the state.chatState.sessions entries
interface PersistentChatSession {
  id: string;
  session_id?: string;
  name?: string;
  topic?: string;
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
}

/**
 * Hook to manage chat state persistence
 * This syncs the Chat component state with our global persistence layer
 * FIXED: All callbacks memoized, stable dependencies, no timestamp regeneration
 */
export const useChatStatePersistence = (
  sessionId: string | null,
  sessions: ChatSession[],
  messages: ChatMessage[],
  draftMessage: string = ''
) => {
  const { state, dispatch } = useAppState();
  const PERSIST_DISABLED = (process.env.NEXT_PUBLIC_DISABLE_STATE_PERSIST || '').toString() === '1' || (process.env.NEXT_PUBLIC_DISABLE_STATE_PERSIST || '').toString().toLowerCase() === 'true';
  
  // Refs to prevent unnecessary effect triggers
  const lastSessionsRef = useRef<string>('');
  const lastMessagesRef = useRef<string>('');
  const lastDraftRef = useRef<string>('');

  // FIXED: Memoized getStoredSessions to prevent unnecessary recalculations
  const getStoredSessions = useCallback((): ChatSession[] => {
    // First check if there are any sessions in our persistent state
    if (state.chatState?.sessions && Object.keys(state.chatState.sessions).length > 0) {
      // Convert the sessions object to a properly structured array
      return Object.values(state.chatState.sessions || {}).map((session: PersistentChatSession) => {
        // Ensure each session conforms to the ChatSession interface
        return {
          id: session.id || session.session_id || '',
          session_id: session.session_id || session.id || '',
          name: session.name || session.topic || `Chat ${(session.session_id || session.id || '').slice(0, 6)}`,
          topic: session.topic || session.name || '',
          lastActivity: session.updated_at || new Date().toISOString(),
          messages: Array.isArray(session.messages) ? session.messages.map(msg => ({
            sender: msg.role === 'user' ? 'user' : 'grace',
            text: msg.content || '',
            timestamp: msg.timestamp || new Date().toISOString(),
            user: msg.role === 'user' ? msg.content : undefined,
            bot: msg.role === 'assistant' ? msg.content : undefined
          })) : [],
          scrollPosition: session.scrollPosition,
          unread_count: session.unread_count || 0
        };
      });
    }
    
    // If no sessions in state, check localStorage cache
    if (PERSIST_DISABLED) {
      return [];
    }
    const activeSessionId = typeof window !== 'undefined' ? localStorage.getItem('activeSessionId') : null;
    if (activeSessionId) {
      try {
        // Try to load cached messages for this session
        const cachedMessages = loadMessagesFromCache(activeSessionId);
        if (cachedMessages.length > 0) {
          return [{
            id: activeSessionId,
            session_id: activeSessionId,
            name: `Chat ${activeSessionId.slice(0, 6)}`,
            topic: `Chat ${activeSessionId.slice(0, 6)}`,
            lastActivity: localStorage.getItem(`lastSynced_${activeSessionId}`) || new Date().toISOString(),
            messages: cachedMessages
          }];
        }
      } catch (e) {
        console.error('Error loading sessions from cache:', e);
      }
    }
    
    return [];
  }, [state.chatState?.sessions, PERSIST_DISABLED]); // Only depend on sessions object
  
  // FIXED: Memoized loadMessagesFromCache to prevent unnecessary recalculations
  const loadMessagesFromCache = useCallback((sid: string): ChatMessage[] => {
    if (!sid) return [];
    
    // Try multiple sources in order of preference
    try {
      // 1. First check persistent global state
      const sessionMessages = state.chatState?.sessions?.[sid]?.messages;
      if (Array.isArray(sessionMessages) && sessionMessages.length > 0) {
        console.log(`Restoring ${sessionMessages.length} messages from global state for session ${sid}`);
        return sessionMessages.map(msg => ({
          sender: msg.role === 'user' ? 'user' : 'grace',
          text: msg.content || '',
          timestamp: msg.timestamp || new Date().toISOString(),
          user: msg.role === 'user' ? msg.content : undefined,
          bot: msg.role === 'assistant' ? msg.content : undefined
        }));
      }
      
      // 2. Then check localStorage
      if (PERSIST_DISABLED) return [];
      const savedMessages = typeof window !== 'undefined' ? localStorage.getItem(`messages_${sid}`) : null;
      if (savedMessages) {
        const parsedMessages = JSON.parse(savedMessages);
        if (Array.isArray(parsedMessages) && parsedMessages.length > 0) {
          console.log(`Restoring ${parsedMessages.length} messages from localStorage for session ${sid}`);
          return parsedMessages;
        }
      }
    } catch (e) {
      console.error('Error loading messages from cache:', e);
    }
    
    return [];
  }, [state.chatState?.sessions, PERSIST_DISABLED]); // Only depend on sessions object
  
  // FIXED: Stabilized effect with refs to prevent loops
  useEffect(() => {
    const storedSessions = getStoredSessions();
    if (storedSessions.length > 0 && sessions.length === 0) {
      console.log('Chat sessions available in persistent state', storedSessions);
    }
  }, [getStoredSessions, sessions.length]); // Only depend on memoized function and length

  // FIXED: Save session state with structural equality checks to prevent loops
  useEffect(() => {
    if (!sessionId || sessions.length === 0) return;
    
    // Create stable session map
    const sessionMap = sessions.reduce<Record<string, PersistentChatSession>>((acc, session) => {
      const sessionKey = session.session_id || session.id;
      if (sessionKey) {
        // FIXED: Use existing timestamp to avoid regeneration
        const existingSession = state.chatState?.sessions?.[sessionKey];
        acc[sessionKey] = {
          id: session.id,
          session_id: session.session_id || session.id,
          topic: session.topic || session.name,
          name: session.name,
          created_at: session.created_at || session.lastActivity,
          // FIXED: Keep existing updated_at to prevent timestamp churn
          updated_at: existingSession?.updated_at || session.updated_at || session.lastActivity,
          preview_message: session.messages && session.messages.length > 0 ?
            (session.messages[session.messages.length - 1].text ||
             session.messages[session.messages.length - 1].user ||
             session.messages[session.messages.length - 1].bot) : '',
          // FIXED: Preserve existing messages to prevent flip-flopping
          messages: existingSession?.messages || [],
          scrollPosition: session.scrollPosition,
          unread_count: session.unread_count || 0
        };
      }
      return acc;
    }, {});

    // FIXED: Use refs to check if anything actually changed
    const currentSessionsStr = JSON.stringify(sessionMap);
    const currentActive = sessions.map(s => s.session_id || s.id).join('|');
    const currentDraft = draftMessage || '';
    
    if (lastSessionsRef.current !== currentSessionsStr || 
        lastDraftRef.current !== currentDraft ||
        state.chatState?.currentSessionId !== sessionId) {
      
      lastSessionsRef.current = currentSessionsStr;
      lastDraftRef.current = currentDraft;
      
      dispatch({
        type: 'SET_CHAT_STATE',
        payload: {
          activeSessions: sessions.map(s => s.session_id || s.id),
          currentSessionId: sessionId,
          sessions: sessionMap,
          draftMessages: {
            ...(state.chatState?.draftMessages || {}),
            [sessionId]: draftMessage
          }
        }
      });
    }
    
    // Persist to localStorage (separate from dispatch to prevent loops)
    const currentSession = sessions.find(s => s.id === sessionId || s.session_id === sessionId);
    if (!PERSIST_DISABLED && currentSession && Array.isArray(currentSession.messages) && currentSession.messages.length > 0) {
      persistMessages(sessionId, currentSession.messages);
    }
  }, [sessionId, sessions, draftMessage, state.chatState?.sessions, state.chatState?.currentSessionId, dispatch]);

  // FIXED: Stabilized message sync effect with refs to prevent loops
  useEffect(() => {
    if (!sessionId || messages.length === 0 || !state.chatState?.sessions) return;
    
    const sessionKey = sessionId;
    const currentSession = state.chatState.sessions[sessionKey];
    const currentMessagesStr = JSON.stringify(messages);
    
    // Only update if messages actually changed
    if (currentSession && lastMessagesRef.current !== currentMessagesStr) {
      lastMessagesRef.current = currentMessagesStr;
      
      const updatedSessions = {
        ...state.chatState.sessions,
        [sessionKey]: {
          ...currentSession,
          messages: messages,
          // FIXED: Only update timestamp when messages actually change
          updated_at: new Date().toISOString()
        }
      };
      
      dispatch({
        type: 'SET_CHAT_STATE',
        payload: {
          sessions: updatedSessions
        }
      });
    }
  }, [sessionId, messages, state.chatState?.sessions, dispatch]);

  // FIXED: Memoized persistMessages function
  const persistMessages = useCallback((sid: string, msgs: ChatMessage[]) => {
    if (!sid || !msgs || msgs.length === 0) {
      // Skip persisting empty arrays to avoid loops and noise
      return;
    }
    try {
      console.log(`Persisting ${msgs.length} messages for session ${sid}`);
      
      // Only store a limited number of messages to prevent localStorage overflows
      const messagesToStore = msgs.slice(-100); // Store more messages (up to 100)
      
      // Store in localStorage as a backup
      if (!PERSIST_DISABLED) {
        localStorage.setItem(`messages_${sid}`, JSON.stringify(messagesToStore));
        localStorage.setItem(`lastSynced_${sid}`, new Date().toISOString());
        localStorage.setItem('activeSessionId', sid);
      }

      // Note: Do NOT dispatch global state updates here to avoid recursive update loops.
    } catch (e) {
      console.error('Failed to store messages:', e);
    }
  }, [PERSIST_DISABLED]); // No dependencies needed - pure function
  
  // FIXED: Properly memoized initializeFromPersistedState function
  const initializeFromPersistedState = useCallback((setSessionsFunc: (sessions: ChatSession[]) => void, setSessionIdFunc: (id: string | null) => void) => {
    const storedSessions = getStoredSessions();
    
    if (storedSessions.length > 0 && sessions.length === 0) {
      // Set the sessions from storage
      setSessionsFunc(storedSessions);
      
      // Set the active session ID if available - use same approach as Chat.tsx
      const activeSessionId = PERSIST_DISABLED ? null : (typeof window !== 'undefined' ? localStorage.getItem('activeSessionId') : null);
      if (activeSessionId) {
        // Check if this session exists in our stored sessions
        const sessionExists = storedSessions.some(s => 
          s.session_id === activeSessionId || s.id === activeSessionId
        );
        
        if (sessionExists) {
          setSessionIdFunc(activeSessionId);
        } else if (state.chatState?.currentSessionId) {
          setSessionIdFunc(state.chatState.currentSessionId);
        } else {
          // Fall back to first session
          setSessionIdFunc(storedSessions[0].session_id || storedSessions[0].id);
        }
      } else if (state.chatState?.currentSessionId) {
        setSessionIdFunc(state.chatState.currentSessionId);
      } else {
        // Fall back to first session
        setSessionIdFunc(storedSessions[0].session_id || storedSessions[0].id);
      }
      
      return true; // Indicate that we restored from persisted state
    }
    
    return false; // Indicate that we did not restore (no stored sessions or sessions already loaded)
  }, [getStoredSessions, sessions.length, state.chatState?.currentSessionId, PERSIST_DISABLED]);
  
  return {
    // Main functions for state initialization and persistence
    initializeFromPersistedState,
    getStoredSessions,
    loadMessagesFromCache,
    persistMessages,
    
    // FIXED: All callback functions properly memoized
    syncScrollPosition: useCallback((position: number) => {
      if (!sessionId) return;
      
      // Save scroll position in both localStorage and global state
      if (!PERSIST_DISABLED) {
        localStorage.setItem(`scrollPosition_${sessionId}`, position.toString());
      }
      
      dispatch({
        type: 'SET_CHAT_STATE',
        payload: {
          sessions: {
            ...(state.chatState?.sessions || {}),
            [sessionId]: {
              ...(state.chatState?.sessions?.[sessionId] || {}),
              scrollPosition: position
            }
          }
        }
      });
    }, [sessionId, state.chatState?.sessions, dispatch, PERSIST_DISABLED]),
    
    // FIXED: Memoized getSavedScrollPosition
    getSavedScrollPosition: useCallback(() => {
      if (!sessionId) return null;
      
      // First check localStorage (Chat.tsx approach)
      const localPosition = PERSIST_DISABLED ? null : (typeof window !== 'undefined' ? localStorage.getItem(`scrollPosition_${sessionId}`) : null);
      if (localPosition) {
        return parseInt(localPosition, 10);
      }
      
      // Fall back to global state
      if (state.chatState?.sessions?.[sessionId]) {
        return state.chatState.sessions[sessionId].scrollPosition;
      }
      
      return null;
    }, [sessionId, state.chatState?.sessions, PERSIST_DISABLED]),
    
    // FIXED: Memoized getSavedDraftMessage
    getSavedDraftMessage: useCallback(() => {
      if (!sessionId) return '';
      
      // First check localStorage (Chat.tsx approach)
      const localDraft = PERSIST_DISABLED ? null : (typeof window !== 'undefined' ? localStorage.getItem(`draft_${sessionId}`) : null);
      if (localDraft) {
        return localDraft;
      }
      
      // Fall back to global state
      if (state.chatState?.draftMessages && sessionId in state.chatState.draftMessages) {
        return state.chatState.draftMessages[sessionId] || '';
      }
      
      return '';
    }, [sessionId, state.chatState?.draftMessages, PERSIST_DISABLED]),
    
    // FIXED: Memoized updateDraftMessage with change detection
    updateDraftMessage: useCallback((message: string) => {
      if (!sessionId) return;
      
      // Skip if unchanged to avoid noisy dispatch loops
      const current = state.chatState?.draftMessages?.[sessionId] || '';
      if (current === message) {
        return;
      }
      
      // Save in both localStorage and global state for consistent behavior with Chat.tsx
      if (!PERSIST_DISABLED) {
        localStorage.setItem(`draft_${sessionId}`, message);
      }
      
      dispatch({
        type: 'SET_CHAT_STATE',
        payload: {
          draftMessages: {
            ...(state.chatState?.draftMessages || {}),
            [sessionId]: message
          }
        }
      });
    }, [sessionId, state.chatState?.draftMessages, dispatch, PERSIST_DISABLED])
  };
};

export default useChatStatePersistence;
