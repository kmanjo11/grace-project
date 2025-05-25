// src/ui/pages/Trading.tsx
import React, { useEffect, useState, useCallback, useMemo, useRef } from 'react';
import { useAuth } from '../components/AuthContext';
import { useAppState } from '../context/AppStateContext';
import MangoV3Service, { MarketData } from '../../services/mangoV3Service';
import { Trade, TradeExecutionResult } from '../api/apiTypes';
import { api, API_ENDPOINTS, ApiError, TradingApi } from '../api/apiClient';
import PriceChart from '../components/PriceChart';
import ErrorBoundary from '../components/ErrorBoundary';
import { toast } from 'react-toastify';
import { tradingEventBus } from '../components/LightweightPositionsWidget';
import { debounce } from 'lodash';

// Constants
const DEFAULT_LEVERAGE = 5;
const DEFAULT_STOP_LOSS = 5;
const DEFAULT_TAKE_PROFIT = 10;

// Types
type TradingState = {
  tokens: MarketData[];
  selectedToken: MarketData | null;
  transactions: Trade[];  // Changed from UITrade to Trade
  isLoading: {
    tokens: boolean;
    transactions: boolean;
    trading: boolean;
  };
  error: string | null;
  resolution: string;
  search: string;
  tradeForm: {  // Defined inline instead of using TradeForm
    amount: string;
    leverage: number;
    isLeverage: boolean;
    isSmartTrade: boolean;
    stopLoss: number;
    takeProfit: number;
    orderType: 'market' | 'limit'; // Type of order: market or limit
    limitPrice: string; // Price for limit orders
  };
};
// Initial state
const initialState: TradingState = {
  tokens: [],
  selectedToken: null,
  transactions: [],
  isLoading: {
    tokens: true,
    transactions: false,
    trading: false,
  },
  error: null,
  resolution: '1h',
  search: '',
  tradeForm: {
    amount: '',
    leverage: DEFAULT_LEVERAGE,
    isLeverage: false,
    isSmartTrade: false,
    stopLoss: DEFAULT_STOP_LOSS,
    takeProfit: DEFAULT_TAKE_PROFIT,
    orderType: 'market', // Default to market orders
    limitPrice: '',
  },
};

// Process Mango token data with validation to create proper MarketData objects
const processMangoToken = (token: any): MarketData | null => {
  try {
    if (!token || typeof token !== 'object') {
      console.warn('Invalid token data:', token);
      return null;
    }
    
    // Ensure required fields are present
    const address = String(token.address || token.mintAddress || '').toLowerCase().trim();
    if (!address) {
      console.warn('Token missing address:', token);
      return null;
    }
    
    // Extract basic token data
    const baseCurrency = String(token.baseCurrency || token.symbol || '').toUpperCase().trim();
    const quoteCurrency = String(token.quoteCurrency || 'USDC').toUpperCase().trim();
    
    // Create a name using the market pattern if available, otherwise use the base currency
    const name = token.name || `${baseCurrency}-${quoteCurrency}`;
    
    // Use provided price or default to 0 if not available or invalid
    const price = typeof token.price === 'number' && !isNaN(token.price) ? token.price : 0;
    
    // Create a MarketData object with only the properties defined in the interface
    const marketData: MarketData = {
      name: name,
      address: address,
      baseCurrency: baseCurrency,
      quoteCurrency: quoteCurrency,
      price: price,
      marketId: token.marketId || ''
    };
    
    // Add optional properties if available
    if (token.symbol) marketData.symbol = token.symbol.toUpperCase().trim();
    if (token.logoURI) marketData.logoURI = token.logoURI;
    if (token.decimals !== undefined) marketData.decimals = token.decimals;
    
    // Store any additional data in the marketData object using its index signature
    // This ensures compatibility while preserving extra information
    marketData['source'] = 'mango';
    marketData['canTrade'] = true;
    marketData['canChart'] = true;
    
    return marketData;
  } catch (error) {
    console.error('Error processing token:', error, token);
    return null;
  }
};

