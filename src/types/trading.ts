// Base types
export type BaseOrderType = 'market' | 'limit' | 'ioc' | 'postOnly' | 'reduceOnly' | 'fillOrKill' | 'immediateOrCancel';
export type AdvancedOrderType = 'twap' | 'vwap' | 'iceberg';
export type OrderType = BaseOrderType | AdvancedOrderType;

export type TradeType = 'buy' | 'sell' | 'swap' | 'close_position';
export type TradeStatus = 'new' | 'open' | 'closed' | 'canceled' | 'expired' | 'triggered' | 'settling' | 'settled' | 'partially_filled' | 'rejected' | 'pending_cancel';
export type PositionSide = 'long' | 'short' | 'both';
export type TimeInForce = 'ioc' | 'postOnly' | 'reduceOnly' | 'fillOrKill' | 'gtc' | 'gtd' | 'fok' | 'immediateOrCancel';

export type ExecutionStrategy = 'single' | 'twap' | 'vwap' | 'iceberg';
export type RoutingStrategy = 'smart' | 'direct' | 'aggregate';

export interface CircuitBreakerState {
  isTriggered: boolean;
  reason?: string;
  triggeredAt?: number;
  cooldownUntil?: number;
  failureCount: number;
  lastError?: Error;
}

// Mango Markets specific types
export type MangoAccountStatus = 'uninitialized' | 'initialized' | 'liquidated' | 'bankrupt' | 'beingLiquidated';

// Mango supports a subset of order types natively
export type MangoOrderType = 'limit' | 'ioc' | 'postOnly' | 'market' | 'fillOrKill' | 'immediateOrCancel' | 'reduceOnly';

// Type guard to check if an order type is natively supported by Mango
export function isMangoOrderType(orderType: string): orderType is MangoOrderType {
  return ['limit', 'ioc', 'postOnly', 'market', 'fillOrKill', 'immediateOrCancel', 'reduceOnly'].includes(orderType);
}

export type MangoSelfTradeBehavior = 'decrementTake' | 'cancelProvide' | 'abortTransaction';

export interface MangoTokenPosition {
  mint: string;
  amount: number;
  value: number;
  index: number;
  nativeDeposits: number;
  nativeBorrows: number;
  nativeDepositIndex: number;
  nativeBorrowIndex: number;
}

export interface MangoPerpPosition {
  marketIndex: number;
  basePosition: number;
  quotePosition: number;
  settledPnl: number;
  unsettledPnl: number;
  lastCumulativeFundingRate: number;
  takerBase: number;
  takerQuote: number;
  mngoAccrued: number;
}

export interface MangoAccountInfo {
  address: string;
  owner: string;
  delegate?: string;
  accountNum: number;
  tokens: MangoTokenPosition[];
  perpAccounts: MangoPerpPosition[];
  inUseCount: number;
  isDelegate: boolean;
  isUpgradeable: boolean;
  isFrozen: boolean;
  isNative: boolean;
  rentExemptMin: number;
  closeAuthority?: string;
  extendedMeta?: Record<string, any>;
}

// Mango Markets enums
export enum MangoInstruction {
  InitMangoAccount = 'InitMangoAccount',
  Deposit = 'Deposit',
  Withdraw = 'Withdraw',
  AddSpotMarket = 'AddSpotMarket',
  AddPerpMarket = 'AddPerpMarket',
  CancelAllPerpOrders = 'CancelAllPerpOrders',
  ConsumeEvents = 'ConsumeEvents',
  CancelPerpOrderByClientId = 'CancelPerpOrderByClientId',
  PlacePerpOrder = 'PlacePerpOrder',
  PlacePerpOrder2 = 'PlacePerpOrder2',
  CancelPerpOrder = 'CancelPerpOrder',
  SettleFunds = 'SettleFunds',
  SettleFees = 'SettleFees',
  SettlePnl = 'SettlePnl',
  UpdateFunding = 'UpdateFunding',
  UpdateRootBank = 'UpdateRootBank',
  UpdateMarginBasket = 'UpdateMarginBasket',
  UpdateMargin = 'UpdateMargin',
  UpdateMarginDeposit = 'UpdateMarginDeposit',
  UpdateMarginLending = 'UpdateMarginLending',
  UpdateMarginLiquidation = 'UpdateMarginLiquidation',
  UpdateMarginRepay = 'UpdateMarginRepay',
  UpdateMarginWithdraw = 'UpdateMarginWithdraw',
  UpdatePerpMarket = 'UpdatePerpMarket',
  UpdatePerpMarket2 = 'UpdatePerpMarket2',
  UpdateSpotMarket = 'UpdateSpotMarket',
  UpdateSpotMarket2 = 'UpdateSpotMarket2',
  UpdateSpotMarket3 = 'UpdateSpotMarket3',
  UpdateSpotMarket4 = 'UpdateSpotMarket4',
  UpdateSpotMarket5 = 'UpdateSpotMarket5',
  UpdateSpotMarket6 = 'UpdateSpotMarket6',
  UpdateSpotMarket7 = 'UpdateSpotMarket7',
  UpdateSpotMarket8 = 'UpdateSpotMarket8',
  UpdateSpotMarket9 = 'UpdateSpotMarket9',
  UpdateSpotMarket10 = 'UpdateSpotMarket10',
}

