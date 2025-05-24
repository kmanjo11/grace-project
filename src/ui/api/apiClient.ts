/**
 * API Client for Grace App
 * 
 * Provides standardized error handling and response processing for all API calls.
 */

// Import standardized auth utilities
import { getAuthToken, addAuthHeaders } from '../utils/authUtils';
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

// API configuration
const API_BASE_URL = ''; // Empty string for same-origin requests

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
    LIMIT_ORDERS: '/api/user/limit-orders'
  },
  WALLET: {
    DATA: '/api/wallet/data',
    INFO: '/api/wallet/info',
    GENERATE: '/api/wallet/generate',
    SEND: '/api/wallet/send',
    CONNECT_PHANTOM: '/api/wallet/phantom/connect',
    COMPLETE_PHANTOM: '/api/wallet/phantom/callback', // Updated to match actual backend endpoint
    DISCONNECT_PHANTOM: '/api/wallet/phantom/disconnect',
    BALANCE: '/api/wallet/balance',
    TRANSACTIONS: '/api/wallet/transactions'
  },
  CHAT: {
    SESSIONS: '/api/chat/sessions',
    NEW_SESSION: '/api/chat/new-session',
    HISTORY: (sessionId: string) => `/api/chat/history/${sessionId}`,
    MESSAGE: '/api/chat/message'
  },
  SOCIAL: {
    // Core social media endpoints
    SENTIMENT: '/api/social/sentiment',
    TRENDING: '/api/social/trending',
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
    HISTORY: '/api/trading/history',
    SMART_SETTINGS: '/api/trading/smart-settings',
    TOKENS: '/api/trading/tokens',
    PRICE_CHART: '/api/trading/price-chart',
    SWAP: '/api/trading/swap',
    SELL_POSITION: '/api/trading/sell-position',
    USER_POSITIONS: '/api/user/positions',
    LEVERAGE_POSITIONS: '/api/user/leverage-positions',
    SPOT_POSITIONS: '/api/user/spot-positions'
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
  // Validate input to prevent null/undefined errors
  if (!responseData) {
    return {} as T;
  }
  
  // PRIORITY 1: Handle authentication responses
  // This special case handles login/auth endpoints that return {token, user}
  if (responseData.token) {
    // Make sure we always have a user object, even if empty
    return {
      ...responseData,
      user: responseData.user || {}
    } as T;
  }
  
  // PRIORITY 2: Handle standard API success response format
  // Most endpoints return {success: true/false, data: {...}}
  if (responseData.success === true && responseData.data) {
    return responseData.data as T;
  }
  
  // PRIORITY 3: Handle legacy results format
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
  const statusCode = response.status;
  
  try {
    // Try to parse as JSON, but don't fail if it's not JSON
    const rawData = await response.json();
    
    if (!response.ok) {
      throw new ApiError(
        rawData?.message || rawData?.error || 'An unknown error occurred',
        statusCode,
        rawData
      );
    }
    
    // Normalize the response format
    const normalizedData = normalizeResponse<T>(rawData);
    
    return {
      success: true,
      data: normalizedData,
      statusCode,
      rawResponse: rawData // Keep original response for debugging
    };
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    
    if (error instanceof SyntaxError) {
      // JSON parse error
      throw new ApiError('Invalid response format', statusCode);
    }
    
    throw new ApiError('Network error', statusCode || 0);
  }
}

/**
 * Make an API request with proper error handling
 */
export async function apiRequest<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    // Use the standardized addAuthHeaders utility to handle auth headers consistently
    const authOptions = addAuthHeaders(options);
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, authOptions);

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