const Trading: React.FC = () => {
  const { user } = useAuth();
  // Get access to the app state for persistence
  const { state: appState, dispatch } = useAppState();
  
  // Initialize state with saved values from appState if available
  const savedTradingState = appState.tradingState || {};
  const [state, setState] = useState<TradingState>({
    ...initialState,
    // Restore any saved values
    selectedToken: savedTradingState.selectedToken || initialState.selectedToken,
    resolution: savedTradingState.resolution || initialState.resolution,
    search: savedTradingState.search || initialState.search,
    tradeForm: {
      ...initialState.tradeForm,
      ...(savedTradingState.tradeForm || {})
    }
  });
  
  const abortController = useRef<AbortController | null>(null);

  // Save state to global persistence whenever it changes
  useEffect(() => {
    // Don't update during initial load
    if (state.tokens.length > 0 || state.selectedToken) {
      // Save to global app state
      dispatch({
        type: 'SET_TRADING_STATE',
        payload: {
          selectedToken: state.selectedToken,
          resolution: state.resolution,
          search: state.search,
          tradeForm: state.tradeForm,
          // Save positions in a compatible format for persistence
          positions: state.selectedToken ? [state.selectedToken] : []
        }
      });
    }
  }, [state.selectedToken, state.resolution, state.search, state.tradeForm, dispatch]);

  // Action creators with type safety
  const actions = useMemo(() => ({
    setTokens: (tokens: MarketData[]) => {
      console.log('Setting tokens:', tokens);
      setState(prev => ({ ...prev, tokens }));
    },
    selectToken: (token: MarketData | null) => {
      console.log('Selecting token:', token?.name);
      setState(prev => ({ ...prev, selectedToken: token }));
    },
    setTransactions: (transactions: Trade[]) => {
      setState(prev => ({ ...prev, transactions }));
    },
    setLoading: (loading: Partial<TradingState['isLoading']>) => {
      setState(prev => ({
        ...prev,
        isLoading: { ...prev.isLoading, ...loading }
      }));
    },
    setError: (error: string | null) => {
      console.error('Trading error:', error);
      setState(prev => ({
        ...prev,
        error,
        isLoading: { ...prev.isLoading, tokens: false, trading: false }
      }));
      if (error) {
        toast.error(error);
      }
    },
    setResolution: (resolution: string) => {
      console.log('Setting resolution:', resolution);
      setState(prev => ({
        ...prev,
        resolution,
        isLoading: { ...prev.isLoading, trading: true }
      }));
    },
    setSearch: (search: string) => {
      setState(prev => ({ ...prev, search }));
    },
    updateTradeForm: (form: Partial<TradingState['tradeForm']>) => {
      setState(prev => ({
        ...prev,
        tradeForm: { ...prev.tradeForm, ...form }
      }));
    },
    toggleLeverage: () => {
      setState(prev => ({
        ...prev,
        tradeForm: {
          ...prev.tradeForm,
          isLeverage: !prev.tradeForm.isLeverage,
          leverage: !prev.tradeForm.isLeverage ? DEFAULT_LEVERAGE : 1,
        },
      }));
    },
    toggleSmartTrade: () => {
      setState(prev => ({
        ...prev,
        tradeForm: {
          ...prev.tradeForm,
          isSmartTrade: !prev.tradeForm.isSmartTrade,
        },
      }));
    },
    toggleOrderType: () => {
      setState(prev => ({
        ...prev,
        tradeForm: {
          ...prev.tradeForm,
          orderType: prev.tradeForm.orderType === 'market' ? 'limit' : 'market',
          // Reset limitPrice when switching back to market order
          limitPrice: prev.tradeForm.orderType === 'limit' ? prev.tradeForm.limitPrice : '',
        },
      }));
    },
  }), []);

  // Show trade confirmation dialog
  const showTradeConfirmation = async (details: {
    token: string;
    action: string;
    amount: string;
    price?: number;
    total?: number;
    stopLoss?: number;
    takeProfit?: number;
  }): Promise<boolean> => {
    // Format numbers for display
    const formatNumber = (num?: number) => {
      if (num === undefined) return 'N/A';
      return num.toLocaleString(undefined, { maximumFractionDigits: 6 });
    };
    
    // Build confirmation message
    const message = `
      Please confirm your trade:
      
      ${details.action.toUpperCase()} ${details.amount} ${details.token}
      Price: $${formatNumber(details.price)}
      Total: $${formatNumber(details.total)}
      ${details.stopLoss ? `Stop Loss: $${formatNumber(details.stopLoss)}` : ''}
      ${details.takeProfit ? `Take Profit: $${formatNumber(details.takeProfit)}` : ''}
    `;
    
    // Use built-in browser confirmation
    return window.confirm(message);
  };

  // Execute a trade (buy/sell)
  const executeTrade = useCallback(async (side: 'buy' | 'sell') => {
    if (!state.selectedToken || !state.tradeForm.amount) {
      toast.error('Please select a token and enter an amount');
      return;
    }

    // For limit orders, validate limit price
    if (state.tradeForm.orderType === 'limit' && !state.tradeForm.limitPrice) {
      toast.error('Please enter a limit price');
      return;
    }

    try {
      actions.setLoading({ trading: true });
      
      if (state.tradeForm.orderType === 'limit') {
        // Handle limit order placement
        const limitOrderData = {
          market: state.selectedToken.symbol,
          side: side,
          price: parseFloat(state.tradeForm.limitPrice),
          size: parseFloat(state.tradeForm.amount),
          trade_type: state.tradeForm.isLeverage ? 'leverage' : 'spot',
          leverage: state.tradeForm.isLeverage ? state.tradeForm.leverage : undefined,
          reduce_only: false,
          client_id: `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`
        };

        try {
          // Call the limit orders API endpoint
          const response = await api.post(API_ENDPOINTS.USER.LIMIT_ORDERS, limitOrderData);
          
          if (response.success) {
            toast.success(`${side.toUpperCase()} limit order placed successfully at $${state.tradeForm.limitPrice}`);
            // Emit trade confirmed event for position widgets to update
            tradingEventBus.emit('trade:confirmed', {
              type: 'limit_order_placed',
              data: response,
              trade: {
                action: side,
                token: state.selectedToken.symbol,
                amount: state.tradeForm.amount,
                price: state.tradeForm.limitPrice,
                isLeverage: state.tradeForm.isLeverage,
                timestamp: Date.now()
              }
            });
          } else {
            throw new Error(response.error || 'Failed to place limit order');
          }
        } catch (error: any) {
          console.error('Limit order placement error:', error);
          toast.error(`Limit order failed: ${error.message || 'Unknown error'}`);
        }
      } else {
        // Handle market order (existing functionality)
        const tradeData = {
          action: side,
          token: state.selectedToken.symbol,
          amount: state.tradeForm.amount,
          isLeverage: state.tradeForm.isLeverage,
          leverage: state.tradeForm.isLeverage ? state.tradeForm.leverage : undefined,
          stopLoss: state.tradeForm.stopLoss,
          takeProfit: state.tradeForm.takeProfit,
          isSmartTrade: state.tradeForm.isSmartTrade
        };

        // Step 1: Execute trade (gets confirmation request)
        const tradeResult = await TradingApi.executeTrade(tradeData);
        
        // Step 2: If confirmation is required, handle it
        if (tradeResult.result?.status === 'confirmation_required' && 
            tradeResult.result.confirmation_id) {
          
          // Show confirmation dialog to user
          const confirmDetails = {
            token: state.selectedToken.symbol,
            action: side,
            amount: state.tradeForm.amount,
            price: tradeResult.result.current_price,
            total: tradeResult.result.estimated_total,
            stopLoss: tradeResult.result.stop_loss_price,
            takeProfit: tradeResult.result.take_profit_price
          };
          
          // Ask user to confirm
          const userConfirmed = await showTradeConfirmation(confirmDetails);
          
          if (userConfirmed) {
            // Execute confirmation
            const confirmResult = await TradingApi.confirmTrade(
              tradeResult.result.confirmation_id
            );
            
            if (confirmResult.success) {
              toast.success(`${side.toUpperCase()} order executed successfully`);
              // Emit trade confirmed event for position widgets to update
              tradingEventBus.emit('trade:confirmed', {
                type: 'trade_confirmed',
                data: confirmResult,
                trade: {
                  action: side,
                  token: state.selectedToken.symbol,
                  amount: state.tradeForm.amount,
                  isLeverage: state.tradeForm.isLeverage,
                  timestamp: Date.now()
                }
              });
            } else {
              throw new Error(confirmResult.error || 'Trade confirmation failed');
            }
          } else {
            toast.info('Trade canceled by user');
            return; // User canceled
          }
        } else if (tradeResult.success) {
          // Trade executed immediately
          toast.success(`${side === 'buy' ? 'Buy' : 'Sell'} order placed successfully`);
        } else {
          // Trade failed
          throw new Error(tradeResult.error || 'Failed to execute trade');
        }
      }
    } catch (error: any) {
      console.error('Trade execution error:', error);
      toast.error(`Trade failed: ${error.message || 'Unknown error'}`);
    } finally {
      actions.setLoading({ trading: false });
    }
  }, [state.selectedToken, state.tradeForm, actions]);

  // Handle token selection with data loading
  const handleTokenSelect = useCallback(async (token: MarketData) => {
    if (!token?.address) {
      const errorMsg = 'Invalid token: Missing address';
      console.error(errorMsg, token);
      actions.setError(errorMsg);
      return;
    }
    
    console.log(`Selected token: ${token.name} (${token.address})`);
    
    // Update UI state
    actions.selectToken(token);
    actions.setSearch('');
    actions.setTokens([]);
    actions.updateTradeForm({ amount: '' });
    actions.setLoading({ trading: true });
    
    try {
      // Calculate time range (last 24 hours in seconds)
      const endTime = Math.floor(Date.now() / 1000);
      const startTime = endTime - (24 * 60 * 60);
      
      console.log(`Fetching OHLCV data for ${token.symbol} (${token.address})`);
      console.log(`- Resolution: ${state.resolution || '1h'}`);
      console.log(`- Time range: ${new Date(startTime * 1000).toISOString()} to ${new Date(endTime * 1000).toISOString()}`);
      
      // Load token price data - use market name for OHLCV request, not address
      // Per Mango V3 API: /api/markets/{market_name}/candles
      const marketName = token.name || `${token.baseCurrency}-${token.quoteCurrency}` || token.address;
      console.log(`Using market name for OHLCV request: ${marketName}`);
      
      const priceData = await MangoV3Service.getOHLCV(
        marketName,
        state.resolution || '1h',
        startTime,
        endTime
      );
      
      console.log(`Received ${priceData.length} data points`);
      
      if (!priceData || priceData.length === 0) {
        throw new Error('No price data available for this token');
      }
      
      // Update token with latest price and additional market data
      const latestData = priceData[priceData.length - 1];
      const updatedToken = {
        ...token,
        price: latestData.close,
        change_24h: ((latestData.close - priceData[0].open) / priceData[0].open) * 100,
        volume_24h: priceData.reduce((sum, data) => sum + (data.volume || 0), 0)
      };
      
      console.log(`Updated token data:`, {
        price: updatedToken.price,
        change_24h: updatedToken.change_24h,
        volume_24h: updatedToken.volume_24h
      });
      
      actions.selectToken(updatedToken);
      
    } catch (error) {
      const errorMsg = error instanceof Error ? 
        `Failed to load token data: ${error.message}` : 
        'Failed to load token data';
        
      console.error(errorMsg, error);
      actions.setError(errorMsg);
    } finally {
      actions.setLoading({ trading: false });
    }
  }, [state.resolution, actions]);

  // Handle resolution change with validation
  const handleResolutionChange = useCallback((newResolution: string) => {
    try {
      // Validate the resolution format
      if (!/^\d+[mhd]$/.test(newResolution)) {
        throw new Error('Invalid resolution format. Use format like 1m, 5m, 1h, etc.');
      }
      
      // Test the resolution by making a small API call
      // This will throw if the resolution is invalid
      MangoV3Service.getOHLCV('SOL-PERP', newResolution)
        .then(() => {
          console.log(`Valid resolution: ${newResolution}`);
          // Update the resolution in state
          actions.setResolution(newResolution);
          
          // Trigger a refetch of the chart data if a token is selected
          if (state.selectedToken) {
            actions.setLoading({ trading: true });
          }
        })
        .catch(error => {
          console.error('Invalid resolution:', error);
          actions.setError('This resolution is not supported');
        });
    } catch (error) {
      console.error('Resolution validation error:', error);
      actions.setError(error instanceof Error ? error.message : 'Invalid resolution');
    }
  }, [actions, state.selectedToken]);
  
  // Get available resolutions from MangoV3Service
  const availableResolutions = useMemo(() => ({
    '1m': '1 minute',
    '5m': '5 minutes',
    '15m': '15 minutes',
    '1h': '1 hour',
    '4h': '4 hours',
    '1d': '1 day'
  }), []);

  // Fetch transaction history for the current user
  const fetchTransactions = useCallback(async () => {
    if (!user) return;
    
    try {
      actions.setLoading({ transactions: true });
      const response = await api.get(`${API_ENDPOINTS.MANGO.TRADES}?limit=10`);
      
      if (response && Array.isArray(response.data)) {
        actions.setTransactions(response.data);
      } else {
        console.warn('Invalid transaction data format:', response);
        actions.setTransactions([]);
      }
    } catch (error) {
      console.error('Error fetching transactions:', error);
      actions.setTransactions([]);
    } finally {
      actions.setLoading({ transactions: false });
    }
  }, [user, actions]);
  
  // Fetch detailed token information
  const fetchTokenInfo = useCallback(async (symbol: string) => {
    if (!symbol) return null;
    
    try {
      const response = await api.get(`${API_ENDPOINTS.TRADING.TOKENS}/${symbol}`);
      if (response && response.data) {
        const processedToken = processMangoToken(response.data);
        if (processedToken) {
          // Update the selected token with fresh data
          actions.selectToken(processedToken);
          return processedToken;
        }
      }
      return null;
    } catch (error) {
      console.error(`Error fetching token info for ${symbol}:`, error);
      return null;
    }
  }, [actions]);

  // Hook into trading events
  useEffect(() => {
    // Listen for trade confirmation events to refresh data
    const handleTradeConfirmed = (event: any) => {
      console.log('Trade confirmed event received:', event);
      // Refresh transactions
      fetchTransactions();
      // Refresh token data if needed
      if (state.selectedToken && event.trade && event.trade.token === state.selectedToken.symbol) {
        fetchTokenInfo(state.selectedToken.symbol);
      }
    };
    
    tradingEventBus.on('trade:confirmed', handleTradeConfirmed);
    
    return () => {
      tradingEventBus.off('trade:confirmed', handleTradeConfirmed);
    };
  }, [state.selectedToken, fetchTransactions, fetchTokenInfo]);

  // Fetch tokens with debounce
  const fetchTokens = useCallback(
    debounce(async (query: string) => {
      const searchQuery = query.trim();
      console.log('Searching for tokens with query:', searchQuery);
      
      if (!searchQuery) {
        console.log('Empty search query, clearing tokens');
        actions.setTokens([]);
        return;
      }

      // Cancel any pending requests
      if (abortController.current) {
        console.log('Cancelling previous search request');
        abortController.current.abort();
      }
      
      abortController.current = new AbortController();
      actions.setLoading({ tokens: true });

      try {
        console.log('Fetching tokens from Mango V3 API...');
        // Use empty string to get all markets when search is 3+ characters
        // This ensures we search through all available tokens
        const response = await MangoV3Service.searchMarkets(
          searchQuery.length >= 3 ? searchQuery : ''
        );
        console.log(`Received ${response.length} tokens from API`);
        
        // Process all tokens
        const allTokens = response
          .map(processMangoToken)
          .filter((token): token is MarketData => token !== null);
        
        // If search query is present, filter on client side for more flexible matching
        const tokens = searchQuery.length >= 3 
          ? allTokens.filter(token => {
              const query = searchQuery.toLowerCase();
              return (
                token.symbol.toLowerCase().includes(query) ||
                token.name.toLowerCase().includes(query) ||
                token.baseCurrency?.toLowerCase().includes(query) ||
                token.quoteCurrency?.toLowerCase().includes(query) ||
                token.address?.toLowerCase().includes(query)
              );
            })
          : allTokens;
        
        console.log(`Displaying ${tokens.length} tokens after filtering`);
        actions.setTokens(tokens);
        actions.setError(null);
      } catch (error) {
        if (error.name === 'AbortError') {
          console.log('Search was cancelled');
          return;
        }
        
        console.error('Error fetching tokens:', error);
        const errorMessage = error instanceof Error ? error.message : 'Failed to fetch tokens';
        actions.setError(errorMessage);
      } finally {
        actions.setLoading({ tokens: false });
      }
    }, 300),
    []
  );

  // Handle search input change
  const handleSearchChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    actions.setSearch(value);
    
    // Only fetch tokens if search is empty (to clear) or has at least 3 characters
    if (value === '' || value.length >= 3) {
      fetchTokens(value);
    }
  }, [fetchTokens, actions]);

  // Fetch wallet balances
  const [walletBalances, setWalletBalances] = useState<{
    balances: { [key: string]: number };
    loading: boolean;
    error: string | null;
  }>({
    balances: {},
    loading: false,
    error: null
  });

  // Fetch wallet balances
  const fetchWalletBalances = useCallback(async () => {
    if (!user) return;
    
    try {
      setWalletBalances(prev => ({ ...prev, loading: true, error: null }));
      
      const response = await api.get(API_ENDPOINTS.WALLET.BALANCE);
      
      if (response.success && response.data) {
        const balanceData = response.data;
        const formattedBalances: { [key: string]: number } = {};
        
        // Format balances to a usable format
        if (Array.isArray(balanceData.tokens)) {
          balanceData.tokens.forEach((token: any) => {
            if (token.symbol && typeof token.amount === 'number') {
              formattedBalances[token.symbol.toUpperCase()] = token.amount;
            }
          });
        }
        
        console.log('Wallet balances loaded:', formattedBalances);
        setWalletBalances({
          balances: formattedBalances,
          loading: false,
          error: null
        });
      } else {
        throw new Error(response.error || 'Failed to load wallet balances');
      }
    } catch (error) {
      console.error('Error fetching wallet balances:', error);
      setWalletBalances(prev => ({
        ...prev,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to load wallet balances'
      }));
    }
  }, [user]);

  // Initial data fetch
  useEffect(() => {
    // Load initial tokens
    fetchTokens('');
    
    // Cleanup function to abort any pending requests
    return () => {
      if (abortController.current) {
        abortController.current.abort();
      }
    };
  }, [fetchTokens]);

  // Render token list
  const renderTokenList = () => (
    <div className="bg-gray-900 rounded-lg p-4 h-full">
      <div className="mb-4">
        <input
          type="text"
          placeholder="Search tokens..."
          className="w-full p-2 bg-gray-800 text-white rounded"
          value={state.search}
          onChange={handleSearchChange}
        />
      </div>
      <div className="space-y-2 max-h-[500px] overflow-y-auto">
        {state.tokens.map((token) => (
          <div
            key={token.address}
            className={`p-3 rounded-lg cursor-pointer hover:bg-gray-800 ${
              state.selectedToken?.address === token.address ? 'bg-blue-900' : 'bg-gray-800'
            }`}
            onClick={() => handleTokenSelect(token)}
          >
            <div className="flex justify-between items-center">
              <div>
                <div className="font-medium">{token.symbol}</div>
                <div className="text-sm text-gray-400">{token.name}</div>
                {/* Show trading pair information clearly */}
                {token.baseCurrency && token.quoteCurrency && (
                  <div className="text-xs text-blue-400 mt-1">
                    {token.baseCurrency}/{token.quoteCurrency}
                  </div>
                )}
              </div>
              <div className="text-right">
                <div>${token.price?.toFixed(6) || 'N/A'}</div>
                <div className={`text-sm ${
                  (token.change_24h || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                }`}>
                  {token.change_24h ? `${token.change_24h.toFixed(2)}%` : 'N/A'}
                </div>
              </div>
            </div>
          </div>
        ))}
        
        {state.isLoading.tokens && (
          <div className="text-center py-4">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
          </div>
        )}
        
        {!state.isLoading.tokens && state.tokens.length === 0 && state.search && (
          <div className="text-center py-4 text-gray-400">
            No tokens found
          </div>
        )}
      </div>
    </div>
  );

  // Check if user has enough balance for the trade
  const checkWalletBalance = useCallback((token: string, amount: string): boolean => {
    if (!amount || isNaN(parseFloat(amount))) return true; // Don't show error if amount is empty
    
    // Find the token in wallet balances
    const tokenSymbol = token.toUpperCase();
    const balance = walletBalances.balances[tokenSymbol] || 0;
    
    return parseFloat(amount) <= balance;
  }, [walletBalances.balances]);
  
  // Render wallet balances section
  const renderWalletBalances = () => {
    const relevantBalances = Object.entries(walletBalances.balances)
      .filter(([symbol]) => {
        // Show all balances, but prioritize the selected token if available
        if (state.selectedToken && state.selectedToken.symbol === symbol) return true;
        // Only show non-zero balances or top 3 tokens
        return true;
      })
      .sort((a, b) => b[1] - a[1]) // Sort by balance value, highest first
      .slice(0, 5); // Show top 5 balances
    
    return (
      <div className="mb-4 p-3 bg-gray-800 rounded-lg">
        <h3 className="text-sm font-medium text-gray-400 mb-2">Wallet Balances</h3>
        
        {walletBalances.loading ? (
          <div className="text-center py-1">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500 mx-auto"></div>
          </div>
        ) : walletBalances.error ? (
          <div className="text-xs text-red-400">{walletBalances.error}</div>
        ) : relevantBalances.length > 0 ? (
          <div className="space-y-1">
            {relevantBalances.map(([symbol, amount]) => (
              <div key={symbol} className="flex justify-between items-center">
                <span className="text-sm font-medium">{symbol}</span>
                <span className="text-sm text-gray-300">{amount.toFixed(6)}</span>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-xs text-gray-500">No balances available</div>
        )}
      </div>
    );
  };

  // Render trading form
  const renderTradingForm = () => (
    <div className="bg-gray-900 rounded-lg p-4">
      {state.selectedToken ? (
        <>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold">
              {state.selectedToken.symbol}
              <span className="ml-2 text-sm text-gray-400">
                ${state.selectedToken.price?.toFixed(6) || 'N/A'}
              </span>
            </h2>
            <div className={`text-sm ${
              (state.selectedToken.change_24h || 0) >= 0 ? 'text-green-400' : 'text-red-400'
            }`}>
              {state.selectedToken.change_24h ? `${state.selectedToken.change_24h.toFixed(2)}%` : 'N/A'}
            </div>
          </div>
          
          <div className="space-y-4">
            {/* Show wallet balances above the trading form */}
            {renderWalletBalances()}
            
            {/* Order Type Toggle (Market/Limit) */}
            <div className="flex items-center justify-between bg-gray-800 rounded p-2">
              <div className="text-sm text-gray-400">Order Type:</div>
              <div className="flex bg-gray-700 rounded overflow-hidden">
                <button
                  className={`px-3 py-1 text-sm ${state.tradeForm.orderType === 'market' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}`}
                  onClick={() => state.tradeForm.orderType !== 'market' && actions.toggleOrderType()}
                >
                  Market
                </button>
                <button
                  className={`px-3 py-1 text-sm ${state.tradeForm.orderType === 'limit' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}`}
                  onClick={() => state.tradeForm.orderType !== 'limit' && actions.toggleOrderType()}
                >
                  Limit
                </button>
              </div>
            </div>
            
            <div>
              <label className="block text-sm text-gray-400 mb-1">Amount</label>
              <input
                type="number"
                className={`w-full p-2 ${state.selectedToken && !checkWalletBalance(state.selectedToken.symbol, state.tradeForm.amount) ? 'bg-red-900/30 border border-red-500' : 'bg-gray-800'} text-white rounded`}
                value={state.tradeForm.amount}
                onChange={(e) => actions.updateTradeForm({ amount: e.target.value })}
                placeholder="0.0"
              />
              {state.selectedToken && !checkWalletBalance(state.selectedToken.symbol, state.tradeForm.amount) && (
                <div className="text-xs text-red-400 mt-1">
                  Insufficient balance for {state.selectedToken.symbol}
                </div>
              )}
            </div>
            
            {/* Limit Price field - only shown for limit orders */}
            {state.tradeForm.orderType === 'limit' && (
              <div>
                <label className="block text-sm text-gray-400 mb-1">Limit Price ($)</label>
                <input
                  type="number"
                  className="w-full p-2 bg-gray-800 text-white rounded"
                  value={state.tradeForm.limitPrice}
                  onChange={(e) => actions.updateTradeForm({ limitPrice: e.target.value })}
                  placeholder={state.selectedToken?.price?.toFixed(6) || "0.0"}
                />
              </div>
            )}
            
            <div className="flex items-center justify-between">
              <button
                className={`px-3 py-1 rounded ${
                  state.tradeForm.isLeverage
                    ? 'bg-blue-600 hover:bg-blue-700'
                    : 'bg-gray-700 hover:bg-gray-600'
                }`}
                onClick={actions.toggleLeverage}
              >
                Leverage
              </button>
              
              {state.tradeForm.isLeverage && (
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-400">Amount:</span>
                  <input
                    type="number"
                    min="1"
                    max="20"
                    className="w-16 p-1 bg-gray-800 text-white rounded text-center"
                    value={state.tradeForm.leverage}
                    onChange={(e) => 
                      actions.updateTradeForm({ 
                        leverage: Math.min(20, Math.max(1, Number(e.target.value) || 1)) 
                      })
                    }
                  />
                  <span className="text-sm">x</span>
                </div>
              )}
              
              <button
                className={`px-3 py-1 rounded ${
                  state.tradeForm.isSmartTrade
                    ? 'bg-blue-600 hover:bg-blue-700'
                    : 'bg-gray-700 hover:bg-gray-600'
                }`}
                onClick={actions.toggleSmartTrade}
              >
                Smart Trade
              </button>
            </div>
            
            {state.tradeForm.isSmartTrade && (
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Stop Loss (%)</label>
                  <input
                    type="number"
                    min="0"
                    step="0.1"
                    className="w-full p-2 bg-gray-800 text-white rounded"
                    value={state.tradeForm.stopLoss}
                    onChange={(e) => 
                      actions.updateTradeForm({ 
                        stopLoss: Math.max(0, Number(e.target.value) || 0) 
                      })
                    }
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Take Profit (%)</label>
                  <input
                    type="number"
                    min="0"
                    step="0.1"
                    className="w-full p-2 bg-gray-800 text-white rounded"
                    value={state.tradeForm.takeProfit}
                    onChange={(e) => 
                      actions.updateTradeForm({ 
                        takeProfit: Math.max(0, Number(e.target.value) || 0) 
                      })
                    }
                  />
                </div>
              </div>
            )}
            
            <div className="grid grid-cols-2 gap-4">
              <button
                className={`bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded ${state.isLoading.trading ? 'opacity-50 cursor-not-allowed' : ''}`}
                onClick={() => executeTrade('buy')}
                disabled={state.isLoading.trading}
              >
                {state.isLoading.trading ? 'Processing...' : 'Buy'}
              </button>
              <button
                className={`bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded ${state.isLoading.trading ? 'opacity-50 cursor-not-allowed' : ''}`}
                onClick={() => executeTrade('sell')}
                disabled={state.isLoading.trading}
              >
                {state.isLoading.trading ? 'Processing...' : 'Sell'}
              </button>
            </div>
          </div>
        </>
      ) : (
        <div className="text-center py-8 text-gray-400">
          Select a token to start trading
        </div>
      )}
    </div>
  );

  // Render price chart
  const renderPriceChart = () => (
    <div className="bg-gray-900 rounded-lg p-4 h-full">
      {state.selectedToken ? (
        <div className="h-full flex flex-col">
          <div className="flex justify-between items-center mb-2">
            <h3 className="text-lg font-medium">Price Chart</h3>
            <div className="flex space-x-2">
              {Object.entries(availableResolutions).map(([res, label]) => (
                <button
                  key={res}
                  className={`px-2 py-1 text-sm rounded ${
                    state.resolution === res
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                  }`}
                  onClick={() => handleResolutionChange(res)}
                >
                  {res}
                </button>
              ))}
            </div>
          </div>
          
          <div className="flex-1 min-h-[300px]">
            <PriceChart
              tokenAddress={state.selectedToken.address}
              selectedToken={state.selectedToken}
              resolution={state.resolution}
              onError={actions.setError}
              onLoading={(loading) => actions.setLoading({ trading: loading })}
              onResolutionChange={handleResolutionChange}
              onTokenSelect={handleTokenSelect}
            />
          </div>
        </div>
      ) : (
        <div className="flex items-center justify-center h-full text-gray-400">
          Select a token to view chart
        </div>
      )}
    </div>
  );

  // Render transaction history with proper type safety and fallbacks
  const renderTransactionHistory = () => {
    // Ensure we have transactions to display
    const transactions = Array.isArray(state.transactions) ? state.transactions : [];
    
    return (
      <div className="bg-gray-900 rounded-lg p-4 h-full">
        <h3 className="text-lg font-medium mb-4">Recent Trades</h3>
        
        {state.isLoading.transactions ? (
          <div className="text-center py-4">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
          </div>
        ) : transactions.length > 0 ? (
          <div className="space-y-2">
            {transactions.map((tx: any, index: number) => {
              // Safely extract transaction data with fallbacks
              const side = tx?.side?.toLowerCase() === 'sell' ? 'sell' : 'buy';
              const symbol = tx?.symbol || 'TOKEN';
              const amount = tx?.amount ? Number(tx.amount).toFixed(4) : '0';
              const price = tx?.price ? `$${Number(tx.price).toFixed(6)}` : '$0';
              const timestamp = tx?.timestamp ? new Date(tx.timestamp).toLocaleString() : 'Just now';
              
              return (
                <div key={index} className="flex justify-between items-center p-2 bg-gray-800 rounded">
                  <div className="flex items-center">
                    <div className={`w-3 h-3 rounded-full mr-2 ${
                      side === 'buy' ? 'bg-green-500' : 'bg-red-500'
                    }`}></div>
                    <span className="font-medium">{symbol}</span>
                  </div>
                  <div className="text-right">
                    <div className={side === 'buy' ? 'text-green-400' : 'text-red-400'}>
                      {side.toUpperCase()} {amount} @ {price}
                    </div>
                    <div className="text-xs text-gray-400">
                      {timestamp}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-400">
            No recent trades found
          </div>
        )}
      </div>
    );
  };

  return (
    <ErrorBoundary>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-6">Trading</h1>
        
        {state.error && (
          <div className="bg-red-900/50 border border-red-500 text-white px-4 py-3 rounded mb-4">
            {state.error}
          </div>
        )}
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="lg:col-span-1">
            {renderTokenList()}
          </div>
          <div className="lg:col-span-2">
            {renderTradingForm()}
          </div>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            {renderPriceChart()}
          </div>
          <div className="lg:col-span-1">
            {renderTransactionHistory()}
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
};

// Define props for the TradingPage component
interface TradingPageProps {}

const TradingPage: React.FC<TradingPageProps> = () => {
  return (
    <ErrorBoundary>
      <Trading />
    </ErrorBoundary>
  );
};

export default TradingPage;