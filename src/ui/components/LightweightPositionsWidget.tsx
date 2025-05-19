import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from './AuthContext';
import { TradingApi } from '../api/apiTypes';
import { LeveragePosition, BasePosition, SpotPosition } from '../api/apiTypes';
import { api, API_ENDPOINTS, ApiError } from '../api/apiClient';
import { getAuthToken } from '../utils/authUtils';
import { AgentTaskManager } from '../../services/AgentTaskManager';

// Enhanced Position Tracking Hook
const usePositionTracking = () => {
  const [positions, setPositions] = useState<BasePosition[]>([]);
  const [positionAnalysis, setPositionAnalysis] = useState<any>({});
  const [transactions, setTransactions] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTransactions = useCallback(async () => {
    try {
      const response = await fetch(API_ENDPOINTS.WALLET.TRANSACTIONS, {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`
        }
      });
      
      const data = await response.json();
      if (data.success) {
        setTransactions(data.transactions || []);
      }
    } catch (error) {
      console.error('Error fetching transactions:', error);
    }
  }, []);

  const fetchPositions = useCallback(async () => {
    try {
      setIsLoading(true);
      
      // Fetch both leverage and spot positions
      const [leverageResponse, spotResponse] = await Promise.all([
        fetch(API_ENDPOINTS.TRADING.LEVERAGE_POSITIONS, {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getAuthToken()}`
          }
        }).then(res => res.json()),
        fetch(API_ENDPOINTS.TRADING.SPOT_POSITIONS, {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getAuthToken()}`
          }
        }).then(res => res.json())
      ]);

      // Combine positions
      const combinedPositions = [
        ...leverageResponse.positions,
        ...spotResponse.positions
      ];

      setPositions(combinedPositions);
      updatePositionAnalysis(combinedPositions);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      console.error('Position tracking error:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updatePositionAnalysis = useCallback((currentPositions: BasePosition[]) => {
    const analysis = calculatePositionAnalysis(currentPositions);
    setPositionAnalysis(analysis);
  }, []);

  // Sell a specific position
  const sellPosition = useCallback(async (positionId: string) => {
    try {
      const foundPosition = positions.find(pos => pos.id === positionId);
      if (!foundPosition) {
        throw new Error('Position not found');
      }

      const response = await fetch(API_ENDPOINTS.TRADING.SELL_POSITION, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`
        },
        body: JSON.stringify({ positionId })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to sell position');
      }

      if (data.success) {
        // Update positions and analysis
        const updatedPositions = positions.filter(pos => pos.id !== positionId);
        setPositions(updatedPositions);
        updatePositionAnalysis(updatedPositions);

        // Emit sell event with transaction details
        tradingEventBus.emit('positionSold', {
          ...foundPosition,
          soldAmount: data.soldAmount,
          timestamp: data.timestamp
        });

        // Show success message
        console.log(data.message);
      } else {
        throw new Error(data.error || 'Unknown error during position sale');
      }
    } catch (error) {
      console.error('Error selling position', error);
      setError(error instanceof Error ? error.message : 'Unknown error');
    }
  }, [positions, updatePositionAnalysis]);

  // Set up real-time position tracking and transaction history
  useEffect(() => {
    const trackPositionsInterval = setInterval(fetchPositions, 30000); // Update every 30 seconds
    const trackTransactionsInterval = setInterval(fetchTransactions, 60000); // Update every minute
    
    // Initial fetch
    fetchPositions();
    fetchTransactions();

    return () => {
      clearInterval(trackPositionsInterval);
      clearInterval(trackTransactionsInterval);
    };
  }, [fetchPositions, fetchTransactions]);

  return { 
    positions, 
    positionAnalysis, 
    isLoading, 
    error, 
    refetch: fetchPositions,
    sellPosition 
  };
};

// Utility function to calculate position analysis
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
// API Response Type for Positions
interface PositionsResponse {
  success: boolean;
  error?: string;
  positions?: RawPosition[];
}

// Raw Position Data Type
interface RawPosition {
  id?: string;
  token?: string;
  type?: 'spot' | 'leverage';
  amount?: number | string;
  entryPrice?: number | string;
  currentPrice?: number | string;
  leverage?: number | string;
  openTimestamp?: string;
  market?: string;
  side?: 'long' | 'short';
  liquidationPrice?: number | string;
  marginUsed?: number | string;
  unrealizedPnl?: number | string;
  pnlPercentage?: number | string;
}

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

// Type guard to validate and transform position
function isValidPosition(pos: RawPosition): pos is CompactPosition {
  // Validate required fields and convert types
  try {
    return !!(
      pos.id && 
      typeof pos.id === 'string' &&
      pos.token && 
      typeof pos.token === 'string' &&
      (pos.type === 'spot' || pos.type === 'leverage') &&
      pos.amount !== undefined &&
      pos.entryPrice !== undefined &&
      pos.currentPrice !== undefined
    );
  } catch {
    return false;
  }
}