export interface TradeFees {
  maker: number;
  taker: number;
  liquidation: number;
}

export interface TradingLimits {
  minOrderSize: number;
  minPriceIncrement: number;
  minSizeIncrement: number;
  maxLeverage: number;
}

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
export interface MangoTokenInfo {
  // Core token info
  mint: string;
  rootBank: string;
  decimals: number;
  mintDecimals: number;
  
  // Mango specific
  nativeDeposits: number;
  nativeBorrows: number;
  nativeDepositIndex: number;
  nativeBorrowIndex: number;
  
  // Oracle
  oraclePrice: number;
  oraclePriceLastUpdated: number;
  oraclePriceLastUpdatedSlot: number;
  
  // Interest rates
  depositRate: number;
  borrowRate: number;
  
  // Risk parameters
  maintLeverage: number;
  initLeverage: number;
  liquidationFee: number;
  
  // UI
  symbol: string;
  name: string;
  logoURI?: string;
}

export interface TokenData {
  // Core identification
  symbol: string;
  name: string;
  address: string;
  decimals: number;
  
  // Market data
  price: number;
  change_24h: number;
  market_cap: number;
  volume_24h: number;
  high_24h?: number;
  low_24h?: number;
  
  // Mango specific fields (make optional for compatibility)
  mint?: string;
  rootBank?: string;
  nodeBank?: string;
  bankNum?: number;
  oracle?: string;
  oraclePrice?: number;
  depositRate?: number;
  borrowRate?: number;
  depositIndex?: number;
  borrowIndex?: number;
  totalDeposits?: number;
  totalBorrows?: number;
  maintAssetWeight?: number;
  initAssetWeight?: number;
  maintLiabWeight?: number;
  initLiabWeight?: number;
  liquidationFee?: number;
  platformFee?: number;
  insuranceFound?: boolean;
  
  // Include all MangoTokenInfo fields as optional
  mintDecimals?: number;
  nativeDeposits?: number;
  nativeBorrows?: number;
  nativeDepositIndex?: number;
  nativeBorrowIndex?: number;
  oraclePriceLastUpdated?: number;
  oraclePriceLastUpdatedSlot?: number;
  maintLeverage?: number;
  initLeverage?: number;
  
  // Trading info
  minOrderSize?: number;
  minPriceIncrement?: number;
  minSizeIncrement?: number;
  maxLeverage?: number;
  
  // Metadata
  logoURI?: string;
  website?: string;
  twitter?: string;
  description?: string;
  
  // Source tracking
  source: 'mango' | 'birdeye' | 'gmgn' | 'custom';
  canTrade: boolean;
  canChart: boolean;
  isStablecoin?: boolean;
  
  // Additional API-specific fields
  [key: string]: any; // For any additional fields from different APIs
}

// Trade types
// Mango specific transaction data
export interface MangoTransactionData {
  // Mango specific fields
  mangoAccount: string;
  mangoGroup: string;
  perpMarket?: string;
  openOrders?: string;
  
  // Transaction metadata
  signature: string;
  slot: number;
  blockTime: number;
  
  // Order status
  orderId?: string;
  clientOrderId?: number;
  
  // For spot trades
  fromToken?: string;
  toToken?: string;
  
  // For perp trades
  basePosition?: number;
  quotePosition?: number;
  
  // Fees and funding
  feeRate?: number;
  feeAmount?: number;
  feeToken?: string;
  
  // Liquidation info if applicable
  liquidation?: {
    liquidator: string;
    liquidatee: string;
    price: number;
    feeToLiquidator: number;
    feeToInsuranceFund: number;
  };
}

export interface BaseTransaction {
  // Core transaction data
  id: string;
  clientOrderId?: string | number;
  type: TradeType;
  symbol: string;
  tokenAddress: string;
  quoteTokenAddress?: string;
  amount: number;
  filledAmount: number;
  remainingAmount: number;
  price: number;
  averagePrice?: number;
  stopPrice?: number;
  triggerPrice?: number;
  
  // Mango specific data
  mangoData?: MangoTransactionData;
  
  // Status and timing
  status: TradeStatus;
  createdAt: string | number;
  updatedAt?: string | number;
  closedAt?: string | number;
  
