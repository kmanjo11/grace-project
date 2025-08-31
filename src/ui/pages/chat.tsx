// src/pages/Chat.tsx

import React, { useEffect, useState, useRef, useCallback, useLayoutEffect } from 'react';
import { useAuth } from '../components/AuthContext';
import { useChatStatePersistence } from '../components/ChatStatePersistence';
import XFeed from '../components/XFeed';
import { useConversations } from '../hooks/useConversations';
import { useMessages } from '../hooks/useMessages';

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
  const { isAuthenticated, user } = useAuth();
  const PERSIST_DISABLED = (process.env.NEXT_PUBLIC_DISABLE_STATE_PERSIST || '').toString() === '1' || (process.env.NEXT_PUBLIC_DISABLE_STATE_PERSIST || '').toString().toLowerCase() === 'true';
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState<string>('');
  const [error, setError] = useState<string>('');
  
  // React Query hooks
  const { sessions: qSessions, create, rename, isLoading: sessionsLoading } = useConversations();
  const { messages: qMessages, isSending, send, isFetching } = useMessages(sessionId);
  
  // Track if sessions have been loaded
  const [sessionsLoaded, setSessionsLoaded] = useState<boolean>(false);
  // Use ref to avoid duplicate session creation
  const messagesEndRef = useRef<HTMLDivElement>(null);
  // Scroll management refs
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const lastKnownScrollTopRef = useRef<number>(0);
  const isUserScrollingRef = useRef<boolean>(false);
  const scrollSaveTimerRef = useRef<number | null>(null);
  const restoredScrollForSessionRef = useRef<Record<string, boolean>>({});
  const suppressAutoScrollUntilRef = useRef<number>(0);
  const justMountedRef = useRef<boolean>(true);
  const [isAtBottom, setIsAtBottom] = useState<boolean>(false);

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
    if (!sid || !msgs || msgs.length === 0) return; // avoid persisting empty arrays
    try {
      // Only store a limited number of messages to prevent localStorage overflows
      const messagesToStore = msgs.slice(-50); // Store just the last 50 messages
      if (!PERSIST_DISABLED) {
        localStorage.setItem(`messages_${sid}`, JSON.stringify(messagesToStore));
      }
      
      // Store a timestamp with the messages to track freshness
      if (!PERSIST_DISABLED) {
        localStorage.setItem(`lastSynced_${sid}`, new Date().toISOString());
      }
      
      // Always store the active session ID to ensure it's available when returning to the page
      if (!PERSIST_DISABLED) {
        localStorage.setItem('activeSessionId', sid);
      }
    } catch (e) {
      console.error('Failed to store messages in localStorage:', e);
    }
  };
  
  // Helper function to load messages from cache
  const loadMessagesFromCache = (sid: string): ChatMessage[] => {
    if (!sid) return [];
    try {
      const savedMessages = PERSIST_DISABLED ? null : (typeof window !== 'undefined' ? localStorage.getItem(`messages_${sid}`) : null);
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
  // Guard to ensure we only attempt session restoration once per mount
  const restoredOnceRef = useRef(false);
  // Dedup guard for history loads per session
  const lastHistoryLoadRef = useRef<Record<string, number>>({});
  
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
  
  // Helper: check if container is near bottom (so it's safe to auto-scroll)
  const isNearBottom = useCallback((container: HTMLElement | null, threshold = 80) => {
    if (!container) return false;
    const distanceFromBottom = container.scrollHeight - container.scrollTop - container.clientHeight;
    return distanceFromBottom <= threshold;
  }, []);

  // Restore saved scroll position only once per session change (layout-safe)
  useLayoutEffect(() => {
    if (!sessionId) return;
    if (restoredScrollForSessionRef.current[sessionId]) return;

    const savedPosition = getSavedScrollPosition();
    if (savedPosition !== null) {
      setTimeout(() => {
        const container = scrollContainerRef.current;
        if (container && typeof savedPosition === 'number' && !isNaN(savedPosition)) {
          // Immediate jump (no smooth) for initial restore
          container.scrollTop = savedPosition;
          lastKnownScrollTopRef.current = savedPosition;
        }
      }, 100);
    }

    restoredScrollForSessionRef.current[sessionId] = true;
    // After first paint, initial mount no longer special
    setTimeout(() => { justMountedRef.current = false; }, 200);
  }, [sessionId, getSavedScrollPosition]);
  
  // Save scroll position when user scrolls
  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    const top = e.currentTarget.scrollTop;
    lastKnownScrollTopRef.current = top;
    isUserScrollingRef.current = true;
    // Suppress programmatic auto-scroll for a cooldown window after user scroll
    suppressAutoScrollUntilRef.current = Date.now() + 900;
    if (!sessionId) return;
    // Debounce syncing scroll position to reduce rerenders
    if (scrollSaveTimerRef.current) {
      window.clearTimeout(scrollSaveTimerRef.current);
      scrollSaveTimerRef.current = null;
    }
    scrollSaveTimerRef.current = window.setTimeout(() => {
      syncScrollPosition(top);
      isUserScrollingRef.current = false;
    }, 150);
  }, [sessionId, syncScrollPosition]);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  // Sync React Query sessions into local state once, then use local selection logic
  useEffect(() => {
    if (!isAuthenticated) {
      setSessions([]);
      setSessionId(null);
      return;
    }
    if (!qSessions) return;
    // Normalize to ChatSession shape expected by current UI
    const normalized = qSessions.map((s: any) => ({
      id: s.session_id || s.id,
      session_id: s.session_id || s.id,
      name: s.name || s.topic || 'New Conversation',
      topic: s.topic || s.name || 'New Conversation',
      lastActivity: s.lastActivity || new Date().toISOString(),
      messages: [],
    })) as ChatSession[];
    setSessions(normalized);
    if (!sessionId && normalized.length > 0) {
      const saved = PERSIST_DISABLED ? null : (typeof window !== 'undefined' ? localStorage.getItem('activeSessionId') : null);
      const found = normalized.find(s => (s.session_id || s.id) === saved);
      setSessionId(found ? (found.session_id || found.id) : (normalized[0].session_id || normalized[0].id));
    }
    setSessionsLoaded(true);
  }, [qSessions, isAuthenticated]);

  // Track if messages were loaded from cache to handle merging with backend data
  const [messagesFromCache, setMessagesFromCache] = useState<boolean>(false);

  // Sync React Query messages into local UI when they change
  useEffect(() => {
    if (!sessionId) return;
    if (Array.isArray(qMessages)) {
      setMessages(qMessages as unknown as ChatMessage[]);
    }
  }, [qMessages, sessionId]);

  // When session changes, persist active id and show cached messages immediately (fast UX)
  useEffect(() => {
    if (!sessionId) return;
    if (!PERSIST_DISABLED) {
      localStorage.setItem('activeSessionId', sessionId);
    }
    const cached = loadMessagesFromCache(sessionId);
    if (cached.length) setMessages(cached);
  }, [sessionId]);

  // FIXED: Stabilized session restoration effect
  useEffect(() => {
    // If not authenticated or sessions not loaded yet, or already restored, return early
    if (!isAuthenticated || !sessionsLoaded || restoredOnceRef.current || sessions.length === 0) return;

    console.log('Attempting to restore previous session');

    // Try to restore previous session if available
    const savedSessionId = PERSIST_DISABLED ? null : (typeof window !== 'undefined' ? localStorage.getItem('activeSessionId') : null);
    const sessionExists = sessions.some(s => (s.session_id || s.id) === savedSessionId);

    if (savedSessionId && sessionExists) {
      console.log('Found previous session in loaded sessions:', savedSessionId);
      setSessionId(savedSessionId);
    } else if (sessions.length > 0) {
      console.log('No saved session found, selecting most recent session');
      // Sort by lastActivity and select the most recent
      const mostRecent = sessions.reduce((latest, current) => {
        return new Date(current.lastActivity) > new Date(latest.lastActivity) ? current : latest;
      });
      setSessionId(mostRecent.session_id || mostRecent.id);
    }

    // Mark restoration as done to prevent repeating
    restoredOnceRef.current = true;
  }, [isAuthenticated, sessionsLoaded, sessions.length]); // Only depend on length, not full sessions array

  // Observe if the bottom sentinel is visible within the scroll container (isAtBottom)
  useEffect(() => {
    const container = scrollContainerRef.current;
    const target = messagesEndRef.current;
    if (!container || !target) return;
    const io = new IntersectionObserver(
      ([entry]) => setIsAtBottom(entry.isIntersecting),
      { root: container, threshold: 0.99, rootMargin: '0px 0px -1px 0px' }
    );
    io.observe(target);
    return () => io.disconnect();
  }, []);

  // FIXED: Stabilized scroll effect using isAtBottom and fetch-settled gating
  useEffect(() => {
    const now = Date.now();
    if (now < suppressAutoScrollUntilRef.current) return;
    if (isFetching) return; // wait until data settles
    if (!isAtBottom) return; // only follow to bottom if already at bottom
    const container = scrollContainerRef.current;
    if (container) {
      setTimeout(() => {
        // Use smooth only after initial mount
        const behavior: ScrollBehavior = justMountedRef.current ? 'auto' : 'smooth';
        messagesEndRef.current?.scrollIntoView({ behavior });
      }, 100);
    }

    // Store messages in localStorage using our helper function (only if we have messages)
    if (sessionId && messages.length > 0) {
      persistMessages(sessionId, messages);
    }
  }, [messages.length, sessionId, persistMessages, isFetching, isAtBottom]);

  // React Query manages refresh; remove manual refreshSessions

  // Create a new session using hook
  const createNewSession = useCallback(async () => {
    if (!isAuthenticated) return;
    try {
      setError('');
      const result = await create('New Conversation');
      const newId = typeof result === 'string' 
        ? result 
        : (result?.session_id || result?.id);
      if (newId) {
        setSessionId(newId);
        if (!PERSIST_DISABLED) {
          localStorage.setItem('activeSessionId', newId);
        }
        setMessages([]);
        return newId;
      }
    } catch (err) {
      console.error('Failed to create new session:', err);
      setError('Failed to create new chat session');
    }
  }, [isAuthenticated, create]);


  
  // Send chat message with session ID
  const sendMessage = async () => {
    if (!input.trim() || !isAuthenticated || !sessionId) return;
    // Ensure the active session ID is saved in localStorage
    if (!PERSIST_DISABLED) {
      localStorage.setItem('activeSessionId', sessionId);
    }
    
    // Snapshot message then clear input for responsive UX
    const messageToSend = input;
    setInput('');
    
    // Preliminary topic from first message if needed
    const currentSession = sessions.find(s => s.session_id === sessionId || s.id === sessionId);
    const isGenericTopic = currentSession && (
      !currentSession.topic || 
      currentSession.topic === 'New Conversation' || 
      currentSession.topic.startsWith('Chat ') ||
      currentSession.topic.startsWith('Conversation ')
    );
    if (messages.length === 0 && isGenericTopic && messageToSend) {
      const prelimTopic = generateSimpleTopicFromMessage(messageToSend);
      try { await rename(sessionId, prelimTopic); } catch (e) { console.warn('Prelim rename failed:', e); }
    }

    try {
      console.log('[Chat] sendMessage()', { sessionId, length: messageToSend.length });
      await send(messageToSend);
    } catch (e) {
      console.error('Failed to send message:', e);
      setError('Failed to send message');
      // Restore draft on error
      setInput(messageToSend);
    }
  };

  // State for mobile sidebar visibility
  const [sidebarVisible, setSidebarVisible] = useState(false);
  const [showXFeed, setShowXFeed] = useState(false);

  // Defer XFeed mount slightly to avoid contributing to initial layout shift
  useEffect(() => {
    const t = setTimeout(() => setShowXFeed(true), 800);
    return () => clearTimeout(t);
  }, []);

  // Ensure browser doesn't fight our scroll restore on refresh/navigation
  useEffect(() => {
    if (typeof window !== 'undefined' && 'scrollRestoration' in window.history) {
      try { (window.history as any).scrollRestoration = 'manual'; } catch {}
    }
  }, []);

  // ... (rest of the code remains the same)
  // Toggle sidebar on mobile
  const toggleSidebar = () => {
    setSidebarVisible(!sidebarVisible);
  };
  
  // Simple function to rename a chat session
  const handleSessionRename = async (sessionId: string) => {
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
        // Update server via hook
        try { await rename(sessionId, newName.trim()); } catch (e) { console.warn('Rename failed:', e); }
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
            disabled={!isAuthenticated || sessionsLoading}
          >
            + New Chat
          </button>
          
          {error && <p className="text-red-500 text-xs mb-2">{error}</p>}
          
          {!isAuthenticated && (
            <p className="text-yellow-500 text-xs mb-2">Please log in to use chat</p>
          )}
          <ul className="space-y-2">
            {sessions.map((s) => {
              // Safely get the session ID, checking both session_id and id
              const currentSessionId = s.session_id || s.id;
              if (!currentSessionId) return null; // Skip if no valid ID
              
              return (
                <li key={currentSessionId} className="relative group">
                  <button
                    onClick={() => {
                      // Clear current messages first to avoid UI flashing
                      setMessages([]);
                      // Set the session ID
                      setSessionId(currentSessionId);
                      // Immediately load messages from cache
                      const cachedMessages = loadMessagesFromCache(currentSessionId);
                      if (cachedMessages.length > 0) {
                        setMessages(cachedMessages);
                      }
                      // Store the active session ID (only if persistence enabled)
                      if (!PERSIST_DISABLED) {
                        localStorage.setItem('activeSessionId', currentSessionId);
                      }
                      // Close sidebar on mobile after selection
                      setSidebarVisible(false);
                    }}
                    className={`w-full text-left px-3 py-2 rounded text-sm hover:bg-red-800 ${sessionId === currentSessionId ? 'bg-red-900 text-white' : 'text-red-300'}`}
                  >
                    {/* Display the topic/name or generate one from message content */}
                    {s.topic || s.name || `Chat ${currentSessionId.slice(0, 6)}`}
                  </button>
                </li>
              );
            })}
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
          {/* Active session indicator for debugging */}
          <div className="flex items-center justify-between border-b border-red-800/60 px-4 py-2 text-xs text-red-300/80">
            <div>
              <span className="mr-2">Active session:</span>
              <code className="bg-red-900/30 px-2 py-0.5 rounded">{(user && (user.displayName || user.username)) ? (user.displayName || user.username) : (sessionId || 'none')}</code>
            </div>
            {PERSIST_DISABLED ? (
              <span className="text-yellow-400">persistence: off</span>
            ) : (
              <span className="text-green-400">persistence: on</span>
            )}
          </div>
          <div 
            className="flex-1 overflow-y-auto p-6 space-y-4" 
            onScroll={handleScroll}
            ref={scrollContainerRef}
            style={{ overscrollBehavior: 'contain', overflowAnchor: 'none' as any, scrollbarGutter: 'stable both-edges' as any }}
          >
            {messages.length === 0 && !isSending && (
              <div className="text-center text-gray-500 my-8">
                {isAuthenticated ? 'No messages yet. Start a conversation!' : 'Please log in to start chatting'}
              </div>
            )}
            
            {/* Typing/loading indicator with reserved space to prevent layout shift */}
            <div className="my-4 text-center" style={{ minHeight: '1.5rem' }}>
              <span
                className={`text-yellow-500 ${isSending ? 'inline-block animate-pulse' : 'hidden'}`}
                aria-live="polite"
              >
                Grace is thinking...
              </span>
            </div>
            
            {messages.map((msg, idx) => (
              <div key={idx} className="mb-4">
                {msg.sender === 'user' ? (
                  <div className="text-right p-2 rounded-lg bg-red-900/30 text-red-300">
                    <span className="font-bold">You:</span> {msg.text}
                  </div>
                ) : null}
                
                {msg.sender === 'grace' ? (
                  <div className="text-left p-2 rounded-lg bg-green-900/30 text-green-300">
                    <span className="font-bold">Grace:</span> {msg.text}
                  </div>
                ) : null}
              </div>
            ))}
            
            {/* This empty div is used as a reference for scrolling to the bottom */}
            <div ref={messagesEndRef} />
          </div>

          <footer className="flex border-t border-red-800 bg-black p-4">
            <textarea
              id="chat-input"
              name="chatMessage"
              autoComplete="off"
              autoCorrect="off"
              autoCapitalize="off"
              className="flex-1 mr-2 rounded bg-white/10 p-2 text-white min-h-[60px] resize-none"
              placeholder={isAuthenticated ? "Type your message... (Shift+Enter for new line)" : "Please log in to chat"}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault(); // Prevent default to avoid new line
                  if (!isSending && isAuthenticated && input.trim()) {
                    sendMessage();
                  }
                }
              }}
              disabled={!isAuthenticated || isSending}
              aria-label="Chat message input"
              ref={(el) => {
                // Conditionally focus when safe: user at bottom, not during recent user scroll, and not already focused
                if (!el) return;
                if (!isAuthenticated || isSending) return;
                const now = Date.now();
                const safeToFocus = isAtBottom && now > suppressAutoScrollUntilRef.current && document.activeElement !== el;
                if (safeToFocus) {
                  setTimeout(() => {
                    try { el.focus(); } catch {}
                  }, 100);
                }
              }}
            />
            <button
              onClick={sendMessage}
              disabled={isSending || !isAuthenticated || !input.trim()}
              className="rounded bg-red-700 px-4 py-2 hover:bg-red-900 disabled:bg-gray-700 disabled:cursor-not-allowed"
            >
              {isSending ? '...' : 'Send'}
            </button>
          </footer>
          
          {/* XFeed Section (deferred mount to reduce CLS) */}
          {showXFeed && (
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
          )}
        </main>
      </div>
  );
}
