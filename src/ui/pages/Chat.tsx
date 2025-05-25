// src/pages/Chat.tsx

import React, { useEffect, useState, FormEvent, useRef, useCallback } from 'react';
import { api, API_ENDPOINTS } from '../api/apiClient';
import { useAuth } from '../components/AuthContext';
import { getAuthToken } from '../utils/authUtils';
import { useChatStatePersistence } from '../components/ChatStatePersistence';
import XFeed from '../components/XFeed';

interface ChatMessage {
  sender?: 'user' | 'grace';
  text?: string;
  timestamp?: string;
  user?: string; // For API response format
  bot?: string; // For API response format
}

interface ChatSession {
  id: string;
  name: string;
  lastActivity: string;
  messages: ChatMessage[];
  session_id?: string; // For API compatibility
  topic?: string; // For API compatibility
}

export default function Chat() {
  // Use the Auth context for authentication state
  const { user, isAuthenticated } = useAuth();
  // Use standardized token function from authUtils
  const token = getAuthToken();
  
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  
  // Track if sessions have been loaded
  const [sessionsLoaded, setSessionsLoaded] = useState<boolean>(false);
  // Use ref to avoid duplicate session creation
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize chat state persistence hook
  const {
    initializeFromPersistedState,
    getSavedDraftMessage,
    updateDraftMessage,
    syncScrollPosition,
    getSavedScrollPosition
  } = useChatStatePersistence(sessionId, sessions, messages, input);

  // Helper function to generate a simple topic from message content
  const generateSimpleTopicFromMessage = (message: string | undefined | null): string => {
    if (!message) return 'New Conversation';
    
    try {
      // Take first 30 characters from the message, or up to the first period
      const firstSentence = message.split('.')[0].trim();
      const topicText = firstSentence.length > 30 ? 
        firstSentence.substring(0, 30) + '...' : 
        firstSentence;
      return topicText || 'New Conversation';
    } catch (e) {
      console.error('Error generating topic:', e);
      return 'New Conversation';
    }
  };
  
  // Helper function to persist messages to localStorage with timestamp
  const persistMessages = (sid: string, msgs: ChatMessage[]) => {
    if (!sid || !msgs) return;
    try {
      // Only store a limited number of messages to prevent localStorage overflows
      const messagesToStore = msgs.slice(-50); // Store just the last 50 messages
      localStorage.setItem(`messages_${sid}`, JSON.stringify(messagesToStore));
      
      // Store a timestamp with the messages to track freshness
      localStorage.setItem(`lastSynced_${sid}`, new Date().toISOString());
      
      // Always store the active session ID to ensure it's available when returning to the page
      localStorage.setItem('activeSessionId', sid);
    } catch (e) {
      console.error('Failed to store messages in localStorage:', e);
    }
  };
  
  // Helper function to load messages from cache
  const loadMessagesFromCache = (sid: string): ChatMessage[] => {
    if (!sid) return [];
    try {
      const savedMessages = localStorage.getItem(`messages_${sid}`);
      if (savedMessages) {
        const parsedMessages = JSON.parse(savedMessages);
        if (Array.isArray(parsedMessages) && parsedMessages.length > 0) {
          console.log('Loaded cached messages for session:', sid);
          return parsedMessages;
        }
      }
    } catch (e) {
      console.error('Failed to load messages from cache:', e);
    }
    return [];
  };
  
  // Track if component is mounted to prevent state updates after unmounting
  const isMountedRef = useRef(true);
  
  // Initialize from persisted state on component mount
  useEffect(() => {
    if (!sessionsLoaded && isAuthenticated) {
      const restored = initializeFromPersistedState(setSessions, setSessionId);
      if (restored) {
        setSessionsLoaded(true);
        console.log('Chat sessions restored from persisted state');
      }
    }
  }, [sessionsLoaded, isAuthenticated, initializeFromPersistedState]);

  // Restore draft message when session changes
  useEffect(() => {
    if (sessionId) {
      const savedDraft = getSavedDraftMessage();
      if (savedDraft && savedDraft !== input) {
        setInput(savedDraft);
      }
    }
  }, [sessionId, getSavedDraftMessage]);

  // Save draft message as user types
  useEffect(() => {
    if (sessionId && input) {
      updateDraftMessage(input);
    }
  }, [sessionId, input, updateDraftMessage]);
  
  // Auto-scroll to bottom when messages change or restore saved scroll position
  useEffect(() => {
    if (messagesEndRef.current) {
      // Check if we have a saved scroll position
      const savedPosition = getSavedScrollPosition();
      
      if (savedPosition !== null) {
        // Use setTimeout to ensure the DOM is fully rendered
        setTimeout(() => {
          const chatContainer = messagesEndRef.current?.parentElement;
          if (chatContainer) {
            chatContainer.scrollTop = savedPosition;
          }
        }, 100);
      } else {
        // Default to scrolling to bottom
        messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
      }
    }
  }, [messages, sessionId, getSavedScrollPosition]);
  
  // Save scroll position when user scrolls
  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    if (sessionId) {
      syncScrollPosition(e.currentTarget.scrollTop);
    }
  }, [sessionId, syncScrollPosition]);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isMountedRef.current = false;
    };
  }, []);
  
  // Load sessions from backend when authenticated
  useEffect(() => {
    const loadSessions = async () => {
      if (!isAuthenticated || !token) {
        // Clear sessions when not authenticated
        setSessions([]);
        setSessionId(null);
        setMessages([]);
        setSessionsLoaded(false); // Reset sessions loaded flag
        
        // Clean up localStorage when logging out
        try {
          const activeSessionIds = JSON.parse(localStorage.getItem('activeSessionIds') || '[]');
          // Clean up each session data
          activeSessionIds.forEach((sid: string) => {
            localStorage.removeItem(`messages_${sid}`);
          });
          // Remove tracking keys
          localStorage.removeItem('activeSessionIds');
          localStorage.removeItem('activeSessionId');
        } catch (e) {
          console.error('Error cleaning up localStorage on logout:', e);
        }
        
        return;
      }
      
      try {
        const { data, success } = await api.get(API_ENDPOINTS.CHAT.SESSIONS);
        
        if (success && data && Array.isArray(data)) {
          console.log('Loaded sessions:', data);
          // Map incoming sessions to our structure
          const formattedSessions = data.map((s: any) => {
            // Find a meaningful name for the session
            let sessionName = s.topic || s.name;
            if (!sessionName || sessionName === 'New Chat' || sessionName === 'New Conversation') {
              // If no meaningful name, try to extract from first message if available
              if (s.preview_message) {
                sessionName = generateSimpleTopicFromMessage(s.preview_message);
              } else if (s.messages && Array.isArray(s.messages) && s.messages.length > 0) {
                // Try to use first message in the array if available
                const firstMsg = s.messages[0];
                const msgText = firstMsg.text || firstMsg.user || firstMsg.message;
                sessionName = generateSimpleTopicFromMessage(msgText);
              } else {
                // Fallback to date-based name
                sessionName = `Conversation ${new Date(s.lastActivity || s.created || new Date()).toLocaleDateString()}`;
              }
            }
            
            return {
              id: s.session_id || s.id,
              name: sessionName,
              lastActivity: s.lastActivity || s.last_activity || new Date().toISOString(),
              messages: [],
              session_id: s.session_id || s.id,
              topic: sessionName
            };
          });
          
          // Sort by last activity, most recent first
          const sortedSessions = formattedSessions.sort((a, b) => 
            new Date(b.lastActivity).getTime() - new Date(a.lastActivity).getTime()
          );
          
          setSessions(sortedSessions);
          
          // Try to restore last active session from localStorage
          const savedSessionId = localStorage.getItem('activeSessionId');
          const sessionExists = sortedSessions.some(s => 
            s.session_id === savedSessionId || s.id === savedSessionId
          );
          
          if (savedSessionId && sessionExists) {
            // Restore previous session
            setSessionId(savedSessionId);
            
            // Try to restore messages from localStorage first for instant display
            try {
              const savedMessages = localStorage.getItem(`messages_${savedSessionId}`);
              if (savedMessages) {
                try {
                  const parsedMessages = JSON.parse(savedMessages);
                  console.log(`Restored ${parsedMessages.length} messages for session ${savedSessionId} from localStorage`);
                  setMessages(parsedMessages);
                  // Mark these messages as from cache, so backend fetch won't replace them if they're identical
                  setMessagesFromCache(true);
                  
                  // Ensure the active session ID is saved in localStorage
                  localStorage.setItem('activeSessionId', savedSessionId);
                } catch (parseError) {
                  console.error('Failed to parse saved messages:', parseError);
                  // If parsing fails, we'll rely solely on backend data
                }
              }
            } catch (e) {
              console.error('Failed to access localStorage:', e);
            }
            
            // Still load messages from backend for latest updates
            loadSessionMessages(savedSessionId);
          } else if (sortedSessions.length > 0) {
            // Select first session if available
            setSessionId(sortedSessions[0].session_id || sortedSessions[0].id);
            // Load messages for this session
            loadSessionMessages(sortedSessions[0].session_id || sortedSessions[0].id);
          } else {
            // If no sessions, create a default session
            await createNewSession();
          }
        } else {
          // If no sessions or error, create a default session
          await createNewSession();
        }
      } catch (err) {
        console.error('Failed to load sessions:', err);
        setError('Failed to load chat sessions');
        // If error loading sessions, create a default one
        await createNewSession();
      }
    };
    
    loadSessions();
  }, [isAuthenticated, token]); // Re-run when auth state changes

  // Track if messages were loaded from cache to handle merging with backend data
  const [messagesFromCache, setMessagesFromCache] = useState<boolean>(false);

  // Function to load messages for a session (memoized with useCallback)
  const loadSessionMessages = useCallback(async (sid: string) => {
    if (!sid || !isAuthenticated) return;
    
    // Check if we have cached messages first
    const cachedMessages = loadMessagesFromCache(sid);
    const hasExistingMessages = cachedMessages.length > 0;
    
    // If we have cached messages, use them immediately
    if (hasExistingMessages) {
      console.log('Using cached messages while backend loads for session:', sid);
      // Only set messages if they're different from current messages to avoid unnecessary renders
      if (JSON.stringify(cachedMessages) !== JSON.stringify(messages)) {
        setMessages(cachedMessages);
        // Mark these messages as from cache, so backend fetch won't replace them if they're identical
        setMessagesFromCache(true);
        // Ensure the active session is saved in localStorage
        localStorage.setItem('activeSessionId', sid);
      }
    }
    
    try {
      setError('');
      // Get the auth token to ensure we're using the current one
      const currentToken = getAuthToken();
      if (!currentToken) {
        console.error('No auth token available');
        return;
      }
      
      const { data, success } = await api.get(API_ENDPOINTS.CHAT.HISTORY(sid));
      
      if (success && data && Array.isArray(data)) {
        // Convert messages to our expected format
        const formattedMessages = data.map((msg: any) => {
          // Handle different possible message formats
          if (msg.user) {
            return { sender: 'user' as const, text: msg.user, timestamp: msg.timestamp };
          } else if (msg.bot) {
            return { sender: 'grace' as const, text: msg.bot, timestamp: msg.timestamp };
          } else {
            return msg; // Already in our format
          }
        });
        
        // If backend returned messages
        if (formattedMessages.length > 0) {
          // If we have cached messages, we need to handle merging carefully
          if (hasExistingMessages) {
            // If backend has more messages than cache, use backend data
            if (formattedMessages.length > cachedMessages.length) {
              console.log('Backend has more messages than cache, updating');
              setMessages(formattedMessages);
              persistMessages(sid, formattedMessages);
            } else {
              // Check for any local messages that might not have synced yet
              const lastServerMessageTime = formattedMessages.length > 0 ? 
                new Date(formattedMessages[formattedMessages.length - 1].timestamp).getTime() : 0;
              
              // Keep local messages sent after the last server message
              const localNewMessages = cachedMessages.filter(m => 
                new Date(m.timestamp || Date.now()).getTime() > lastServerMessageTime
              );
              
              // Combine server messages with any newer local ones
              if (localNewMessages.length > 0) {
                console.log('Merging backend messages with local messages');
                const mergedMessages = [...formattedMessages, ...localNewMessages];
                setMessages(mergedMessages);
                persistMessages(sid, mergedMessages);
              } else if (JSON.stringify(formattedMessages) !== JSON.stringify(cachedMessages)) {
                // Only update if different to avoid unnecessary renders
                setMessages(formattedMessages);
                persistMessages(sid, formattedMessages);
              }
            }
          } else {
            // No cache, use backend data
            console.log('Setting messages from backend, no cache available');
            setMessages(formattedMessages);
            persistMessages(sid, formattedMessages);
          }
        } else if (!hasExistingMessages) {
          // Backend returned empty and we have no cache
          setMessages([]);
        }
      }
    } catch (err) {
      console.error(`Failed to load messages for session ${sid}:`, err);
      // If we have cached messages, keep using them on error
      if (!hasExistingMessages) {
        setMessages([]);
      }
    }
  }, [isAuthenticated]);

  // Load messages when session ID changes
  useEffect(() => {
    // If any required condition is missing, return early
    if (!sessionId || !isAuthenticated || !sessionsLoaded) return;
    
    console.log('Session ID changed, loading messages for:', sessionId);
    
    // Store current session ID in localStorage to persist across page navigations
    localStorage.setItem('activeSessionId', sessionId);
    
    // Load from backend (our updated function now handles cache properly)
    loadSessionMessages(sessionId);
  }, [sessionId, loadSessionMessages, isAuthenticated, sessionsLoaded]);

  // On component mount, try to restore the last active session from localStorage
  useEffect(() => {
    // If not authenticated or sessions not loaded yet, return early
    if (!isAuthenticated || !sessionsLoaded) return;
    
    console.log('Attempting to restore previous session');
    
    // Sort sessions by last activity
    const sortedSessions = [...sessions].sort((a, b) => {
      return new Date(b.lastActivity).getTime() - new Date(a.lastActivity).getTime();
    });
    setSessions(sortedSessions);
    
    // Try to restore previous session if available
    const savedSessionId = localStorage.getItem('activeSessionId');
    
    if (savedSessionId && sortedSessions.some(s => (s.session_id || s.id) === savedSessionId)) {
      console.log('Found previous session in loaded sessions:', savedSessionId);
      
      // Set the session ID - this will trigger the useEffect that loads messages
      setSessionId(savedSessionId);
    } else if (sortedSessions.length > 0) {
      // If no saved session but we have sessions, automatically select the most recent one
      console.log('No saved session found, selecting most recent session');
      setSessionId(sortedSessions[0].session_id || sortedSessions[0].id);
    }
  }, [isAuthenticated, sessionsLoaded, sessions]);

  // Scroll to bottom whenever messages change
  useEffect(() => {
    // Scroll to bottom of messages
    if (messagesEndRef.current) {
      // Use a small timeout to ensure the DOM has updated
      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    }
    
    // Store messages in localStorage using our helper function
    if (sessionId && messages.length > 0) {
      persistMessages(sessionId, messages);
    }
  }, [messages, sessionId]);

  // Refresh sessions list from backend (memoized with useCallback)
  const refreshSessions = useCallback(async () => {
    if (!isAuthenticated) return;
    
    try {
      const { data, success } = await api.get(API_ENDPOINTS.CHAT.SESSIONS);
      
      if (success && Array.isArray(data)) {
        // Sort sessions by lastActivity, newest first
        const sortedSessions = [...data].sort((a, b) => {
          return new Date(b.lastActivity).getTime() - new Date(a.lastActivity).getTime();
        });
        
        setSessions(sortedSessions);
      }
    } catch (err) {
      console.error('Failed to refresh sessions:', err);
    }
  }, [isAuthenticated]);

  // Create a new session with backend (memoized with useCallback)
  const createNewSession = useCallback(async () => {
    if (!isAuthenticated) return;
    
    try {
      setError('');
      const { data, success } = await api.post(API_ENDPOINTS.CHAT.NEW_SESSION, {});
      
      if (success && data) {
        const newSession = {
          id: data.session_id,
          name: data.name || 'New Conversation',  // Better default name
          lastActivity: data.lastActivity || new Date().toISOString(),
          messages: [],
          session_id: data.session_id,
          topic: data.topic || 'New Conversation'  // Better default topic
        };
        
        // Add to existing sessions
        setSessions(prev => [newSession, ...prev]);
        
        // Clear messages first
        setMessages([]);
        
        // Set the session ID
        setSessionId(newSession.session_id);
        
        // Initialize empty cache for this session
        persistMessages(newSession.session_id, []);
        
        // Store the session ID in localStorage to maintain across page navigations
        localStorage.setItem('activeSessionId', newSession.session_id);
        
        // Mark this session as loaded from cache to prevent overwriting
        setMessagesFromCache(true);
        
        return newSession.session_id;
      } else {
        throw new Error('Failed to create session');
      }
    } catch (err) {
      console.error('Failed to create new session:', err);
      setError('Failed to create new chat session');
      
      // Create locally if backend fails
      // Use random component for more uniqueness
      const fallbackId = `session-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
      const fallbackSession = {
        id: fallbackId,
        name: 'New Conversation',  // Better default name
        lastActivity: new Date().toISOString(),
        messages: [],
        session_id: fallbackId,
        topic: 'New Conversation'  // Better default topic
      };
      
      setSessions(prev => [fallbackSession, ...prev]);
      
      // Clear messages first
      setMessages([]);
      
      // Set the session ID
      setSessionId(fallbackId);
      
      // Initialize empty cache for this session
      persistMessages(fallbackId, []);
      
      // Store even fallback session ID
      localStorage.setItem('activeSessionId', fallbackId);
      
      // Mark this session as loaded from cache to prevent overwriting
      setMessagesFromCache(true);
      
      return fallbackId;
    }
  }, [isAuthenticated]);


  
  // Send chat message with session ID
  const sendMessage = async () => {
    if (!input.trim() || !isAuthenticated || !sessionId) return;
    
    // Create a temp message object to show immediately
    const tempUserMessage: ChatMessage = {
      sender: 'user',
      text: input,
      timestamp: new Date().toISOString()
    };
    
    // Create updated messages array with the new message
    const updatedMessages = [...messages, tempUserMessage];
    
    // Persist messages to localStorage immediately - do this BEFORE state update
    // to avoid potential race conditions
    persistMessages(sessionId, updatedMessages);
    
    // Ensure the active session ID is saved in localStorage
    localStorage.setItem('activeSessionId', sessionId);
    
    // Add to UI immediately
    setMessages(updatedMessages);
    
    // Generate preliminary topic from first message if needed
    const currentSession = sessions.find(s => s.session_id === sessionId || s.id === sessionId);
    const isGenericTopic = currentSession && (
      !currentSession.topic || 
      currentSession.topic === 'New Conversation' || 
      currentSession.topic.startsWith('Chat ') ||
      currentSession.topic.startsWith('Conversation ')
    );
    
    if (messages.length === 0 && isGenericTopic && input) {
      try {
        // This is the first message, use it to create a preliminary topic
        const prelimTopic = generateSimpleTopicFromMessage(input);
        // Update session with a meaningful name based on first message
        const updatedSessions = sessions.map(s => 
          (s.session_id === sessionId || s.id === sessionId) 
            ? { ...s, topic: prelimTopic, name: prelimTopic } 
            : s
        );
        setSessions(updatedSessions);
      } catch (e) {
        console.error('Error updating session topic:', e);
      }
    }
    
    // Clear input field
    setInput('');
    
    // Set loading state
    setLoading(true);
    
    try {
      // Send message to API
      const { data, success } = await api.post(API_ENDPOINTS.CHAT.MESSAGE, {
        session_id: sessionId,
        message: input
      });
      
      if (success && data) {
        // Format the response to match our message structure
        const botResponse: ChatMessage = {
          sender: 'grace',
          text: data.response || '',
          timestamp: new Date().toISOString()
        };
        
        // Create final messages array with both user message and bot response
        const finalMessages = [...updatedMessages, botResponse];
        
        // Persist the complete conversation including bot response - do this BEFORE state update
        // to avoid potential race conditions
        persistMessages(sessionId, finalMessages);
        
        // Ensure the active session ID is saved in localStorage
        localStorage.setItem('activeSessionId', sessionId);
        
        // Add to messages
        setMessages(finalMessages);
        
        // Re-sync with server to ensure we have the latest data
        loadSessionMessages(sessionId);
        
        // Update session if the server provides a topic
        if (data.topic) {
          try {
            // Replace our preliminary topic with server-generated one
            const updatedSessions = sessions.map(s => 
              (s.session_id === sessionId || s.id === sessionId) 
                ? { ...s, topic: data.topic, name: data.topic } 
                : s
            );
            setSessions(updatedSessions);
          } catch (e) {
            console.error('Error updating session with server topic:', e);
          }
        }
      } else {
        setError('Failed to get response');
      }
    } catch (err) {
      console.error('Failed to send message:', err);
      setError('Failed to send message');
      
      // Even if there's an error, we should still show the user's message
      // This ensures the user can see their message even if Grace doesn't respond
      // Persist messages to localStorage first to avoid race conditions
      persistMessages(sessionId, updatedMessages);
      localStorage.setItem('activeSessionId', sessionId);
      setMessages(updatedMessages);
    } finally {
      setLoading(false);
      
      // Ensure we scroll to the latest message with a small delay to ensure DOM update
      setTimeout(() => {
        if (messagesEndRef.current) {
          messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
      }, 100);
    }
  };

  // State for mobile sidebar visibility
  const [sidebarVisible, setSidebarVisible] = useState(false);

  // ... (rest of the code remains the same)
  // Toggle sidebar on mobile
  const toggleSidebar = () => {
    setSidebarVisible(!sidebarVisible);
  };
  
  // Simple function to rename a chat session
  const handleSessionRename = (sessionId: string) => {
    try {
      // Find the session to rename
      const session = sessions.find(s => s.session_id === sessionId || s.id === sessionId);
      if (!session) return;
      
      // Get current name to show as default
      const currentName = session.topic || session.name || `Chat ${sessionId.slice(0, 6)}`;
      
      // Prompt for new name
      const newName = prompt('Enter a new name for this chat:', currentName);
      
      // Update if name provided
      if (newName && newName.trim() && newName !== currentName) {
        // Update locally
        const updatedSessions = sessions.map(s => 
          (s.session_id === sessionId || s.id === sessionId) 
            ? { ...s, topic: newName.trim(), name: newName.trim() } 
            : s
        );
        setSessions(updatedSessions);
        
        // Note: In a full implementation, you would also update the server
        // But for this minimal improvement, we're just updating the UI
      }
    } catch (e) {
      console.error('Error renaming session:', e);
    }
  };

  return (
    <div className="flex h-[calc(100vh-16rem)] overflow-hidden rounded-lg border border-red-700">
        {/* Mobile sidebar toggle button */}
        <button 
          className="md:hidden absolute top-2 left-2 z-10 bg-red-800 rounded-full p-2 text-white shadow-md"
          onClick={toggleSidebar}
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M3 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
          </svg>
        </button>
        
        {/* Sidebar - responsive with md: breakpoint */}
        <aside className={`${sidebarVisible ? 'block' : 'hidden'} md:block absolute md:relative md:w-64 w-3/4 bg-black border-r border-red-800 p-4 overflow-y-auto h-full z-10`}>
          <h2 className="text-red-300 text-lg font-mono mb-2 flex justify-between items-center">
            <span>Sessions</span>
            <button onClick={toggleSidebar} className="md:hidden text-red-300 hover:text-red-100">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </h2>
          <button
            onClick={() => {
              createNewSession();
              setSidebarVisible(false);
            }}
            className="w-full mb-4 rounded bg-red-700 px-4 py-2 hover:bg-red-900"
            disabled={!isAuthenticated || loading}
          >
            + New Chat
          </button>
          
          {error && <p className="text-red-500 text-xs mb-2">{error}</p>}
          
          {!isAuthenticated && (
            <p className="text-yellow-500 text-xs mb-2">Please log in to use chat</p>
          )}
          <ul className="space-y-2">
            {sessions.map((s) => (
              <li key={s.session_id} className="relative group">
                <button
                onClick={() => {
                  // Clear current messages first to avoid UI flashing
                  setMessages([]);
                  // Set the session ID
                  setSessionId(s.session_id);
                  // Immediately load messages from cache
                  const cachedMessages = loadMessagesFromCache(s.session_id);
                  if (cachedMessages.length > 0) {
                    setMessages(cachedMessages);
                  }
                  // Store the active session ID
                  localStorage.setItem('activeSessionId', s.session_id);
                  // Close sidebar on mobile after selection
                  setSidebarVisible(false);
                }}
                className={`w-full text-left px-3 py-2 rounded text-sm hover:bg-red-800 ${sessionId === s.session_id ? 'bg-red-900 text-white' : 'text-red-300'}`}
              >
                  {/* Display the topic/name or generate one from message content */}
                  {s.topic || s.name || `Chat ${s.session_id.slice(0, 6)}`}
                </button>

              </li>
            ))}
          </ul>
        </aside>

        {/* Chat Window */}
        {/* Overlay to close sidebar on mobile when clicked outside */}
        {sidebarVisible && (
          <div 
            className="md:hidden fixed inset-0 bg-black bg-opacity-50 z-0"
            onClick={() => setSidebarVisible(false)}
          />
        )}
        
        <main className="flex-1 bg-black flex flex-col">
          <div 
            className="flex-1 overflow-y-auto p-6 space-y-4" 
            onScroll={handleScroll}
          >
            {messages.length === 0 && !loading && (
              <div className="text-center text-gray-500 my-8">
                {isAuthenticated ? 'No messages yet. Start a conversation!' : 'Please log in to start chatting'}
              </div>
            )}
            
            {/* Show loading indicator when waiting for Grace's response */}
            {loading && (
              <div className="text-center text-yellow-500 my-4 animate-pulse">
                Grace is thinking...
              </div>
            )}
            
            {messages.map((msg, idx) => (
              <div key={idx} className="mb-4">
                {msg.sender === 'user' || msg.user ? (
                  <div className="text-right p-2 rounded-lg bg-red-900/30 text-red-300">
                    <span className="font-bold">You:</span> {msg.text || msg.user}
                  </div>
                ) : null}
                
                {msg.sender === 'grace' || msg.bot ? (
                  <div className="text-left p-2 rounded-lg bg-green-900/30 text-green-300">
                    <span className="font-bold">Grace:</span> {msg.text || msg.bot}
                  </div>
                ) : null}
              </div>
            ))}
            
            {/* This empty div is used as a reference for scrolling to the bottom */}
            <div ref={messagesEndRef} />
          </div>

          <footer className="flex border-t border-red-800 bg-black p-4">
            <textarea
              className="flex-1 mr-2 rounded bg-white/10 p-2 text-white min-h-[60px] resize-none"
              placeholder={isAuthenticated ? "Type your message... (Shift+Enter for new line)" : "Please log in to chat"}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault(); // Prevent default to avoid new line
                  if (!loading && isAuthenticated && input.trim()) {
                    sendMessage();
                  }
                }
              }}
              disabled={!isAuthenticated || loading}
              autoFocus
              aria-label="Chat message input"
              ref={(el) => {
                // Focus when session changes
                if (el && isAuthenticated && !loading) {
                  setTimeout(() => el.focus(), 100); // Small delay to ensure it works across browsers
                }
              }}
            />
            <button
              onClick={sendMessage}
              disabled={loading || !isAuthenticated || !input.trim()}
              className="rounded bg-red-700 px-4 py-2 hover:bg-red-900 disabled:bg-gray-700 disabled:cursor-not-allowed"
            >
              {loading ? '...' : 'Send'}
            </button>
          </footer>
          
          {/* XFeed Section */}
          <div className="border-t border-red-800/50 p-4 bg-black/70">
            <div className="bg-transparent text-white p-4">
              <div className="flex justify-between items-center mb-2">
                <h3 className="flex items-center text-red-500 font-bold relative pl-4 before:content-[''] before:absolute before:left-0 before:top-0 before:h-full before:w-1 before:bg-red-500">
                  XFeed Channel
                </h3>
                {/* Direct Add Account Button */}
                <button 
                  onClick={() => {
                    // Find and click the settings button in XFeed
                    const settingsBtn = document.querySelector('[data-xfeed-settings]');
                    if (settingsBtn && settingsBtn instanceof HTMLElement) {
                      settingsBtn.click();
                    }
                  }}
                  className="text-xs px-2 py-1 rounded bg-red-900/50 text-red-200 hover:bg-red-800 flex items-center space-x-1"
                >
                  <span className="text-lg leading-none">+</span>
                  <span>Add Account</span>
                </button>
              </div>
              <hr className="border-gray-800 mb-4" />
              <XFeed maxItems={3} /> {/* Limit to 3 items to keep it compact */}
            </div>
          </div>
        </main>
      </div>
  );
}
