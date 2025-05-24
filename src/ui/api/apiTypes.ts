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

export interface TradeExecutionResult {
  success: boolean;
  result?: {
    status: 'pending' | 'confirmed' | 'confirmation_required' | 'failed';
    confirmation_id?: string;
    txHash?: string;
    current_price?: number;
    estimated_total?: number;
    stop_loss_price?: number;
    take_profit_price?: number;
    smart_trading_applied?: boolean;
    original_amount?: string;
    adjusted_amount?: string;
    error?: string;
    platform?: string;
    trade_id?: string;
    confirmation_details?: {
      market?: string;
      side?: string;
      size?: number;
      price?: number;
      leverage?: number;
      order_type?: string;
      order?: any;
    };
  };
  status?: string;
  error?: string;
  requiresConfirmation?: boolean;
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
  success: boolean;
  positions: BasePosition[];
  metadata?: any;
  error?: {
    message: string;
    code: string;
  };
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

// TradingApi is implemented in apiClient.ts - DO NOT DUPLICATE HERE
