import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { useAuth } from './AuthContext';
import { 
  LeveragePosition, 
  BasePosition, 
  SpotPosition, 
  UserPositionsResponse,
  ErrorDetails,
  PositionHistoryParams,
  Trade
} from '../api/apiTypes';
import { api, API_ENDPOINTS, ApiError, TradingApi } from '../api/apiClient';
import { getAuthToken } from '../utils/authUtils';
import { toast } from 'react-toastify';
import { AgentTaskManager } from '../../services/AgentTaskManager';

// Calculate position analysis metrics
const calculatePositionAnalysis = (positions: BasePosition[]) => {
  if (!positions || positions.length === 0) {
    return {
      total_positions: 0,
      total_value: 0,
      risk_level: 'No Positions',
      position_breakdown: {
        leverage: 0,
        spot: 0
      }
    };
  }

  const totalPositions = positions.length;
  const totalValue = positions.reduce((sum, pos) => sum + (pos.amount * pos.currentPrice), 0);
  
  // Separate leverage and spot positions
  const leveragePositions = positions.filter(pos => pos.type === 'leverage') as LeveragePosition[];
  const spotPositions = positions.filter(pos => pos.type === 'spot') as SpotPosition[];
  
  // Calculate average leverage
  const avgLeverage = leveragePositions.length > 0 
    ? leveragePositions.reduce((sum, pos) => sum + pos.leverage, 0) / leveragePositions.length 
    : 0;

  // Advanced risk calculation
  const riskScore = (
    (avgLeverage * leveragePositions.length) + 
    (spotPositions.length * 0.5) // Lower weight for spot positions
  );
  const riskLevel = riskScore < 5 ? 'Low Risk' 
    : riskScore < 15 ? 'Moderate Risk' 
    : 'High Risk';

  return {
    total_positions: totalPositions,
    total_value: totalValue,
    avg_leverage: avgLeverage,
    risk_level: riskLevel,
    position_breakdown: {
      leverage: leveragePositions.length,
      spot: spotPositions.length
    },
    unrealized_pnl: positions.reduce((sum, pos) => sum + (pos.unrealizedPnl || 0), 0)
  };
};

// Global event system for trading and transaction management
class TradingEventBus {
  private listeners: Record<string, Function[]> = {};

  on(event: string, callback: Function): void {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event].push(callback);
  }

  emit(event: string, data?: any): void {
    if (this.listeners[event]) {
      this.listeners[event].forEach(callback => callback(data));
    }
  }

  off(event: string, callback: Function): void {
    if (this.listeners[event]) {
      this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
    }
  }

  clear(event: string): void {
    this.listeners[event] = [];
  }
}

// Singleton event bus
export const tradingEventBus = new TradingEventBus();

// Compact interface for trading positions
// Strict type definition for incoming position data
// Extended position type for UI with calculated fields
type UIPosition = BasePosition & {
  currentValue: number;
  profitLoss: number;
  openTimestamp: string;
  leverage?: number;
  liquidationPrice?: number;
  marginRatio?: number;
  // Add any additional UI-specific fields here
};

// Validated and transformed position interface
// Transaction types for comprehensive tracking
interface TransactionDetails {
  id: string;
  type: 'buy' | 'sell' | 'swap' | 'transfer';
  token: string;
  amount: number;
  timestamp: string;
  status: 'pending' | 'completed' | 'failed';
}

interface CompactPosition {
  id: string;
  token: string;
  type: 'spot' | 'leverage';
  amount: number;
  entryPrice: number;
  currentPrice: number;
  leverage?: number;
  openTimestamp: string;
  currentValue: number;
  profitLoss: number;
}

// Type guard to validate position data
const isValidPosition = (pos: unknown): pos is BasePosition => {
  if (typeof pos !== 'object' || pos === null) return false;
  
  const position = pos as Partial<BasePosition>;
  return (
    typeof position.id === 'string' &&
    typeof position.token === 'string' &&
    (position.type === 'spot' || position.type === 'leverage') &&
    typeof position.amount === 'number' &&
    typeof position.entryPrice === 'number' &&
    typeof position.currentPrice === 'number' &&
    typeof position.openTimestamp === 'number'
  );
};

