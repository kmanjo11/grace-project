/**
 * API Client for Grace App
 * 
 * Provides standardized error handling and response processing for all API calls.
 */

// Auth token key for localStorage
const AUTH_TOKEN_KEY = 'grace_auth_token';

// Get auth token from localStorage
export const getAuthToken = (): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(AUTH_TOKEN_KEY);
  }
  return null;
};

// Save auth token to localStorage
export const saveAuthToken = (token: string): void => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(AUTH_TOKEN_KEY, token);
  }
};

// Remove auth token from localStorage
export const removeAuthToken = (): void => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(AUTH_TOKEN_KEY);
  }
};

// Add auth headers to request options
export const addAuthHeaders = (options: RequestInit = {}): RequestInit => {
  const token = getAuthToken();
  if (token) {
    return {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    };
  }
  return options;
};
import { Trade, TradeHistoryResponse, PositionHistoryResponse, TradeExecutionResult, PositionHistoryEntry, UserPositionsResponse, BasePosition } from './apiTypes';
// No circular imports

// API Response types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  statusCode?: number;
  rawResponse?: any; // Original unprocessed response for debugging
}

// API Error types
export class ApiError extends Error {
  public statusCode: number;
  public data?: any;

  constructor(message: string, statusCode: number, data?: any) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
    this.data = data;
  }
}

// API configuration - use environment variable if available, otherwise use relative path
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || ''; // Will be set in Docker build

// Ensure API_BASE_URL ends with a slash
const getBaseUrl = () => {
  if (API_BASE_URL.endsWith('/')) {
    return API_BASE_URL.slice(0, -1);
  }
  return API_BASE_URL;
};

// API endpoints constants
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/api/auth/login',
    REGISTER: '/api/auth/register',
    VERIFY_TOKEN: '/api/auth/verify_token',
    LOGOUT: '/api/auth/logout',
    REFRESH_TOKEN: '/api/auth/refresh',
    FORGOT_PASSWORD: '/api/auth/forgot-password',
    RESET_PASSWORD: '/api/auth/reset-password'
  },
  USER: {
    PROFILE: '/api/user/profile',
    LEVERAGE_POSITIONS: '/api/user/leverage_positions',
    SPOT_POSITIONS: '/api/user/spot_positions',
    POSITION_HISTORY: '/api/user/position_history',
    TRADE_HISTORY: '/api/user/trade_history',
    LIMIT_ORDERS: '/api/limit-orders'
  },
  WALLET: {
    DATA: '/api/wallet/data',
    INFO: '/api/wallet/info',
    MANGO_BALANCE: '/api/wallet/mango-balance', // Mango exc balance
    GENERATE: '/api/wallet/generate',
    SEND: '/api/wallet/send',
    CONNECT_PHANTOM: '/api/wallet/phantom/connect',
    COMPLETE_PHANTOM: '/api/wallet/phantom/callback', // Updated to match actual backend endpoint
    DISCONNECT_PHANTOM: '/api/wallet/phantom/disconnect',
    // Map BALANCE to INFO since the server uses /api/wallet/info endpoint to get wallet balance
    BALANCE: '/api/wallet/info',
    TRANSACTIONS: '/api/wallet/transactions'
  },
  CHAT: {
    // Get all chat sessions for the authenticated user
    SESSIONS: '/api/chat/sessions',
    // Create a new chat session
    NEW_SESSION: '/api/chat/session/new',
    // Get chat history for a specific session
    HISTORY: (sessionId: string) => `/api/chat/history/${sessionId}`,
    // Send a chat message
    MESSAGE: '/api/chat/message'
  },
  SOCIAL: {
    // Core social media endpoints
    SENTIMENT: '/api/social/sentiment',
    TRENDING: '/api/social/trending-topics',
    INFLUENTIAL: '/api/social/influential',
    TWEETS: '/api/social/tweets',
  },
  MANGO: {
    // Mango Markets API endpoints
    BASE: '/api/mango',
    OHLCV: '/api/mango/ohlcv',
    MARKETS: '/api/mango/markets',
    ORDER_BOOK: '/api/mango/orderbook',
    TRADES: '/api/mango/trades',
    MARKET_STATS: '/api/mango/market-stats',
    COMMUNITIES: '/api/social/communities',
    ENTITIES: '/api/social/entities',
    FEED: '/api/social/feed',
    CONNECTIONS: '/api/social/connections'
  },
  TRADING: {
    EXECUTE: '/api/trading/execute',
    CONFIRM: '/api/trading/confirm',
    SMART_SETTINGS: '/api/trading/smart-settings',
    TOKENS: '/api/trading/tokens',
    PRICE_CHART: '/api/trading/price-chart',
    SWAP: '/api/trading/swap',
    SELL_POSITION: '/api/trading/sell-position',
    USER_POSITIONS: '/api/user/positions',
    LEVERAGE_POSITIONS: '/api/user/leverage_positions',
    SPOT_POSITIONS: '/api/user/spot_positions'
  },
  SETTINGS: {
    // Updated to match backend implementation
    PROFILE: '/api/user/settings',  // Matches user_settings endpoint in backend
    NOTIFICATIONS: '/api/settings/notifications', // Keep for future implementation
    // Additional backend settings endpoint
    TRADING_SETTINGS: '/api/trading/smart-settings', // Matches trading_smart_settings in backend
  },
};