// Safe type conversion function
function safeConvert(value: number | string | undefined, defaultValue: number = 0): number {
  if (value === undefined || value === null) return defaultValue;
  const converted = Number(value);
  return isNaN(converted) ? defaultValue : converted;
}

interface LightweightPositionsWidgetProps {
  initialExpanded?: boolean;
  onToggleExpand?: (expanded: boolean) => void;
}

const LightweightPositionsWidget: React.FC<LightweightPositionsWidgetProps> = ({
  initialExpanded = false,
  onToggleExpand
}) => {
  const { user } = useAuth();
  const [positions, setPositions] = useState<CompactPosition[]>([]);
  const [transactions, setTransactions] = useState<any[]>([]);
  const [isExpanded, setIsExpanded] = useState(initialExpanded);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch transaction history
  const fetchTransactions = useCallback(async () => {
    try {
      const response = await fetch(API_ENDPOINTS.WALLET.TRANSACTIONS, {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`
        }
      });
      
      const data = await response.json();
      if (data.success) {
        setTransactions(data.transactions || []);
      }
    } catch (error) {
      console.error('Error fetching transactions:', error);
    }
  }, []);

  // Track new trades from different sources
  const trackNewTrade = useCallback((tradeData: RawPosition) => {
    // Validate and transform trade data
    if (!isValidPosition(tradeData)) {
      console.warn('Invalid trade data', tradeData);
      return;
    }

    const newPosition: CompactPosition = {
      id: tradeData.id || `trade_${Date.now()}`,
      token: tradeData.token as string,
      type: tradeData.type === 'leverage' ? 'leverage' : 'spot',
      amount: safeConvert(tradeData.amount),
      entryPrice: safeConvert(tradeData.entryPrice),
      currentPrice: safeConvert(tradeData.currentPrice, safeConvert(tradeData.entryPrice)),
      leverage: tradeData.leverage ? safeConvert(tradeData.leverage) : undefined,
      openTimestamp: tradeData.openTimestamp || new Date().toISOString(),
      currentValue: safeConvert(tradeData.amount) * safeConvert(tradeData.currentPrice, safeConvert(tradeData.entryPrice)),
      profitLoss: tradeData.entryPrice ? 
        ((safeConvert(tradeData.currentPrice) - safeConvert(tradeData.entryPrice)) / safeConvert(tradeData.entryPrice)) * 100 : 0
    };

    setPositions(prev => [...prev, newPosition]);

    // Update transactions after successful sell
    fetchTransactions();

    // Log transaction
    const transaction: TransactionDetails = {
      id: newPosition.id,
      type: newPosition.type === 'leverage' ? 'buy' : 'swap',
      token: newPosition.token,
      amount: newPosition.amount,
      timestamp: new Date().toISOString(),
      status: 'completed'
    };

    setTransactions(prev => [transaction, ...prev]);
  }, []);

  // Fetch user-specific positions with minimal authentication
  const fetchPositions = async () => {
    console.log('🔍 Fetching User Positions');

    try {
      // Attempt to get user identifier from local storage or session
      const userIdentifier = localStorage.getItem('user_identifier') || 
                             sessionStorage.getItem('user_identifier');

      if (!userIdentifier) {
        console.warn('🚫 No user identifier found, skipping position fetch');
        setPositions([]);
        return;
      }

      // Fetch spot positions
      const spotResponse: PositionsResponse = await api.get(API_ENDPOINTS.TRADING.USER_POSITIONS, {
        headers: {
          'Content-Type': 'application/json',
          'X-User-Identifier': userIdentifier
        }
      });
      
      // Fetch leverage positions from Mango V3
      const leverageResponse: PositionsResponse = await api.get(API_ENDPOINTS.TRADING.LEVERAGE_POSITIONS, {
        headers: {
          'Content-Type': 'application/json',
          'X-User-Identifier': userIdentifier
        }
      });
      
      console.log('📊 Spot Positions:', spotResponse);
      console.log('📊 Leverage Positions:', leverageResponse);

      // Combine and validate positions
      const allPositions = [
        ...(spotResponse.positions || []),
        ...(leverageResponse.positions || [])
      ];

      if (!Array.isArray(allPositions)) {
        console.error('❌ Invalid positions data type');
        throw new Error('Invalid positions data');
      }
      
      // Transform and validate positions
      const compactPositions: CompactPosition[] = allPositions
        .filter(isValidPosition)
        .map(pos => ({
          id: pos.id as string,
          token: pos.token as string,
          type: pos.type === 'leverage' ? 'leverage' : 'spot',
          amount: safeConvert(pos.amount),
          entryPrice: safeConvert(pos.entryPrice),
          currentPrice: safeConvert(pos.currentPrice),
          leverage: pos.leverage ? safeConvert(pos.leverage) : undefined,
          openTimestamp: pos.openTimestamp || new Date().toISOString(),
          currentValue: safeConvert(pos.amount) * safeConvert(pos.currentPrice),
          profitLoss: safeConvert(pos.entryPrice) ? 
            ((safeConvert(pos.currentPrice) - safeConvert(pos.entryPrice)) / safeConvert(pos.entryPrice)) * 100 : 0
        }));
      
      console.log(`✅ Processed ${compactPositions.length} user positions`);

      // Always set positions, even if empty
      setPositions(compactPositions);
    } catch (error) {
      console.error('❌ Failed to fetch user positions', error);
      setPositions([]); // Clear existing positions on error
    }
  };

  // Fetch positions when user changes or component mounts
  useEffect(() => {
    fetchPositions();
  }, [user]);

  // Initial fetch and periodic refresh
  useEffect(() => {
    if (user) {
      // Initial fetch
      fetchPositions();
      fetchTransactions();

      // Set up periodic refresh
      const positionsInterval = setInterval(fetchPositions, 60000); // Refresh every minute
      const transactionsInterval = setInterval(fetchTransactions, 60000); // Refresh every minute

      // Listen for trading events
      tradingEventBus.on('newTrade', trackNewTrade);
      tradingEventBus.on('positionUpdate', fetchPositions);

      return () => {
        clearInterval(positionsInterval);
        clearInterval(transactionsInterval);
        tradingEventBus.off('newTrade', trackNewTrade);
        tradingEventBus.off('positionUpdate', fetchPositions);
      };
    }
  }, [user, trackNewTrade]);

  // Sell a specific position
  const sellPosition = async (positionId: string) => {
    const [positions, setPositions] = useState<BasePosition[]>([]);
    const [positionAnalysis, setPositionAnalysis] = useState<any>({});
    try {
      const foundPosition = positions.find(pos => pos.id === positionId);
      if (!foundPosition) {
        throw new Error('Position not found');
      }

      const response = await fetch(API_ENDPOINTS.TRADING.SELL_POSITION, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`
        },
        body: JSON.stringify({ positionId })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to sell position');
      }

      if (data.success) {
        // Remove position from local state
        setPositions(prev => prev.filter(pos => pos.id !== positionId));
        
        // Update position analysis
        const remainingPositions = positions.filter(pos => pos.id !== positionId);
        const analysis = calculatePositionAnalysis(remainingPositions);
        setPositionAnalysis(analysis);

        // Emit sell event with transaction details
        tradingEventBus.emit('positionSold', {
          ...foundPosition,
          soldAmount: data.soldAmount,
          timestamp: data.timestamp
        });

        // Show success message
        console.log(data.message);
      } else {
        throw new Error(data.error || 'Unknown error during position sale');
      }
    } catch (error) {
      console.error('Error selling position', error);
    }
  };

  // Diagnostic rendering to understand widget state
  console.log('💬 Public Positions Widget Render:', {
    positionsCount: positions.length
  });

  return (
    <div className="bg-white shadow-md rounded-lg p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold">Public Trading Positions</h2>
        <button
          onClick={() => {
            setIsExpanded(!isExpanded);
            onToggleExpand && onToggleExpand(!isExpanded);
          }}
          className="text-blue-500 hover:text-blue-700"
        >
          {isExpanded ? 'Collapse' : 'Expand'}
        </button>
      </div>
      {positions.length === 0 ? (
        <div className="text-center py-4">
          <p className="text-gray-500 mb-2">No public positions available</p>
          <p className="text-sm text-gray-400">Trading activity will be displayed here</p>
        </div>
      ) : (
        <div className={`transition-all duration-300 ${isExpanded ? 'max-h-96' : 'max-h-24'} overflow-hidden`}>
          <table className="w-full">
            <thead>
              <tr className="bg-gray-100">
                <th className="p-2 text-left">Token</th>
                <th className="p-2 text-left">Type</th>
                <th className="p-2 text-left">Amount</th>
                <th className="p-2 text-left">Entry Price</th>
                <th className="p-2 text-left">Current Price</th>
                <th className="p-2 text-left">P/L %</th>
              </tr>
            </thead>
            <tbody>
              {positions.map((position) => (
                <tr key={position.id} className="border-b">
                  <td className="p-2">{position.token}</td>
                  <td className="p-2">{position.type}</td>
                  <td className="p-2">{position.amount.toFixed(2)}</td>
                  <td className="p-2">${position.entryPrice.toFixed(2)}</td>
                  <td className="p-2">${position.currentPrice.toFixed(2)}</td>
                  <td className={`p-2 ${position.profitLoss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {position.profitLoss.toFixed(2)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default LightweightPositionsWidget;