// Safe type conversion with error handling
const safeConvert = <T extends number | string | undefined>(
  value: T,
  defaultValue: T extends number ? number : string = 0 as any
): T extends number ? number : string => {
  if (value === undefined || value === null) return defaultValue as any;
  if (typeof value === 'number') return value as any;
  if (typeof value === 'string') {
    const num = parseFloat(value);
    return (isNaN(num) ? defaultValue : num) as any;
  }
  return defaultValue as any;
};

interface LightweightPositionsWidgetProps {
  initialExpanded?: boolean;
  onToggleExpand?: (expanded: boolean) => void;
  refreshInterval?: number;
}

const LightweightPositionsWidget: React.FC<LightweightPositionsWidgetProps> = ({
  initialExpanded = false,
  onToggleExpand,
  refreshInterval = 30000, // 30 seconds default
}) => {
  const { user } = useAuth();
  // Define a unified position type for the UI that includes all possible fields
  interface UIPosition {
    id: string;
    token: string;
    type: 'spot' | 'leverage';
    amount: number;
    entryPrice: number;
    currentPrice: number;
    currentValue: number;
    profitLoss: number;
    openTimestamp: string;
    // Optional fields that might be present
    side?: 'long' | 'short';
    market?: string;
    timestamp?: string;
    unrealizedPnl?: number;
    realizedPnl?: number;
    // Leverage specific fields
    leverage?: number;
    liquidationPrice?: number;
    marginRatio?: number;
  }
  
  const [positions, setPositions] = useState<UIPosition[]>([]);
  
  // Type guard to check if a position is a leverage position
  const isLeveragePosition = (position: UIPosition): position is UIPosition & { leverage: number } => {
    return position.type === 'leverage';
  };
  const [transactions, setTransactions] = useState<TransactionDetails[]>([]);
  const [isExpanded, setIsExpanded] = useState(initialExpanded);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  
  // Refs for cleanup and state management
  const isMounted = useRef(true);
  const positionInterval = useRef<NodeJS.Timeout>();
  const transactionsInterval = useRef<NodeJS.Timeout>();

  // Fetch transaction history with retry logic
  const fetchTransactions = useCallback(async (isRetry = false): Promise<void> => {
    if (!user?.token) {
      setError('Authentication required');
      return;
    }

    if (!isRetry) {
      setIsLoading(true);
    }

    try {
      const { data, success, error } = await api.get<TransactionDetails[]>(
        API_ENDPOINTS.WALLET.TRANSACTIONS,
        { headers: { 'Authorization': `Bearer ${user.token}` } }
      );
      
      if (success && data) {
        setTransactions(Array.isArray(data) ? data : []);
      } else {
        throw new Error(error || 'Failed to fetch transactions');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch transactions';
      console.error('Error fetching transactions:', error);
      
      if (!isRetry) {
        // Only show error toast on first attempt
        toast.error(errorMessage);
        // Auto-retry after delay
        setTimeout(() => fetchTransactions(true), 5000);
      }
      
      throw error; // Re-throw for handling in the caller if needed
    } finally {
      if (!isRetry) {
        setIsLoading(false);
      }
    }
  }, [user?.token]);

  // Track new trades from different sources
  const trackNewTrade = useCallback((tradeData: Partial<BasePosition>) => {
    try {
      // Validate and transform trade data
      if (!isValidPosition(tradeData)) {
        console.warn('Invalid trade data', tradeData);
        return;
      }
  
      const entryPrice = tradeData.entryPrice || 0;
      const currentPrice = tradeData.currentPrice || entryPrice;
      const amount = tradeData.amount || 0;
      const profitLoss = entryPrice ? 
        ((currentPrice - entryPrice) / entryPrice) * 100 : 0;
  
      const newPosition: UIPosition = {
        ...tradeData,
        id: tradeData.id || `trade_${Date.now()}`,
        token: tradeData.token || 'UNKNOWN',
        type: tradeData.type || 'spot',
        amount,
        entryPrice,
        currentPrice,
        openTimestamp: tradeData.openTimestamp?.toString() || new Date().toISOString(),
        timestamp: tradeData.timestamp || new Date().toISOString(),
        currentValue: amount * currentPrice,
        profitLoss
      };

      // Log transaction first to ensure it's captured before potential position updates
      const transaction: TransactionDetails = {
        id: newPosition.id,
        type: newPosition.type === 'leverage' ? 'buy' : 'swap',
        token: newPosition.token,
        amount: newPosition.amount,
        timestamp: newPosition.openTimestamp,
        status: 'completed'
      };

      // Batch state updates
      setPositions(prev => [...prev, newPosition]);
      setTransactions(prev => [transaction, ...prev]);

      // Refresh transactions data
      fetchTransactions().catch(err => {
        console.error('Error refreshing transactions:', err);
      });
    } catch (error) {
      console.error('Error tracking new trade:', error);
      toast.error('Failed to track new trade');
    }
  }, [fetchTransactions]);

  // Fetch user positions with proper error handling and type safety
  const fetchPositions = useCallback(async (isRetry = false): Promise<void> => {
    if (!user?.token) {
      setError('User not authenticated');
      return;
    }

    if (!isRetry) {
      setIsLoading(true);
      setError(null);
    }

    try {
      // Use TradingApi methods that match your API types
      // Wrap in try-catch to prevent Promise.all from failing completely if one request fails
      let spotResponse = { positions: [] };
      let leverageResponse = { positions: [] };
      
      try {
        spotResponse = await TradingApi.getUserSpotPositions();
      } catch (spotError) {
        console.error('Error fetching spot positions:', spotError);
      }
      
      try {
        leverageResponse = await TradingApi.getUserLeveragePositions();
      } catch (leverageError) {
        console.error('Error fetching leverage positions:', leverageError);
      }

      if (!isMounted.current) return;

      // Transform API positions to UI positions
      const transformToUIPosition = (pos: SpotPosition | LeveragePosition): UIPosition => {
        const basePosition: UIPosition = {
          id: pos.id,
          token: pos.token,
          type: pos.type,
          amount: pos.amount,
          entryPrice: pos.entryPrice,
          currentPrice: pos.currentPrice || 0,
          currentValue: pos.amount * (pos.currentPrice || 0),
          profitLoss: pos.unrealizedPnl || 0,
          openTimestamp: new Date(pos.openTimestamp || Date.now()).toISOString(),
          side: pos.side,
          market: pos.market,
          timestamp: pos.timestamp,
          unrealizedPnl: pos.unrealizedPnl,
          realizedPnl: pos.realizedPnl
        };

        // Add leverage-specific fields if this is a leverage position
        if (pos.type === 'leverage') {
          const levPos = pos as LeveragePosition;
          return {
            ...basePosition,
            leverage: levPos.leverage || 1,
            liquidationPrice: levPos.liquidationPrice || 0,
            marginRatio: levPos.marginRatio || 0
          };
        }

        return basePosition;
      };

      // Transform and combine all positions
      const allPositions = [
        ...(spotResponse.positions || []).map(transformToUIPosition),
        ...(leverageResponse.positions || []).map(transformToUIPosition)
      ];

      setPositions(allPositions);
      setLastUpdated(new Date());
      
    } catch (error) {
      console.error('Error fetching positions:', error);
      
      // Set empty positions array to ensure component still renders
      setPositions([]);
      
      if (!isRetry) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to fetch positions';
        setError(errorMessage);
        // Auto-retry after delay
        setTimeout(() => fetchPositions(true), 5000);
      }
      
      throw error; // Re-throw for handling in the caller if needed
    } finally {
      if (!isRetry) {
        setIsLoading(false);
      }
    }
  }, [user?.token]);

  // Fetch positions when user changes or component mounts
  useEffect(() => {
    fetchPositions();
  }, [user]);

  // Listen for trade confirmation events
  useEffect(() => {
    // Handler for trade confirmation events
    const handleTradeConfirmation = (eventData: any) => {
      console.log('Trade confirmed, refreshing positions:', eventData);
      // Refresh positions immediately after trade confirmation
      fetchPositions().catch(err => {
        console.error('Error refreshing positions after trade confirmation:', err);
      });
    };
    
    // Subscribe to trade:confirmed events
    tradingEventBus.on('trade:confirmed', handleTradeConfirmation);
    
    // Cleanup when component unmounts
    return () => {
      tradingEventBus.off('trade:confirmed', handleTradeConfirmation);
    };
  }, [fetchPositions]);

  // Set up polling with proper cleanup
  useEffect(() => {
    if (!user) return;

    // Initial fetch
    const initialFetch = async () => {
      try {
        await Promise.all([
          fetchPositions(),
          fetchTransactions()
        ]);
      } catch (error) {
        console.error('Initial fetch failed:', error);
      }
    };
    initialFetch();

    // Set up polling intervals
    positionInterval.current = setInterval(() => {
      fetchPositions().catch(console.error);
    }, refreshInterval);

    transactionsInterval.current = setInterval(() => {
      fetchTransactions().catch(console.error);
    }, refreshInterval * 2);

    // Cleanup function
    return () => {
      if (positionInterval.current) clearInterval(positionInterval.current);
      if (transactionsInterval.current) clearInterval(transactionsInterval.current);
    };
  }, [user, refreshInterval, fetchPositions, fetchTransactions]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isMounted.current = false;
      if (positionInterval.current) clearInterval(positionInterval.current);
      if (transactionsInterval.current) clearInterval(transactionsInterval.current);
    };
  }, []);

  // Close a position with confirmation and proper error handling
  const closePosition = useCallback(async (positionId: string): Promise<boolean> => {
    if (!user?.token) {
      toast.error('Authentication required to close positions');
      return false;
    }

    // Find the position to close
    const positionToClose = positions.find(pos => pos.id === positionId);
    if (!positionToClose) {
      toast.error('Position not found');
      return false;
    }

    // Confirmation dialog
    const confirmClose = window.confirm(`Are you sure you want to close this ${positionToClose.token} position?`);
    if (!confirmClose) return false;

    try {
      setIsLoading(true);
      
      const response = await api.post<{ success: boolean; message?: string; error?: string }>(
        '/api/trading/sell-position',
        { positionId },
        { headers: { 'Authorization': `Bearer ${user.token}` } }
      );
      
      if (response.data?.success) {
        // Optimistic update - remove the position immediately
        setPositions(prev => prev.filter(pos => pos.id !== positionId));
        
        // Emit position sold event
        tradingEventBus.emit('positionSold', {
          ...positionToClose,
          timestamp: new Date().toISOString()
        });

        // Refresh data in the background
        await Promise.all([
          fetchPositions(),
          fetchTransactions()
        ]);
        
        toast.success(response.data.message || `Successfully closed ${positionToClose.token} position`);
        return true;
      } else {
        throw new Error(response.data?.message || 'Failed to close position');
      }
    } catch (error) {
      console.error('Error selling position', error);
    }
  }, [user?.token, positions, setIsLoading, fetchPositions, fetchTransactions, tradingEventBus]);

  // Memoize position metrics to prevent unnecessary recalculations
  const positionMetrics = useMemo(() => {
    const totalValue = positions.reduce((sum, pos) => sum + pos.currentValue, 0);
    const totalPnl = positions.reduce((sum, pos) => sum + pos.profitLoss, 0);
    const winningPositions = positions.filter(pos => pos.profitLoss > 0).length;
    
    return {
      totalValue,
      totalPnl,
      winRate: positions.length > 0 ? (winningPositions / positions.length) * 100 : 0,
      totalPositions: positions.length,
      lastUpdated
    };
  }, [positions, lastUpdated]);
  
  // Close a position with confirmation and proper error handling
  const handleClosePosition = useCallback(async (positionId: string, percentage?: number): Promise<boolean> => {
    if (!user?.token) {
      toast.error('Authentication required to close positions');
      return false;
    }

    // Find the position to close
    const positionToClose = positions.find(pos => pos.id === positionId);
    if (!positionToClose) {
      toast.error('Position not found');
      return false;
    }
    
    const isPartial = percentage && percentage > 0 && percentage < 100;
    const closeAmount = isPartial 
      ? (positionToClose.amount * percentage / 100) 
      : positionToClose.amount;
    
    // For UI confirmation - we don't need to show this since we now have the slider UI
    // that shows exactly what will be closed
    /*
    const confirmClose = window.confirm(
      `Are you sure you want to close ${isPartial ? percentage + '% of' : ''} this ${positionToClose.token} position?`
    );
    
    if (!confirmClose) return false;
    */

    try {
      setIsLoading(true);
      
      // Use the TradingApi to sell/close the position
      const response = await TradingApi.sellPosition({
        positionId,
        token: positionToClose.token,
        amount: positionToClose.amount,
        type: positionToClose.type,
        percentage: percentage // This will adjust the amount on the backend if needed
      });
      
      if (response.success) {
        // Optimistic update
        if (isPartial) {
          // For partial closes, update the position amount
          setPositions(prev => prev.map(pos => 
            pos.id === positionId 
              ? { ...pos, amount: pos.amount - closeAmount } 
              : pos
          ));
        } else {
          // For full closes, remove the position
          setPositions(prev => prev.filter(pos => pos.id !== positionId));
        }
        
        // Emit position sold event
        tradingEventBus.emit('positionSold', {
          ...positionToClose,
          amount: closeAmount,
          percentage: percentage || 100,
          isPartial: isPartial,
          timestamp: new Date().toISOString()
        });

        // Refresh data in the background
        await Promise.all([
          fetchPositions(),
          fetchTransactions()
        ]);
        
        const successMessage = isPartial
          ? `Successfully closed ${percentage}% of ${positionToClose.token} position`
          : `Successfully closed ${positionToClose.token} position`;
          
        toast.success(response.message || successMessage);
        return true;
      } else {
        throw new Error(response.error || 'Failed to close position');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to close position';
      console.error('Error closing position:', error);
      toast.error(`Error: ${errorMessage}`);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, [user?.token, positions, fetchPositions, fetchTransactions]);

  return (
    <div className="bg-gray-800 shadow-md rounded-lg p-4 border border-gray-700">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold text-red-300">Public Trading Positions</h2>
        <button
          onClick={() => {
            setIsExpanded(!isExpanded);
          }}
          className="text-red-400 hover:text-red-300 text-sm bg-red-900/30 px-2 py-1 rounded border border-red-800"
        >
          {isExpanded ? 'Collapse' : 'Expand'}
        </button>
      </div>
      {positions.length === 0 ? (
        <div className="text-center py-4 border border-gray-700 rounded bg-gray-900/50 p-4">
          <p className="text-gray-300 mb-2">No trading positions available</p>
          <p className="text-sm text-gray-400">Your active trades will appear here</p>
        </div>
      ) : (
        <div className="overflow-hidden">
          {positions.map((position) => (
            <PositionCard 
              key={position.id} 
              position={position} 
              onClose={handleClosePosition} 
            />
          ))}
        </div>
      )}
    </div>
  );
};

// Position Card Component
const PositionCard: React.FC<{ 
  position: BasePosition | CompactPosition; 
  onClose: (id: string, percentage?: number) => Promise<boolean> 
}> = ({ position, onClose }) => {
  const isLeverage = position.type === 'leverage';
  const pnl = 'unrealizedPnl' in position ? position.unrealizedPnl || 0 : 0;
  const pnlPercent = position.entryPrice > 0 
    ? ((position.currentPrice - position.entryPrice) / position.entryPrice) * 100 
    : 0;
  const openTimestamp = 'openTimestamp' in position 
    ? typeof position.openTimestamp === 'string' 
      ? new Date(position.openTimestamp).getTime() 
      : position.openTimestamp 
    : Date.now();
  
  const [isClosing, setIsClosing] = useState(false);
  const [closePercentage, setClosePercentage] = useState(100); // Default to full closure
  const [isLoading, setIsLoading] = useState(false);

  const handleClose = async () => {
    try {
      setIsLoading(true);
      const success = await onClose(position.id, closePercentage);
      if (success) {
        tradingEventBus.emit('positionClosed', { 
          positionId: position.id,
          percentage: closePercentage
        });
        // Reset UI state after successful closure
        setIsClosing(false);
        setClosePercentage(100);
      }
    } catch (error) {
      console.error('Error closing position:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const closeAmount = (position.amount * closePercentage / 100).toFixed(4);
  const closeValue = (position.currentPrice * position.amount * closePercentage / 100).toFixed(2);

  return (
    <div className="bg-gray-900 rounded-lg p-4 mb-3 border-l-4 border-red-500 border border-gray-700">
      <div className="flex justify-between items-start">
        <div>
          <h4 className="font-medium text-white">{position.token}</h4>
          <div className="text-sm text-gray-400">
            {position.amount.toFixed(4)} @ ${position.entryPrice.toFixed(2)}
          </div>
          {isLeverage && 'leverage' in position && (
            <div className="text-xs text-yellow-400 mt-1">
              Leverage: {position.leverage}x
            </div>
          )}
          <div className="text-xs text-gray-500 mt-1">
            {new Date(openTimestamp).toLocaleString()}
          </div>
        </div>
        <div className="text-right">
          <div className={`text-sm font-medium ${
            pnl >= 0 ? 'text-green-400' : 'text-red-400'
          }`}>
            ${pnl.toFixed(2)} ({pnlPercent.toFixed(2)}%)
          </div>
          <div className="text-xs text-gray-400">
            ${(position.amount * position.currentPrice).toFixed(2)}
          </div>
          <div className="text-xs text-gray-500">
            Current: ${position.currentPrice.toFixed(2)}
          </div>
        </div>
      </div>
      
      {!isClosing ? (
        <div className="mt-3 flex justify-end space-x-2">
          <button
            onClick={() => setIsClosing(true)}
            className="text-xs bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded"
          >
            Close Position
          </button>
        </div>
      ) : (
        <div className="mt-3 border-t border-gray-700 pt-2">
          <div className="flex items-center justify-between mb-2">
            <div className="text-sm text-gray-300">
              Close: <span className="font-medium">{closePercentage}%</span> 
              <span className="text-xs text-gray-400 ml-1">({closeAmount} {position.token} ≈ ${closeValue})</span>
            </div>
            <button
              onClick={() => setIsClosing(false)}
              className="text-xs text-gray-400 hover:text-white"
            >
              Cancel
            </button>
          </div>
          
          <div className="mb-3">
            <input 
              type="range" 
              min="1" 
              max="100" 
              value={closePercentage} 
              onChange={(e) => setClosePercentage(parseInt(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>1%</span>
              <span>25%</span>
              <span>50%</span>
              <span>75%</span>
              <span>100%</span>
            </div>
          </div>
          
          <div className="flex justify-end space-x-2">
            <button
              onClick={handleClose}
              disabled={isLoading}
              className={`text-xs ${isLoading ? 'bg-gray-600' : 'bg-red-600 hover:bg-red-700'} text-white px-3 py-1 rounded flex items-center`}
            >
              {isLoading && (
                <svg className="animate-spin -ml-1 mr-2 h-3 w-3 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              )}
              {isLoading ? 'Processing...' : 'Confirm Close'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default LightweightPositionsWidget;