/**
 * Normalize different API response formats to a consistent structure
 * 
 * This prioritizes API response formats in a predictable order:
 * 1. Auth responses with token and user
 * 2. Standard success responses with data
 * 3. Results-based responses
 * 4. Default pass-through
 */
function normalizeResponse<T>(responseData: any): T {
  // Handle auth responses with token
  if (responseData && typeof responseData === 'object' && 'token' in responseData) {
    // Save the token when received in the response
    saveAuthToken(responseData.token);
    // Remove token from response data to avoid exposing it
    const { token, ...rest } = responseData;
    return rest as T;
  }
  
  // Handle standard success response format
  if (responseData && typeof responseData === 'object' && 'success' in responseData) {
    return responseData as T;
  }
  
  // Handle results-based response format
  if (responseData && typeof responseData === 'object' && 'results' in responseData) {
    return {
      success: true,
      data: responseData.results,
      ...responseData
    } as unknown as T;
  }
  
  // Default: pass through the response data as-is
  // Some endpoints return results in a 'results' property
  if (responseData.results) {
    return responseData.results as T;
  }
  
  // PRIORITY 4: Handle direct data format without success flag
  // Some old endpoints return {data: {...}} directly
  if (responseData.data && responseData.success === undefined) {
    return responseData.data as T;
  }
  
  // Fall back to returning the entire response as is
  return responseData as T;
}

/**
 * Process the API response and handle errors consistently
 */
async function processResponse<T>(response: Response): Promise<ApiResponse<T>> {
  try {
    // Clone the response so we can read it multiple times
    const responseClone = response.clone();
    
    // First try to parse as JSON, but handle non-JSON responses gracefully
    let data;
    try {
      data = await response.json();
      
      // If we get a new token in the response, save it
      if (data && data.token) {
        saveAuthToken(data.token);
      }
    } catch (e) {
      // If we can't parse as JSON, return the text response
      const text = await response.text();
      return {
        success: false,
        error: text || 'Invalid response format',
        statusCode: response.status,
        rawResponse: responseClone
      };
    }
    
    // Handle HTTP error status codes
    if (!response.ok) {
      // If we get a 401, clear the auth token
      if (response.status === 401) {
        removeAuthToken();
        // You might want to redirect to login here or handle the unauthorized state
        window.location.href = '/login';
      }
      
      return {
        success: false,
        error: data?.message || data?.error || `HTTP error ${response.status}`,
        statusCode: response.status,
        data,
        rawResponse: responseClone
      };
    }
    
    // Success case - normalize the response data
    return {
      success: true,
      data: normalizeResponse<T>(data),
      statusCode: response.status,
      rawResponse: responseClone
    };
  } catch (error) {
    console.error('Error processing response:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error processing response',
      rawResponse: response.clone()
    };
  }
}

/**
 * Make an API request with proper error handling
 */