  // Fees and costs
  feeAmount?: number;
  feeCurrency?: string;
  feeRate?: number;
  
  // Additional metadata
  tags?: string[];
  metadata?: Record<string, any>;
  
  // Error handling
  error?: string;
  errorCode?: string;
}

export interface Transaction extends BaseTransaction {
  // Additional transaction-specific fields can be added here
}

export interface UITrade extends BaseTransaction {
  // UI-specific extensions
  originalTrade?: any; // Replace 'any' with specific type if available
}

// Position types
export interface MangoPosition {
  // Mango specific position fields
  mangoAccount: string;
  mangoGroup: string;
  perpMarket: string;
  perpMarketIndex: number;
  basePosition: number;
  quotePosition: number;
  settledPnl: number;
  unsettledPnl: number;
  
  // Funding and interest
  takerBase: number;
  takerQuote: number;
  mngoAccrued: number;
  
  // Risk metrics
  maintMarginRequired: number;
  maintMarginRatio: number;
  initMarginRatio: number;
  
  // Timestamps
  lastCumulativeFundingRate: number;
  lastCumulativeInterestRate: number;
}

export interface BasePosition {
  // Position identification
  id: string;
  symbol: string;
  tokenAddress: string;
  quoteTokenAddress?: string;
  
  // Mango specific
  mangoAccount?: string;
  mangoGroup?: string;
  perpMarket?: string;
  perpMarketIndex?: number;
  
  // Position details
  side: PositionSide;
  amount: number;
  entryPrice: number;
  currentPrice: number;
  liquidationPrice?: number;
  
  // Mango specific position data
  basePosition?: number;
  quotePosition?: number;
  settledPnl?: number;
  unsettledPnl?: number;
  
  // Funding and interest
  cumulativeFundingRate?: number;
  cumulativeInterestRate?: number; 
  
  // Risk metrics
  maintMarginRequired?: number;
  maintMarginRatio?: number;
  initMarginRatio?: number;
  
  // PnL calculations
  pnl: number;
  pnlPercent: number;
  pnlPercentAnnualized?: number;
  
  // Risk metrics
  leverage: number;
  notionalValue: number;
  maintenanceMargin: number;
  initialMargin: number;
  
  // Timestamps
  openedAt: string | number;
  updatedAt?: string | number;
  
  // Funding and fees
  fundingRate?: number;
  fundingPaid?: number;
  
  // Additional metadata
  tags?: string[];
  metadata?: Record<string, any>;
  
  // Status
  status: 'open' | 'closed' | 'liquidated';
  
  // Related orders
  takeProfitOrderId?: string;
  stopLossOrderId?: string;
  
  // Risk management
  riskToRewardRatio?: number;
  breakEvenPrice?: number;
}

export interface UIPosition extends BasePosition {
  // UI-specific extensions
  formattedTime?: string;
  marketId?: string;
}

// Form types
export interface TradeForm {
  // Core trade parameters
  amount: string;
  price?: string;
  orderType: OrderType;
  timeInForce?: TimeInForce;
  
  // Leverage and margin
  leverage: number;
  isLeverage: boolean;
  marginType?: 'isolated' | 'cross';
  
  // Advanced order types
  isSmartTrade: boolean;
  
  // Risk management
  stopLoss?: {
    price?: number;
    triggerPrice?: number;
    type: 'limit' | 'market';
    trailValue?: number;
  };
  
  takeProfit?: {
    price?: number;
    triggerPrice?: number;
    type: 'limit' | 'market';
  };
  
  // UI state
  isPostOnly: boolean;
  reduceOnly: boolean;
  
  // Slippage and price impact
  slippageTolerance?: number;
  priceImpact?: number;
  
  // Additional settings
  closePosition?: boolean;
  closePercentage?: number;
  
  // Callbacks
  onFill?: (fill: Partial<BaseTransaction>) => void;
  onError?: (error: Error) => void;
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

// Mango specific order parameters
export interface MangoOrderParams {
  // Order type specific to Mango
  orderType: MangoOrderType;
  selfTradeBehavior?: MangoSelfTradeBehavior;
  
  // Mango specific fields
  mangoAccount?: string;
  mangoGroup?: string;
  perpMarket?: string;
  clientOrderId?: number;
  
  // Advanced order parameters
  maxQuoteQuantity?: number;
  reduceOnly?: boolean;
  
  // Post only handling
  postOnly?: boolean;
  postOnlyAllowAsks?: boolean;
  postOnlyAllowBids?: boolean;
  
  // ICOC (Immediate or Cancel) specific
  immediateOrCancel?: boolean;
  
  // For conditional orders
  triggerCondition?: {
    price: number;
    isAbove: boolean;
  };
  
