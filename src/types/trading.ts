// Base types
export type TradeType = 'buy' | 'sell' | 'swap';
export type TradeStatus = 'pending' | 'completed' | 'failed';

// Chart types
export interface ChartDataPoint {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  formattedTime?: string;
  timestamp?: string;
  price?: number;
}

// Token types
export interface TokenData {
  // Core fields
  symbol: string;
  name: string;
  price: number;
  change_24h: number;
  market_cap: number;
  volume_24h: number;
  
  // Optional fields for different APIs
  marketId?: string;
  address?: string;
  decimals?: number;
  logoURI?: string;
  id?: string;
  baseCurrency?: string;
  quoteCurrency?: string;
  baseMint?: string;
  quoteMint?: string;
  
  // UI and service specific fields
  source?: 'mango' | 'birdeye' | 'both';
  canTrade?: boolean;
  canChart?: boolean;
}

// Trade types
export interface BaseTransaction {
  id: string;
  type: TradeType;
  token: string;
  amount: number;
  price: number;
  timestamp: string;
  status: TradeStatus;
  leverage?: number;
}

export interface Transaction extends BaseTransaction {
  // Additional transaction-specific fields can be added here
}

export interface UITrade extends BaseTransaction {
  // UI-specific extensions
  originalTrade?: any; // Replace 'any' with specific type if available
}

// Position types
export interface BasePosition {
  id: string;
  token: string;
  amount: number;
  entryPrice: number;
  currentPrice: number;
  pnl: number;
  pnlPercent: number;
  timestamp: string;
}

export interface UIPosition extends BasePosition {
  // UI-specific extensions
  formattedTime?: string;
  marketId?: string;
}

// Form types
export interface TradeForm {
  amount: string;
  leverage: number;
  isLeverage: boolean;
  isSmartTrade: boolean;
  stopLoss: number;
  takeProfit: number;
}

// API Response types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  statusCode?: number;
}

// API Request types
export interface MarketRequestParams {
  search?: string;
  limit?: number;
  offset?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface TradeExecutionParams {
  type: TradeType;
  token: string;
  tokenAddress: string;
  amount: number;
  leverage?: number;
  stopLoss?: number;
  takeProfit?: number;
}