async function apiRequest<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    // Get base URL from environment or use relative path
    const baseUrl = process.env.REACT_APP_API_URL || '';
    const url = endpoint.startsWith('http') ? endpoint : `${baseUrl}${endpoint}`;
    
    // Add auth headers to the request
    const requestOptions = addAuthHeaders({
      ...options,
      credentials: 'include', // Include cookies for CSRF protection
      headers: {
        ...options.headers,
        'Content-Type': 'application/json',
      },
    });
    
    const response = await fetch(url, requestOptions);

    return await processResponse<T>(response);
  } catch (error) {
    if (error instanceof ApiError) {
      // Rethrow ApiError instances
      throw error;
    }
    
    // Handle network errors
    throw new ApiError(
      error instanceof Error ? error.message : 'Network error',
      0
    );
  }
}

// Convenience methods for common HTTP methods
export const api = {
  async get<T = any>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    return apiRequest<T>(endpoint, { ...options, method: 'GET' });
  },
  
  async post<T = any>(endpoint: string, data: any, options: RequestInit = {}): Promise<ApiResponse<T>> {
    return apiRequest<T>(endpoint, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
  
  async put<T = any>(endpoint: string, data: any, options: RequestInit = {}): Promise<ApiResponse<T>> {
    return apiRequest<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },
  
  async delete<T = any>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    return apiRequest<T>(endpoint, { ...options, method: 'DELETE' });
  }
};

