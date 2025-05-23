import { Trade } from './apiTypes';
import {
  TradeType,
  TradeStatus,
  ChartDataPoint as BaseChartDataPoint,
  TokenData as BaseTokenData,
  BaseTransaction,
  BasePosition,
  TradeForm as BaseTradeForm,
  ApiResponse,
  MarketRequestParams,
  TradeExecutionParams
} from '../../types/trading';

export interface TokenData extends BaseTokenData {
  source: 'mango' | 'birdeye' | 'both';
  canTrade: boolean;
  canChart: boolean;
}

// UI-specific trade type that maps to the component's needs
export interface UITrade extends BaseTransaction {
  // UI-specific extensions
  originalTrade?: Trade;
  id: string;
  type: 'buy' | 'sell' | 'swap';
  token: string;
  amount: number;
  price: number;
  timestamp: string;
  status: 'pending' | 'completed' | 'failed';
  leverage?: number;
}

// Extend the base Position type with UI-specific fields
export interface UIPosition extends BasePosition {
  // Add any additional UI-specific fields here
  formattedTime?: string;
  marketId?: string;
}

// Token data for the UI
export interface TokenData extends BaseTokenData {
  symbol: string;
  name: string;
  price: number;
  change_24h: number;
  market_cap: number;
  volume_24h: number;
  marketId?: string;
  address?: string;
  decimals?: number;
  logoURI?: string;
  // For compatibility with different APIs
  id?: string;
  baseCurrency?: string;
  quoteCurrency?: string;
  baseMint?: string;
  quoteMint?: string;
}

// Trade form data
export interface TradeForm extends BaseTradeForm {
  amount: string;
  leverage: number;
  isLeverage: boolean;
  isSmartTrade: boolean;
  stopLoss: number;
  takeProfit: number;
}

// Chart data point
export interface ChartDataPoint extends BaseChartDataPoint {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  formattedTime?: string;
  price?: number; // For backward compatibility
}

// Re-export base types for convenience
export type { TradeType, TradeStatus, ApiResponse, MarketRequestParams, TradeExecutionParams };
