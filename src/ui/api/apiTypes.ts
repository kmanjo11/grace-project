// Pagination Types
export interface PaginationInfo {
  has_more: boolean;
  next_cursor?: string;
  limit: number;
  total: number;
}

// Trade Types
export interface Trade {
  id: string;
  market: string;
  side: 'buy' | 'sell';
  price: number;
  size: number;
  timestamp: string;
  trade_source: string;
  trade_type: string;
  leverage: number;
}

export interface TradeHistoryResponse {
  success: boolean;
  trades: Trade[];
  pagination: PaginationInfo;
  metadata: {
    user_identifier?: string;
    start_time?: string;
    end_time?: string;
    timestamp: string;
    fetch_sources: string[];
  };
  error?: string;
}

// Position Types
export interface BasePosition {
  id: string;
  token: string;
  type: 'leverage' | 'spot';
  amount: number;
  entryPrice: number;
  currentPrice: number;
  openTimestamp: number;
  unrealizedPnl?: number;
  realizedPnl?: number;
  side?: 'long' | 'short';
  market?: string;
  timestamp?: string;
}

export interface PositionHistoryEntry extends Omit<BasePosition, 'id' | 'type'> {
  market: string;
  size: number;
  leverage: number;
  side: 'long' | 'short';
  pnl: number;
  realizedPnl: number;
  unrealizedPnl: number;
  timestamp: string;
  trades?: Array<{
    timestamp: string;
    side: string;
    price: number;
    size: number;
    leverage: number;
  }>;
}

export interface PositionHistoryResponse {
  success: boolean;
  position_history: PositionHistoryEntry[];
  pnl_over_time?: Array<{
    timestamp: string;
    total_pnl: number;
    markets: Record<string, any>;
  }>;
  pagination: PaginationInfo;
  metadata: {
    user_identifier: string;
    market?: string;
    start_time: string;
    end_time: string;
    interval: string;
    total_positions: number;
    has_more: boolean;
    cursor?: string;
  };
  error?: string;
  error_details?: ErrorDetails;
}

export interface LeveragePosition extends BasePosition {
  leverage: number;
  liquidationPrice?: number;
  marginRatio?: number;
}

export interface SpotPosition extends BasePosition {}

export interface UserPositionsResponse {
  positions: BasePosition[];
  metadata?: any;
}

export interface APIEndpoints {
  USER: {
    PROFILE: string;
    LEVERAGE_POSITIONS: string;
    SPOT_POSITIONS: string;
    LIMIT_ORDERS: string;
    POSITION_HISTORY: string;
    TRADE_HISTORY: string;
  }
}

import { API_ENDPOINTS } from './apiClient';
import { getAuthToken } from '../utils/authUtils';

// Error handling types
export interface ErrorDetails {
  code: string;
  status: number;
  message?: string;
  timestamp?: string;
  [key: string]: any; // Allow for additional error details
}

// Position History Parameters
export interface PositionHistoryParams {
  market?: string;
  startTime?: string | number;
  endTime?: string | number;
  interval?: string;
  includePnl?: boolean;
  includeLivePnl?: boolean;
  cursor?: string;
  limit?: number;
}

export const TradingApi = {
  getUserLeveragePositions: async (): Promise<UserPositionsResponse> => {
    try {
      const response = await fetch(API_ENDPOINTS.USER.LEVERAGE_POSITIONS, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.message || 'Unknown error');
      }
      
      return {
        positions: data.positions || [],
        metadata: data.metadata || {}
      };
    } catch (error) {
      console.error('Error fetching leverage positions:', error);
      throw error;
    }
  },

  getUserLimitOrders: async (): Promise<UserPositionsResponse> => {
    try {
      const response = await fetch(API_ENDPOINTS.USER.LIMIT_ORDERS, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.message || 'Unknown error');
      }
      
      return {
        positions: data.positions || [],
        metadata: data.metadata || {}
      };
    } catch (error) {
      console.error('Error fetching limit orders:', error);
      throw error;
    }
  },

  getUserSpotPositions: async (): Promise<UserPositionsResponse> => {
    try {
      const response = await fetch(API_ENDPOINTS.USER.SPOT_POSITIONS, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Failed to fetch spot positions');
      }
      
      return data;
    } catch (error) {
      console.error('Error fetching spot positions:', error);
      throw error;
    }
  },
  
  /**
   * Get position history with pagination and filtering
   */
  getPositionHistory: async (params: PositionHistoryParams = {}): Promise<PositionHistoryResponse> => {
    try {
      // Build query parameters
      const queryParams = new URLSearchParams();
      
      if (params.market) queryParams.append('market', params.market);
      if (params.startTime) queryParams.append('start_time', String(params.startTime));
      if (params.endTime) queryParams.append('end_time', String(params.endTime));
      if (params.interval) queryParams.append('interval', params.interval);
      if (params.includePnl !== undefined) queryParams.append('include_pnl', String(params.includePnl));
      if (params.includeLivePnl) queryParams.append('include_live_pnl', 'true');
      if (params.cursor) queryParams.append('cursor', params.cursor);
      if (params.limit) queryParams.append('limit', String(params.limit));
      
      const url = `${API_ENDPOINTS.USER.POSITION_HISTORY}?${queryParams.toString()}`;
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`
        }
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching position history:', error);
      throw error;
    }
  },
  
  /**
   * Get trade history with pagination and filtering
   */
  getTradeHistory: async (params: {
    market?: string;
    startTime?: string | number;
    endTime?: string | number;
    tradeType?: string;
    cursor?: string;
    limit?: number;
  } = {}): Promise<TradeHistoryResponse> => {
    try {
      // Build query parameters
      const queryParams = new URLSearchParams();
      
      if (params.market) queryParams.append('market', params.market);
      if (params.startTime) queryParams.append('start_time', String(params.startTime));
      if (params.endTime) queryParams.append('end_time', String(params.endTime));
      if (params.tradeType) queryParams.append('trade_type', params.tradeType);
      if (params.cursor) queryParams.append('cursor', params.cursor);
      if (params.limit) queryParams.append('limit', String(params.limit));
      
      const url = `${API_ENDPOINTS.USER.TRADE_HISTORY}?${queryParams.toString()}`;
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`
        }
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching trade history:', error);
      throw error;
    }
  }
};