  // For stop orders
  triggerPrice?: number;
  triggerDirection?: 'above' | 'below'; // Renamed from triggerCondition to avoid conflict
  
    // Additional order parameters
  limitPrice?: number;
  maxBaseQuantity?: number;
  clientId?: number;
  expiryTimestamp?: number;
  
  // For advanced order types
  orderTypeV2?: 'limit' | 'ioc' | 'postOnly' | 'market' | 'fillOrKill' | 'immediateOrCancel';
  
  // For stop orders v2
  triggerPriceType?: 'last' | 'oracle';
  triggerConditionPrice?: number;
  triggerOrderType?: 'market' | 'limit';
  triggerLimitPrice?: number;
}

// Base order parameters that are common across all trading systems
export interface BaseOrderParams {
  // Core trade parameters
  type: TradeType;
  side: 'buy' | 'sell';
  symbol: string;
  amount: number;
  price?: number; // For limit orders
  
  // Token details
  tokenAddress: string;
  quoteTokenAddress?: string;
  
  // Order configuration
  timeInForce?: TimeInForce;
  reduceOnly?: boolean;
  postOnly?: boolean;
  
  // Advanced order types
  stopPrice?: number;
  triggerPrice?: number;
  trailValue?: number;
  
  // Risk management
  leverage?: number;
  stopLoss?: number | { price: number; type: 'limit' | 'market' };
  takeProfit?: number | { price: number; type: 'limit' | 'market' };
  
  // Additional metadata
  clientOrderId?: string | number;
  userAddress?: string;
  referrer?: string;
  
  // UI/UX
  slippageTolerance?: number;
  maxSlippage?: number;
  
  // Callbacks
  onUpdate?: (update: TradeUpdate) => void;
}

// Smart order routing parameters
export interface SmartOrderParams {
  // Smart order routing
  executionStrategy?: ExecutionStrategy;
  routingStrategy?: RoutingStrategy;
  
  // TWAP/VWAP specific
  timeHorizonMs?: number;  // Total duration for order completion
  intervalMs?: number;     // Time between order slices
  maxSlippageBps?: number; // Max allowed slippage in basis points
  
  // Circuit breaker
  maxPriceImpactBps?: number;  // Max allowed price impact
  circuitBreaker?: CircuitBreakerState;
  
  // Venue specific parameters
  venueParams?: Record<string, any>;
  
  // Fallback options
  fallbackToMarket?: boolean;
  allowPartialFill?: boolean;
  
  // Monitoring and callbacks
  onExecutionUpdate?: (update: ExecutionUpdate) => void;
  onError?: (error: TradeError) => void;
}

export interface ExecutionUpdate {
  orderId: string;
  status: TradeStatus;
  filledAmount: number;
  remainingAmount: number;
  avgFillPrice: number;
  lastFillPrice: number;
  timestamp: number;
  venue?: string;
  metadata?: Record<string, any>;
}

export interface TradeError extends Error {
  code: string;
  isRecoverable: boolean;
  retryAfter?: number;
  metadata?: Record<string, any>;
}

// Union of all possible order parameters
type OrderParams = Omit<BaseOrderParams, 'orderType' | 'clientOrderId'> & 
  Omit<MangoOrderParams, 'orderType' | 'clientOrderId'> & 
  Partial<SmartOrderParams>;

// Combine base order params with Mango specific params and smart order routing
export interface TradeExecutionParams extends Omit<OrderParams, 'orderType' | 'clientOrderId'> {
  // Mango specific overrides
  mangoAccount?: string;
  mangoGroup?: string;
  perpMarket?: string;
  
  // For spot trading
  fromToken?: string;
  toToken?: string;
  
  // Order type - supports both Mango native and advanced order types
  orderType: OrderType;
  
  // Unified client order ID that works across all order types
  // Can be either string or number for maximum compatibility
  clientOrderId?: string | number;
  
  // For advanced order types, we need to specify the underlying Mango order type
  underlyingOrderType?: MangoOrderType;
  
  // Additional metadata for order execution
  metadata?: {
    isMangoNative?: boolean;
    requiresApproval?: boolean;
    estimatedGas?: number;
    feeToken?: string;
    feeAmount?: number;
  }
  
  // Price impact and slippage protection
  maxPriceImpactBps?: number;
  maxSlippageBps?: number;
  
  // Execution constraints
  minFillPercentage?: number; // 0-100
  
  // Settlement options
  settleOnFill?: boolean;
  
  // Referral program
  referrer?: string;
  
  // Additional metadata
  tags?: string[];
  clientMetadata?: Record<string, any>;
}

export interface TradeUpdate {
  orderId: string;
  status: TradeStatus;
  filledAmount: number;
  remainingAmount: number;
  avgFillPrice?: number;
  lastUpdateTime: number;
  transactionHash?: string;
  error?: string;
}