// Chat API Types
interface ChatSession {
  id: string;
  title: string;
  created: string;
  updated: string;
  message_count: number;
  metadata?: Record<string, any>;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

interface ApiErrorResponse {
  error: string;
  using_fallback?: boolean;
  [key: string]: any;
}

// Chat API methods
export const ChatApi = {
  /**
   * Get all chat sessions for the authenticated user
   * @returns Promise with list of chat sessions
   */
  /**
   * Get all chat sessions for the authenticated user
   * @param limit Optional limit for pagination
   * @param offset Optional offset for pagination
   * @returns Promise with list of chat sessions and pagination info
   */
  async getSessions(limit?: number, offset?: number): Promise<{
    sessions: ChatSession[];
    total: number;
    has_more: boolean;
  }> {
    try {
      const params = new URLSearchParams();
      if (limit) params.append('limit', limit.toString());
      if (offset) params.append('offset', offset.toString());
      
      const query = params.toString();
      const url = query ? `${API_ENDPOINTS.CHAT.SESSIONS}?${query}` : API_ENDPOINTS.CHAT.SESSIONS;
      
      const response = await api.get<{
        data: ChatSession[];
        total: number;
        has_more: boolean;
      }>(url);
      
      return {
        sessions: response.data?.data || [],
        total: response.data?.total || 0,
        has_more: response.data?.has_more || false,
      };
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || 'Failed to fetch chat sessions';
      const usingFallback = error.response?.data?.using_fallback;
      console.error('Error fetching chat sessions:', errorMessage, { usingFallback });
      throw new Error(errorMessage);
    }
  },

  /**
   * Create a new chat session
   * @param title Optional title for the new session
   * @returns Promise with the new session ID
   */
  async createSession(title?: string): Promise<{ session_id: string }> {
    try {
      const response = await api.post<{ session_id: string }>(
        API_ENDPOINTS.CHAT.NEW_SESSION,
        { title: title || 'New Chat' }
      );
      return response.data;
    } catch (error) {
      console.error('Error creating chat session:', error);
      throw new Error('Failed to create chat session');
    }
  },

  /**
   * Get chat history for a specific session
   * @param sessionId ID of the chat session
   * @returns Promise with chat history
   */
  /**
   * Get chat history for a specific session
   * @param sessionId ID of the chat session
   * @param limit Optional limit for pagination
   * @param offset Optional offset for pagination
   * @returns Promise with chat history and pagination info
   */
  async getHistory(
    sessionId: string,
    limit?: number,
    offset?: number
  ): Promise<{
    messages: ChatMessage[];
    total: number;
    has_more: boolean;
  }> {
    try {
      const params = new URLSearchParams();
      if (limit) params.append('limit', limit.toString());
      if (offset) params.append('offset', offset.toString());
      
      const query = params.toString();
      const url = query 
        ? `${API_ENDPOINTS.CHAT.HISTORY(sessionId)}?${query}`
        : API_ENDPOINTS.CHAT.HISTORY(sessionId);
      
      const response = await api.get<{
        data: ChatMessage[];
        total: number;
        has_more: boolean;
      }>(url);
      
      return {
        messages: response.data?.data || [],
        total: response.data?.total || 0,
        has_more: response.data?.has_more || false,
      };
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || 'Failed to fetch chat history';
      const usingFallback = error.response?.data?.using_fallback;
      console.error('Error fetching chat history:', errorMessage, { usingFallback });
      throw new Error(errorMessage);
    }
  },

  /**
   * Send a message in a chat session
   * @param sessionId ID of the chat session
   * @param message The message content
   * @returns Promise with the assistant's response
   */
  /**
   * Send a message in a chat session
   * @param sessionId ID of the chat session
   * @param message The message content
   * @param metadata Optional metadata to include with the message
   * @returns Promise with the assistant's response
   */
  async sendMessage(
    sessionId: string,
    message: string,
    metadata?: Record<string, any>
  ): Promise<{
    response: string;
    metadata?: Record<string, any>;
    session_id: string;
    message_id: string;
    timestamp: string;
  }> {
    try {
      const response = await api.post<{ data: any }>(
        API_ENDPOINTS.CHAT.MESSAGE,
        {
          session_id: sessionId,
          message,
          timestamp: new Date().toISOString(),
          ...(metadata && { metadata }),
        }
      );
      
      if (!response.data || !response.data.data) {
        throw new Error('Invalid response format from server');
      }
      
      return {
        response: response.data.data.response || '',
        metadata: response.data.data.metadata,
        session_id: response.data.data.session_id || sessionId,
        message_id: response.data.data.message_id || `msg_${Date.now()}`,
        timestamp: response.data.data.timestamp || new Date().toISOString(),
      };
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || 'Failed to send chat message';
      const usingFallback = error.response?.data?.using_fallback;
      console.error('Error sending chat message:', errorMessage, { usingFallback });
      throw new Error(errorMessage);
    }
  },
};

// Trading API methods
export const TradingApi = {
  /**
   * Execute a trade (first step of two-phase trade execution)
   * @param params Trade execution parameters
   * @returns Trade execution result with confirmation ID if confirmation required
   */
  async executeTrade(params: {
    action: 'buy' | 'sell';
    token: string;
    amount: string | number;
    isLeverage?: boolean;
    leverage?: number;
    stopLoss?: number;
    takeProfit?: number;
  }): Promise<TradeExecutionResult> {
    try {
      const response = await api.post('/api/trading/execute', {
        ...params,
        amount: params.amount.toString()
      });
      return response.data;
    } catch (error) {
      console.error('Trade execution failed:', error);
      throw new Error(
        error.response?.data?.error || 'Trade execution failed'
      );
    }
  },

  /**
   * Confirm a pending trade (second step of two-phase trade execution)
   * @param confirmationId The confirmation ID from executeTrade response
   * @returns Final trade execution result
   */
  async confirmTrade(confirmationId: string): Promise<TradeExecutionResult> {
    try {
      const response = await api.post('/api/trading/confirm', {
        confirmation_id: confirmationId
      });
      return response.data;
    } catch (error) {
      console.error('Trade confirmation failed:', error);
      throw new Error(
        error.response?.data?.error || 'Trade confirmation failed'
      );
    }
  },
  
  /**
   * Close an existing position (leverage or spot)
   * @param params Position parameters to close
   * @returns Position closing result
   */
  async closePosition(params: {
    market: string;
    position_id?: string;
    size?: number;
    price?: number;
  }): Promise<any> {
    try {
      const response = await api.post('/api/trading/sell-position', params);
      return response.data;
    } catch (error) {
      console.error('Position closing failed:', error);
      throw new Error(
        error.response?.data?.error || 'Failed to close position'
      );
    }
  },
  
  /**
   * Sell a spot token for another token (usually USDC)
   * @param params Token selling parameters
   * @returns Token selling result
   */
  async sellToken(params: {
    token: string;
    amount: number | string;
    target_token?: string;
    price?: number;
  }): Promise<any> {
    try {
      const response = await api.post('/api/trading/sell-token', {
        ...params,
        amount: params.amount.toString()
      });
      return response.data;
    } catch (error) {
      console.error('Token selling failed:', error);
      throw new Error(
        error.response?.data?.error || 'Failed to sell token'
      );
    }
  },
  
  /**
   * Sell or close a position (full or partial)
   * @param params Position selling parameters
   * @returns Result of the position sale
   */
  async sellPosition(params: {
    positionId: string;
    token: string;
    amount: number;
    type: 'spot' | 'leverage';
    percentage?: number; // Optional: percentage of position to close (0-100)
  }): Promise<{success: boolean; message?: string; error?: string}> {
    try {
      const requestData = {...params};
      
      // If percentage is provided, adjust the amount accordingly
      if (params.percentage && params.percentage > 0 && params.percentage < 100) {
        requestData.amount = (params.amount * params.percentage / 100);
      }
      
      const response = await api.post(API_ENDPOINTS.TRADING.SELL_POSITION, requestData);
      return response.data;
    } catch (error) {
      console.error('Failed to close position:', error);
      throw new Error(
        error.response?.data?.error || 'Failed to close position'
      );
    }
  },

  /**
   * Get user's leverage positions from Mango V3
   * @returns User's leverage positions with success/error status
   */
  async getUserLeveragePositions(): Promise<UserPositionsResponse> {
    try {
      const response = await api.get<UserPositionsResponse>(API_ENDPOINTS.USER.LEVERAGE_POSITIONS);
      
      // If response already has the right format, return it directly
      if (response.data && typeof response.data === 'object' && 'success' in response.data) {
        return response.data as UserPositionsResponse;
      }
      
      // Otherwise format according to Mango V3 spec
      return {
        success: true,
        positions: Array.isArray(response.data) ? response.data : [],
        metadata: {
          total_positions: Array.isArray(response.data) ? response.data.length : 0,
          timestamp: new Date().toISOString()
        }
      };
    } catch (error) {
      console.error('Error fetching leverage positions:', error);
      return {
        success: false,
        positions: [],
        error: {
          message: error instanceof Error ? error.message : 'Failed to fetch leverage positions',
          code: 'POSITION_FETCH_ERROR'
        }
      };
    }
  },

  /**
   * Get user's spot positions from wallet balances
   * @returns User's spot positions with success/error status
   */
  async getUserSpotPositions(): Promise<UserPositionsResponse> {
    try {
      const response = await api.get<UserPositionsResponse>(API_ENDPOINTS.USER.SPOT_POSITIONS);
      
      // If response already has the right format, return it directly
      if (response.data && typeof response.data === 'object' && 'success' in response.data) {
        return response.data as UserPositionsResponse;
      }
      
      // Otherwise format according to Mango V3 spec
      return {
        success: true,
        positions: Array.isArray(response.data) ? response.data : [],
        metadata: {
          total_positions: Array.isArray(response.data) ? response.data.length : 0,
          timestamp: new Date().toISOString()
        }
      };
    } catch (error) {
      console.error('Error fetching spot positions:', error);
      return {
        success: false,
        positions: [],
        error: {
          message: error instanceof Error ? error.message : 'Failed to fetch spot positions',
          code: 'POSITION_FETCH_ERROR'
        }
      };
    }
  },

  /**
   * Get position history for a user with pagination and filtering
   * @param params Query parameters for filtering position history
   * @returns Promise with position history data
   */
  getPositionHistory: async (params?: {
    market?: string;
    startTime?: string | number;
    endTime?: string | number;
    interval?: string;
    includePnl?: boolean;
    includeLivePnl?: boolean;
    cursor?: string;
    limit?: number;
  }): Promise<PositionHistoryResponse> => {
    try {
      // Build query parameters
      const queryParams = new URLSearchParams();
      
      if (params?.market) queryParams.append('market', params.market);
      if (params?.startTime) queryParams.append('start_time', String(params.startTime));
      if (params?.endTime) queryParams.append('end_time', String(params.endTime));
      if (params?.interval) queryParams.append('interval', params.interval);
      if (params?.includePnl !== undefined) queryParams.append('include_pnl', String(params.includePnl));
      if (params?.includeLivePnl) queryParams.append('include_live_pnl', 'true');
      if (params?.cursor) queryParams.append('cursor', params.cursor);
      if (params?.limit) queryParams.append('limit', String(params.limit));
      
      const response = await fetch(`${API_ENDPOINTS.USER.POSITION_HISTORY}?${queryParams.toString()}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`
        }
      });
      
      const data = await response.json();
      
      // Handle error responses
      if (!response.ok) {
        const errorData = data?.error || {};
        throw new ApiError(
          errorData.message || `HTTP error! status: ${response.status}`,
          response.status,
          {
            code: errorData.code || 'api_error',
            status: errorData.status || response.status,
            timestamp: errorData.timestamp || new Date().toISOString(),
            ...(errorData.details && { details: errorData.details })
          }
        );
      }
      
      // Transform the successful response to match the PositionHistoryResponse type
      return {
        success: data.success,
        position_history: data.position_history || [],
        pnl_over_time: data.pnl_over_time || [],
        pagination: data.pagination || {
          has_more: data.metadata?.has_more || false,
          next_cursor: data.metadata?.cursor,
          limit: params?.limit || 100,
          total: data.metadata?.total || 0
        },
        metadata: {
          user_identifier: data.metadata?.user_identifier || '',
          market: params?.market || 'all',
          start_time: data.metadata?.start_time || new Date().toISOString(),
          end_time: data.metadata?.end_time || new Date().toISOString(),
          interval: params?.interval || '1d',
          total_positions: data.metadata?.total || 0,
          has_more: data.metadata?.has_more || false,
          cursor: data.metadata?.cursor
        }
      };
    } catch (error) {
      console.error('Error fetching position history:', error);
      
      // Handle ApiError instances
      if (error instanceof ApiError) {
        return {
          success: false,
          position_history: [],
          pnl_over_time: [],
          pagination: {
            has_more: false,
            next_cursor: undefined,
            limit: params?.limit || 100,
            total: 0
          },
          metadata: {
            user_identifier: '',
            market: params?.market || 'all',
            start_time: new Date().toISOString(),
            end_time: new Date().toISOString(),
            interval: params?.interval || '1d',
            total_positions: 0,
            has_more: false
          },
          error: error.message,
          error_details: error.data
        };
      }
      
      // Handle other types of errors
      return {
        success: false,
        position_history: [],
        pnl_over_time: [],
        pagination: {
          has_more: false,
          next_cursor: undefined,
          limit: params?.limit || 100,
          total: 0
        },
        metadata: {
          user_identifier: '',
          market: params?.market || 'all',
          start_time: new Date().toISOString(),
          end_time: new Date().toISOString(),
          interval: params?.interval || '1d',
          total_positions: 0,
          has_more: false
        },
        error: error instanceof Error ? error.message : 'Unknown error',
        error_details: {
          code: 'unexpected_error',
          status: 500,
          timestamp: new Date().toISOString()
        }
      };
    }
  },

  /**
   * Get detailed position history for a specific position
   * @param positionId ID of the position to get history for
   * @param params Additional query parameters
   * @returns Promise with detailed position history
   */
  getPositionDetails: async (
    positionId: string,
    params?: {
      startTime?: string | number;
      endTime?: string | number;
      interval?: string;
    }
  ): Promise<PositionHistoryEntry> => {
    try {
      // Convert params to query string
      const queryParams = new URLSearchParams({ positionId });
      if (params?.startTime) queryParams.append('startTime', String(params.startTime));
      if (params?.endTime) queryParams.append('endTime', String(params.endTime));
      if (params?.interval) queryParams.append('interval', params.interval);

      const endpoint = `${API_ENDPOINTS.USER.POSITION_HISTORY}/details?${queryParams.toString()}`;
      // Create headers object with proper typing
      const authHeaders = addAuthHeaders();
      const headers = new Headers();
      headers.append('Content-Type', 'application/json');
      
      // Add auth headers if they exist
      if (authHeaders) {
        Object.entries(authHeaders).forEach(([key, value]) => {
          if (value) headers.append(key, value);
        });
      }
      
      const response = await api.get<{ success: boolean; data: PositionHistoryEntry }>(endpoint, { headers });

      if (!response.success) {
        throw new Error(response.error || 'Failed to fetch position details');
      }

      return (response.data as any).data;
    } catch (error) {
      console.error('Error fetching position details:', error);
      throw error;
    }
  }
};

export default api;
