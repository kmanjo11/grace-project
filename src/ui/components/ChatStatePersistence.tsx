import React, { useEffect } from 'react';
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
 */
export const useChatStatePersistence = (
  sessionId: string | null,
  sessions: ChatSession[],
  messages: ChatMessage[],
  draftMessage: string = ''
) => {
  const { state, dispatch } = useAppState();

  // Get stored sessions from state - ensure compatibility with Chat.tsx structure
  const getStoredSessions = (): ChatSession[] => {
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
    const activeSessionId = localStorage.getItem('activeSessionId');
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
  };
  
  // Helper to load messages from cache - match the function in Chat.tsx
  const loadMessagesFromCache = (sid: string): ChatMessage[] => {
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
      const savedMessages = localStorage.getItem(`messages_${sid}`);
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
  };
  
  // Effect to log when we have sessions available in state
  useEffect(() => {
    const storedSessions = getStoredSessions();
    if (storedSessions.length > 0 && sessions.length === 0) {
      console.log('Chat sessions available in persistent state', storedSessions);
    }
  }, [state.chatState?.sessions, sessions]);

  // Save the current session state whenever it changes
  useEffect(() => {
    if (sessionId && sessions.length > 0) {
      // Convert sessions array to a record indexed by session ID
      // Use the same sessionId format as in Chat.tsx
      const sessionMap = sessions.reduce<Record<string, PersistentChatSession>>((acc, session) => {
        const sessionKey = session.session_id || session.id;
        if (sessionKey) {
          // Transform to the format our persistence expects
          acc[sessionKey] = {
            id: session.id,
            session_id: session.session_id || session.id,
            topic: session.topic || session.name,
            name: session.name,
            created_at: session.created_at || session.lastActivity,
            updated_at: session.lastActivity || new Date().toISOString(),
            preview_message: session.messages && session.messages.length > 0 ? 
              (session.messages[session.messages.length-1].text || 
               session.messages[session.messages.length-1].user || 
               session.messages[session.messages.length-1].bot) : '',
            messages: session.messages.map(msg => ({
              id: msg.timestamp || new Date().toISOString(),
              content: msg.text || msg.user || msg.bot || '',
              role: msg.sender === 'user' ? 'user' : 'assistant',
              timestamp: msg.timestamp || new Date().toISOString()
            })),
            scrollPosition: session.scrollPosition,
            unread_count: session.unread_count || 0
          };
        }
        return acc;
      }, {});

      // Update global state
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
      
      // Also use the same localStorage persistence as Chat.tsx
      const currentSession = sessions.find(s => s.id === sessionId || s.session_id === sessionId);
      if (currentSession && currentSession.messages) {
        persistMessages(sessionId, currentSession.messages);
      }
    }
  }, [sessions, sessionId, messages, draftMessage, dispatch]);

  // Sync message state between local and global
  useEffect(() => {
    if (sessionId && messages.length > 0 && state.chatState?.sessions) {
      const sessionKey = sessionId;
      const currentSession = state.chatState.sessions[sessionKey];
      
      if (currentSession && !arraysEqual(currentSession.messages || [], messages)) {
        const updatedSessions = {
          ...state.chatState.sessions,
          [sessionKey]: {
            ...currentSession,
            messages: messages,
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
    }
  }, [messages, sessionId, state.chatState?.sessions, dispatch]);

  // Helper to compare arrays
  const arraysEqual = (a: any[], b: any[]) => {
    if (a.length !== b.length) return false;
    
    // Simple length-based check for performance
    return a.length === b.length;
  };

  // Helper function to persist messages - match the function in Chat.tsx
  const persistMessages = (sid: string, msgs: ChatMessage[]) => {
    if (!sid || !msgs) return;
    try {
      console.log(`Persisting ${msgs.length} messages for session ${sid}`);
      
      // Only store a limited number of messages to prevent localStorage overflows
      const messagesToStore = msgs.slice(-100); // Store more messages (up to 100)
      
      // Store in localStorage as a backup
      localStorage.setItem(`messages_${sid}`, JSON.stringify(messagesToStore));
      localStorage.setItem(`lastSynced_${sid}`, new Date().toISOString());
      localStorage.setItem('activeSessionId', sid);
      
      // Also store in global AppState for better persistence across refreshes
      // Convert to the format expected by the AppState
      const persistentMessages = messagesToStore.map(msg => ({
        id: Math.random().toString(36).substring(2, 15),
        content: msg.text || msg.user || msg.bot || '',
        role: msg.sender === 'user' || msg.user ? 'user' : 'assistant',
        timestamp: msg.timestamp || new Date().toISOString()
      }));
      
      // Update chatContext for DynamicStateSnapshot compatibility
      dispatch({
        type: 'SET_CHAT_CONTEXT',
        payload: {
          currentConversationId: sid,
          lastMessageTimestamp: new Date().getTime()
        }
      });
      
      // Update chat state in global AppState
      dispatch({
        type: 'SET_CHAT_STATE',
        payload: {
          currentSessionId: sid,
          sessions: {
            ...(state.chatState?.sessions || {}),
            [sid]: {
              id: sid,
              session_id: sid,
              messages: persistentMessages,
              updated_at: new Date().toISOString(),
              // Preserve existing metadata if available
              ...(state.chatState?.sessions?.[sid] || {}),
              // Update with latest message info
              preview_message: messagesToStore[messagesToStore.length - 1]?.text || ''
            }
          }
        }
      });
    } catch (e) {
      console.error('Failed to store messages:', e);
    }
  };
  
  // Function to initialize sessions from persisted state if available
  const initializeFromPersistedState = (setSessionsFunc: (sessions: ChatSession[]) => void, setSessionIdFunc: (id: string | null) => void) => {
    const storedSessions = getStoredSessions();
    
    if (storedSessions.length > 0 && sessions.length === 0) {
      // Set the sessions from storage
      setSessionsFunc(storedSessions);
      
      // Set the active session ID if available - use same approach as Chat.tsx
      const activeSessionId = localStorage.getItem('activeSessionId');
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
  };
  
  return {
    // Main functions for state initialization and persistence
    initializeFromPersistedState,
    getStoredSessions,
    loadMessagesFromCache,
    persistMessages,
    
    // Functions to sync specific aspects of chat state
    syncScrollPosition: (position: number) => {
      if (!sessionId) return;
      
      // Save scroll position in both localStorage and global state
      localStorage.setItem(`scrollPosition_${sessionId}`, position.toString());
      
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
    },
    
    // Get saved scroll position for current session - check both localStorage and global state
    getSavedScrollPosition: () => {
      if (!sessionId) return null;
      
      // First check localStorage (Chat.tsx approach)
      const localPosition = localStorage.getItem(`scrollPosition_${sessionId}`);
      if (localPosition) {
        return parseInt(localPosition, 10);
      }
      
      // Fall back to global state
      if (state.chatState?.sessions?.[sessionId]) {
        return state.chatState.sessions[sessionId].scrollPosition;
      }
      
      return null;
    },
    
    // Get saved draft message for current session
    getSavedDraftMessage: () => {
      if (!sessionId) return '';
      
      // First check localStorage (Chat.tsx approach)
      const localDraft = localStorage.getItem(`draft_${sessionId}`);
      if (localDraft) {
        return localDraft;
      }
      
      // Fall back to global state
      if (state.chatState?.draftMessages && sessionId in state.chatState.draftMessages) {
        return state.chatState.draftMessages[sessionId] || '';
      }
      
      return '';
    },
    
    // Directly update draft message
    updateDraftMessage: (message: string) => {
      if (!sessionId) return;
      
      // Save in both localStorage and global state for consistent behavior with Chat.tsx
      localStorage.setItem(`draft_${sessionId}`, message);
      
      dispatch({
        type: 'SET_CHAT_STATE',
        payload: {
          draftMessages: {
            ...(state.chatState?.draftMessages || {}),
            [sessionId]: message
          }
        }
      });
    }
  };
};

export default useChatStatePersistence;
