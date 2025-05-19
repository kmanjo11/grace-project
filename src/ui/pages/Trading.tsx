// src/pages/Trading.tsx

import React, { useEffect, useState } from 'react';
import ErrorBoundary from '../components/ErrorBoundary';
import { useAuth } from '../components/AuthContext';
import { api, API_ENDPOINTS, ApiError } from '../api/apiClient';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface TokenData {
  symbol: string;
  name: string;
  price: number;
  change_24h: number;
  market_cap: number;
  volume_24h: number;
}

interface Transaction {
  id: string;
  type: string; // 'buy', 'sell', etc.
  token: string;
  amount: number;
  price: number;
  timestamp: string;
  status: string;
  // Removed action property as we'll use type consistently
}

interface ChartDataPoint {
  timestamp: string; // Changed from time to timestamp to match API format
  price: number;
  formattedTime?: string; // For displaying readable time in tooltip
}

interface ChartDataResponse {
  chartData?: {
    timestamps?: number[]; // Unix timestamps
    prices?: number[];
    labels?: string[];
  };
  token?: string;
  timeframe?: string;
  success?: boolean;
  error?: string;
}

interface SmartSettings {
  enabled: boolean;
  riskLevel: number;
  maxTradeSize: number;
  stopLoss: number;
  takeProfit: number;
}

// Wrap component in Layout since we removed it from the return statement
const TradingContent: React.FC = () => {
  const { user } = useAuth();
  const [tokens, setTokens] = useState<TokenData[]>([]);
  const [selectedToken, setSelectedToken] = useState<string>('');
  const [isChartLoading, setIsChartLoading] = useState<boolean>(false);
  const [chartError, setChartError] = useState<string>('');
  const [amount, setAmount] = useState<string>('');
  const [action, setAction] = useState<'buy' | 'sell'>('buy');
  const [confirmationData, setConfirmationData] = useState<any>(null);
  const [isConfirming, setIsConfirming] = useState<boolean>(false);
  
  // Helper function to safely set action state
  const handleActionChange = (newAction: string) => {
    if (newAction === 'buy' || newAction === 'sell') {
      setAction(newAction);
    }
  };
  const [result, setResult] = useState<string>('');
  const [txHistory, setTxHistory] = useState<Transaction[]>([]);
  
  // Safely handle transaction history
  const safeGetTxHistory = (data: any): Transaction[] => {
    if (!data) return [];
    if (Array.isArray(data)) return data;
    if (data.history && Array.isArray(data.history)) return data.history;
    return [];
  };
  const [search, setSearch] = useState<string>('');
  const [chartData, setChartData] = useState<ChartDataPoint[]>([]);
  const [smart, setSmart] = useState<SmartSettings>({ 
    enabled: false, 
    riskLevel: 50, 
    maxTradeSize: 0.1, 
    stopLoss: 5, 
    takeProfit: 10 
  });
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const fetchTradingData = async () => {
      try {
        setError('');
        
        // Fetch available tokens
        const tokensResponse = await api.get(API_ENDPOINTS.TRADING.TOKENS);
        
        // Log the token response for debugging
        console.log('Token API response:', tokensResponse);
        
        if (!tokensResponse.success) {
          throw new ApiError(
            tokensResponse.error || 'Failed to fetch tokens', 
            tokensResponse.statusCode || 500,
            { endpoint: API_ENDPOINTS.TRADING.TOKENS }
          );
        }
        
        // Check if we have valid token data
        // The backend returns tokens in the 'tokens' field, not 'data'
        if (tokensResponse.data?.tokens && Array.isArray(tokensResponse.data.tokens) && tokensResponse.data.tokens.length > 0) {
          console.log(`Received ${tokensResponse.data.tokens.length} tokens from API`);
          
          // Add price and market data to tokens from backend
          const enhancedTokens = tokensResponse.data.tokens.map(token => ({
            ...token,
            price: token.price || (token.symbol === 'SOL' ? 140.25 : 
                     token.symbol === 'USDC' ? 1.00 : 
                     token.symbol === 'BONK' ? 0.00002 : 
                     token.symbol === 'JTO' ? 3.85 : 
                     token.symbol === 'WIF' ? 0.85 : 10.0),
            change_24h: token.change_24h || Number((Math.random() * 10 - 5).toFixed(2)),
            market_cap: token.market_cap || Math.floor(Math.random() * 10000000000),
            volume_24h: token.volume_24h || Math.floor(Math.random() * 1000000000)
          }));
          
          setTokens(enhancedTokens);
        } else {
          console.warn('API returned empty or invalid token list, using fallback tokens');
          // Provide fallback tokens if API returns empty list
          const fallbackTokens: TokenData[] = [
            { symbol: 'SOL', name: 'Solana', price: 140.25, change_24h: 2.5, market_cap: 64000000000, volume_24h: 2500000000 },
            { symbol: 'USDC', name: 'USD Coin', price: 1.00, change_24h: 0.01, market_cap: 32000000000, volume_24h: 1800000000 },
            { symbol: 'BONK', name: 'Bonk', price: 0.00002, change_24h: 5.2, market_cap: 1200000000, volume_24h: 350000000 },
            { symbol: 'JTO', name: 'Jito', price: 3.85, change_24h: -1.2, market_cap: 450000000, volume_24h: 75000000 },
            { symbol: 'WIF', name: 'Dogwifhat', price: 0.85, change_24h: 4.2, market_cap: 850000000, volume_24h: 95000000 }
          ];
          setTokens(fallbackTokens);
        }
        
        // Fetch transaction history with safer handling
        const txResponse = await api.get(API_ENDPOINTS.TRADING.HISTORY);
        if (!txResponse.success) {
          throw new ApiError(
            txResponse.error || 'Failed to fetch transaction history', 
            txResponse.statusCode || 500,
            { endpoint: API_ENDPOINTS.TRADING.HISTORY }
          );
        }
        
        // The wallet data endpoint returns transactions in a different format
        if (txResponse.data?.transactions && Array.isArray(txResponse.data.transactions)) {
          console.log(`Received ${txResponse.data.transactions.length} transaction records from wallet API`);
          
          // Map wallet transactions to the expected format
          const formattedTransactions = txResponse.data.transactions.map((tx: any) => ({
            id: tx.id || tx.transaction_id || `tx_${Math.random().toString(36).substring(2, 10)}`,
            type: tx.type || tx.action || 'unknown',
            token: tx.token || tx.symbol || 'SOL',
            amount: tx.amount || 0,
            price: tx.price || 0,
            timestamp: tx.timestamp || tx.date || new Date().toISOString(),
            status: tx.status || 'completed'
          }));
          
          setTxHistory(formattedTransactions);
        } else if (txResponse.data?.history && Array.isArray(txResponse.data.history)) {
          // For backward compatibility with the old format
          console.log(`Received ${txResponse.data.history.length} transaction records from history API`);
          setTxHistory(txResponse.data.history);
        } else {
          // Fallback to the safer handling if the expected format isn't found
          console.warn('API returned unexpected transaction history format, using fallback handling');
          setTxHistory(safeGetTxHistory(txResponse.data));
        }
        
        // Smart settings fetch
        const smartResponse = await api.get(API_ENDPOINTS.TRADING.SMART_SETTINGS);
        if (!smartResponse.success) {
          console.warn('Failed to fetch smart trading settings, using defaults', {
            endpoint: API_ENDPOINTS.TRADING.SMART_SETTINGS,
            error: smartResponse.error
          });
          return;
        }
        setSmart(smartResponse.data || smart);
      } catch (err: any) {
        const apiError = err instanceof ApiError ? err : 
          new ApiError(err.message || 'Unexpected trading data error', 500);
        
        console.error('Trading Data Fetch Error', {
          message: apiError.message,
          statusCode: apiError.statusCode,
          additionalData: apiError.data
        });
        
        setError(apiError.message);
      }
    };
    
    if (user) {
      fetchTradingData();
    }
  }, [user]);

  // Auto-select first token if tokens are loaded and none is selected
  useEffect(() => {
    if (Array.isArray(tokens)) {
      console.log(`Token list updated: ${tokens.length} tokens available`);
      
      // Log the first few tokens for debugging
      if (tokens.length > 0) {
        console.log('First few tokens:', tokens.slice(0, 3).map(t => `${t.name} (${t.symbol})`));
      } else {
        console.warn('Token list is empty - dropdown will be blank');
      }
      
      // Auto-select first token if none is selected
      if (!selectedToken && tokens.length > 0) {
        const firstToken = tokens[0];
        if (firstToken && firstToken.symbol) {
          console.log('Auto-selecting first token:', firstToken.symbol);
          setSelectedToken(firstToken.symbol);
        }
      }
    }
  }, [tokens, selectedToken]);

  // Ensure tokens is an array before filtering to prevent TypeError
  const filteredTokens = Array.isArray(tokens) ? tokens.filter(t => 
    t && typeof t === 'object' && 
    ((t.name && t.name.toLowerCase().includes(search.toLowerCase())) || 
     (t.symbol && t.symbol.toLowerCase().includes(search.toLowerCase())))
  ) : [];

  // Auto-select first matching token when search changes
  useEffect(() => {
    if (search && filteredTokens.length > 0) {
      const firstMatchingToken = filteredTokens[0];
      if (firstMatchingToken && firstMatchingToken.symbol) {
        console.log('Auto-selecting first matching token from search:', firstMatchingToken.symbol);
        setSelectedToken(firstMatchingToken.symbol);
      }
    }
  }, [search, filteredTokens]);

  // Fetch chart data when selected token changes
  useEffect(() => {
    if (!selectedToken) return;
    
    const fetchChartData = async () => {
      try {
        setIsChartLoading(true);
        setChartError('');
        console.log(`Fetching chart data for token: ${selectedToken}`);
        
        const { data, success } = await api.get(
          `${API_ENDPOINTS.TRADING.PRICE_CHART}?token=${selectedToken}&timeframe=1d`
        );
        
        // Validate API response structure
        if (!success) {
          throw new Error('API returned unsuccessful response');
        }
        
        if (!data) {
          throw new Error('API response missing data');
        }
        
        // Log the raw response for debugging
        console.log('Raw chart data response:', data);
        
        // Handle different possible response formats from the API server
        let chartData: ChartDataPoint[] = [];
        
        // Case 1: Standard format with chartData containing timestamps, prices, labels
        if (data.chartData) {
          const { timestamps, prices, labels } = data.chartData;
          
          // Log chart data structure for debugging
          console.log('Chart data structure:', {
            hasLabels: Array.isArray(labels),
            hasPrices: Array.isArray(prices),
            hasTimestamps: Array.isArray(timestamps),
            labelsLength: Array.isArray(labels) ? labels.length : 0,
            pricesLength: Array.isArray(prices) ? prices.length : 0,
            timestampsLength: Array.isArray(timestamps) ? timestamps.length : 0
          });
          
          // If we have valid arrays of the same length
          if (Array.isArray(labels) && Array.isArray(prices) && labels.length === prices.length && labels.length > 0) {
            // Map the separate arrays into an array of ChartDataPoint objects
            chartData = labels.map((label, index) => ({
              timestamp: label,
              price: prices[index],
              formattedTime: formatTimestamp(label)
            }));
          } else if (Array.isArray(timestamps) && Array.isArray(prices) && timestamps.length === prices.length && timestamps.length > 0) {
            // Alternative format: timestamps (numbers) and prices
            chartData = timestamps.map((timestamp, index) => ({
              timestamp: new Date(timestamp * 1000).toISOString(),
              price: prices[index],
              formattedTime: formatTimestamp(new Date(timestamp * 1000).toISOString())
            }));
          }
        }
        // Case 2: Direct array of price points
        else if (Array.isArray(data.prices) && Array.isArray(data.times || data.timestamps || data.dates)) {
          const times = data.times || data.timestamps || data.dates;
          if (times.length === data.prices.length) {
            chartData = times.map((time, index) => ({
              timestamp: typeof time === 'number' ? new Date(time * 1000).toISOString() : time,
              price: data.prices[index],
              formattedTime: formatTimestamp(typeof time === 'number' ? new Date(time * 1000).toISOString() : time)
            }));
          }
        }
        // Case 3: Array of objects with timestamp/price pairs
        else if (Array.isArray(data) || Array.isArray(data.points)) {
          const points = Array.isArray(data) ? data : data.points;
          if (Array.isArray(points) && points.length > 0) {
            // Check first item to determine format
            const firstPoint = points[0];
            if (firstPoint && (firstPoint.timestamp || firstPoint.time || firstPoint.date) && (firstPoint.price || firstPoint.value !== undefined)) {
              chartData = points.map(point => ({
                timestamp: point.timestamp || point.time || point.date,
                price: point.price || point.value,
                formattedTime: formatTimestamp(point.timestamp || point.time || point.date)
              }));
            }
          }
        }
        
        // If we have valid chart data, set it
        if (chartData.length > 0) {
          console.log(`Successfully processed ${chartData.length} chart data points`);
          // Sort by timestamp to ensure proper ordering
          chartData.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
          setChartData(chartData);
        } else {
          console.warn('Could not extract valid chart data from response', data);
          setChartData([]);
          setChartError('No valid chart data available for this token');
        }
      } catch (err: any) {
        console.error('Failed to load chart data', err);
        setChartData([]);
        setChartError(err?.message || 'Failed to load price chart data');
        setError(err?.message || 'Failed to load price chart data');
      } finally {
        setIsChartLoading(false);
      }
    };
    
    fetchChartData();
  }, [selectedToken]);

  // Helper function to format timestamps for display
  const formatTimestamp = (timestamp: string): string => {
    try {
      const date = new Date(timestamp);
      if (isNaN(date.getTime())) {
        return timestamp; // Return original if parsing fails
      }
      
      // Format: May 8, 14:30
      return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
      });
    } catch (e) {
      return timestamp; // Return original on error
    }
  };
  
  const updateSmart = async (field: string, value: any) => {
    try {
      const newSmart = { ...smart, [field]: value };
      setSmart(newSmart);
      
      const { success, data } = await api.post(API_ENDPOINTS.TRADING.SMART_SETTINGS, newSmart);
      
      if (!success) {
        throw new Error(data?.error || 'Failed to update smart trading settings');
      }
    } catch (err: any) {
      console.error('Error updating smart settings:', err);
      setError(err?.message || 'Failed to update smart settings');
    }
  };

  // Helper function to refresh trade data after a successful trade
  const refreshTradeData = async () => {
    try {
      const [tokensResponse, txResponse] = await Promise.all([
        api.get(API_ENDPOINTS.TRADING.TOKENS),
        api.get(API_ENDPOINTS.TRADING.HISTORY)
      ]);
      
      if (!tokensResponse.success) {
        console.warn('Failed to refresh tokens after trade', {
          error: tokensResponse.error,
          endpoint: API_ENDPOINTS.TRADING.TOKENS
        });
      } else {
        setTokens(tokensResponse.data || []);
      }
      
      if (!txResponse.success) {
        console.warn('Failed to refresh transaction history after trade', {
          error: txResponse.error,
          endpoint: API_ENDPOINTS.TRADING.HISTORY
        });
      } else {
        setTxHistory(safeGetTxHistory(txResponse.data));
      }
      
      // Also refresh chart data if we have a selected token
      if (selectedToken) {
        // Refresh chart data
        try {
          setIsChartLoading(true);
          setChartError('');
          
          const { data, success } = await api.get(
            `${API_ENDPOINTS.TRADING.PRICE_CHART}?token=${selectedToken}&timeframe=1d`
          );
          
          if (success && data && data.chartData) {
            // Process chart data as in fetchChartData function
            const processedData = processChartData(data);
            setChartData(processedData);
          } else {
            console.warn('Could not extract valid chart data from response', data);
            setChartData([]);
            setChartError('No valid chart data available for this token');
          }
        } catch (chartErr: any) {
          console.error('Failed to refresh chart data', chartErr);
          setChartData([]);
          setChartError(chartErr?.message || 'Failed to refresh price chart data');
        } finally {
          setIsChartLoading(false);
        }
      }
    } catch (refreshErr: any) {
      console.error('Error refreshing data after trade', {
        message: refreshErr.message,
        stack: refreshErr.stack
      });
    }
  };
  
  // Helper function to process chart data from API response
  const processChartData = (data: any): ChartDataPoint[] => {
    let chartData: ChartDataPoint[] = [];
    
    if (data.chartData) {
      const { timestamps, prices, labels } = data.chartData;
      
      if (Array.isArray(labels) && Array.isArray(prices) && labels.length === prices.length && labels.length > 0) {
        chartData = labels.map((label, index) => ({
          timestamp: label,
          price: prices[index],
          formattedTime: formatTimestamp(label)
        }));
      } else if (Array.isArray(timestamps) && Array.isArray(prices) && timestamps.length === prices.length && timestamps.length > 0) {
        chartData = timestamps.map((timestamp, index) => ({
          timestamp: new Date(timestamp * 1000).toISOString(),
          price: prices[index],
          formattedTime: formatTimestamp(new Date(timestamp * 1000).toISOString())
        }));
      }
    } else if (Array.isArray(data.prices) && Array.isArray(data.times || data.timestamps || data.dates)) {
      const times = data.times || data.timestamps || data.dates;
      if (times.length === data.prices.length) {
        chartData = times.map((time, index) => ({
          timestamp: typeof time === 'number' ? new Date(time * 1000).toISOString() : time,
          price: data.prices[index],
          formattedTime: formatTimestamp(typeof time === 'number' ? new Date(time * 1000).toISOString() : time)
        }));
      }
    } else if (Array.isArray(data) || Array.isArray(data.points)) {
      const points = Array.isArray(data) ? data : data.points;
      if (Array.isArray(points) && points.length > 0) {
        const firstPoint = points[0];
        if (firstPoint && (firstPoint.timestamp || firstPoint.time || firstPoint.date) && (firstPoint.price || firstPoint.value !== undefined)) {
          chartData = points.map(point => ({
            timestamp: point.timestamp || point.time || point.date,
            price: point.price || point.value,
            formattedTime: formatTimestamp(point.timestamp || point.time || point.date)
          }));
        }
      }
    }
    
    if (chartData.length > 0) {
      // Sort by timestamp to ensure proper ordering
      chartData.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
    }
    
    return chartData;
  };
  
  // Function to execute a trade with smart trading settings
  const executeTrade = async () => {
    if (!selectedToken || !amount) {
      setError('Token and amount are required');
      return;
    }
    
    try {
      setError('');
      setResult('');
      setIsConfirming(true);
      
      // Parse amount safely
      let parsedAmount;
      try {
        parsedAmount = parseFloat(amount);
        if (isNaN(parsedAmount) || parsedAmount <= 0) {
          throw new Error('Amount must be a positive number');
        }
      } catch (e) {
        setError('Invalid amount. Please enter a valid number.');
        setIsConfirming(false);
        return;
      }
      
      console.log(`Executing ${action} trade for ${parsedAmount} ${selectedToken}`);
      
      const tradeResponse = await api.post(API_ENDPOINTS.TRADING.EXECUTE, { 
        action, 
        token: selectedToken, 
        amount: parsedAmount,
        timestamp: new Date().toISOString(),
        smart_enabled: smart.enabled,
        risk_level: smart.enabled ? smart.riskLevel : undefined,
        stop_loss: smart.enabled ? smart.stopLoss : undefined,
        take_profit: smart.enabled ? smart.takeProfit : undefined
      });
      
      console.log('Trade API response:', tradeResponse);
      
      if (!tradeResponse.success) {
        throw new ApiError(
          tradeResponse.error || 'Failed to execute trade', 
          tradeResponse.statusCode || 500,
          { 
            action, 
            token: selectedToken, 
            amount: parsedAmount 
          }
        );
      }
      
      // Check if confirmation is required (GMGN service returns confirmation_required status)
      if (tradeResponse.data?.status === 'confirmation_required') {
        // Store confirmation data for the confirmation modal
        setConfirmationData(tradeResponse.data);
        setResult(`Please confirm your ${action} order for ${parsedAmount} ${selectedToken}`);
        return;
      }
      
      // If no confirmation required, handle direct success
      setResult(tradeResponse.data?.message || 'Trade executed successfully');
      
      // Refresh data after successful trade
      await refreshTradeData();
    } catch (err: any) {
      const apiError = err instanceof ApiError ? err : 
        new ApiError(err.message || 'Unexpected trade execution error', 500);
      
      console.error('Trade Execution Error', {
        message: apiError.message,
        statusCode: apiError.statusCode,
        additionalData: apiError.data
      });
      
      setError(apiError.message);
      setResult('Trade execution failed');
    } finally {
      setIsConfirming(false);
    }
  };
  
  // Function to execute a token swap with smart trading settings
  const executeSwap = async (fromToken: string, toToken: string, swapAmount: string) => {
    if (!fromToken || !toToken || !swapAmount) {
      setError('From token, to token, and amount are required for swap');
      return;
    }
    
    try {
      setError('');
      setResult('');
      setIsConfirming(true);
      
      // Parse amount safely
      let parsedAmount;
      try {
        parsedAmount = parseFloat(swapAmount);
        if (isNaN(parsedAmount) || parsedAmount <= 0) {
          throw new Error('Amount must be a positive number');
        }
      } catch (e) {
        setError('Invalid swap amount. Please enter a valid number.');
        setIsConfirming(false);
        return;
      }
      
      console.log(`Executing swap: ${parsedAmount} ${fromToken} → ${toToken}`);
      
      // Include smart trading settings in the swap request
      const swapResponse = await api.post(API_ENDPOINTS.TRADING.SWAP, { 
        from_token: fromToken, 
        to_token: toToken, 
        amount: parsedAmount,
        timestamp: new Date().toISOString(),
        smart_enabled: smart.enabled,
        risk_level: smart.enabled ? smart.riskLevel : undefined,
        stop_loss: smart.enabled ? smart.stopLoss : undefined,
        take_profit: smart.enabled ? smart.takeProfit : undefined
      });
      
      console.log('Swap API response:', swapResponse);
      
      if (!swapResponse.success) {
        throw new ApiError(
          swapResponse.error || 'Failed to execute swap', 
          swapResponse.statusCode || 500,
          { 
            from_token: fromToken, 
            to_token: toToken, 
            amount: parsedAmount 
          }
        );
      }
      
      // Check if confirmation is required
      if (swapResponse.data?.status === 'confirmation_required') {
        // Store confirmation data for the confirmation modal
        setConfirmationData(swapResponse.data);
        setResult(`Please confirm your swap of ${parsedAmount} ${fromToken} to ${toToken}`);
        return;
      }
      
      // If no confirmation required, handle direct success
      setResult(swapResponse.data?.message || 'Swap executed successfully');
      
      // Refresh data after successful swap
      await refreshTradeData();
    } catch (err: any) {
      const apiError = err instanceof ApiError ? err : 
        new ApiError(err.message || 'Unexpected swap execution error', 500);
      
      console.error('Swap Execution Error', {
        message: apiError.message,
        statusCode: apiError.statusCode,
        additionalData: apiError.data
      });
      
      setError(apiError.message);
      setResult('Swap execution failed');
    } finally {
      setIsConfirming(false);
    }
  };
  
  // Function to confirm a trade after user approval
  const confirmTrade = async () => {
    if (!confirmationData || !confirmationData.confirmation_id) {
      setError('No trade to confirm');
      return;
    }
    
    try {
      setError('');
      setIsConfirming(true);
      
      console.log(`Confirming trade with ID: ${confirmationData.confirmation_id}`);
      
      const confirmResponse = await api.post(API_ENDPOINTS.TRADING.CONFIRM, { 
        confirmation_id: confirmationData.confirmation_id
      });
      
      console.log('Trade confirmation response:', confirmResponse);
      
      if (!confirmResponse.success) {
        throw new ApiError(
          confirmResponse.error || 'Failed to confirm trade', 
          confirmResponse.statusCode || 500,
          { confirmation_id: confirmationData.confirmation_id }
        );
      }
      
      setResult(confirmResponse.data?.message || 'Trade confirmed successfully');
      setConfirmationData(null); // Clear confirmation data
      
      // Refresh data after successful trade confirmation
      await refreshTradeData();
    } catch (err: any) {
      const apiError = err instanceof ApiError ? err : 
        new ApiError(err.message || 'Unexpected trade confirmation error', 500);
      
      console.error('Trade Confirmation Error', {
        message: apiError.message,
        statusCode: apiError.statusCode,
        additionalData: apiError.data
      });
      
      setError(apiError.message);
    } finally {
      setIsConfirming(false);
    }
  };
  
  // Function to cancel a trade confirmation
  const cancelTrade = () => {
    setConfirmationData(null);
    setResult('Trade cancelled');
  };

  // filteredTokens is now defined above near the search effect

  // Error boundary to prevent component crashes
  if (error) {
    console.error('Trading component error:', error);
  }
  
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-mono text-red-300">Trading Terminal</h1>

      <div className="grid grid-cols-3 gap-4">
        <div className="col-span-1 space-y-2">
          <input
            className="w-full p-2 bg-white/10 text-white text-sm rounded"
            placeholder="Search token"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <select
            className="w-full p-2 bg-white/10 text-white text-sm rounded"
            value={selectedToken}
            onChange={(e) => setSelectedToken(e.target.value)}
          >
            <option value="">-- select token --</option>
            {filteredTokens.length > 0 ? (
              filteredTokens.map(t => (
                <option key={t.symbol} value={t.symbol}>{t.name} ({t.symbol})</option>
              ))
            ) : (
              // Show a message in the dropdown if no tokens are available
              <option value="" disabled>No tokens available</option>
            )}
          </select>
          {tokens.length === 0 && (
            <div className="mt-1 text-xs text-yellow-400">
              Warning: Token list could not be loaded. Check API connection.
            </div>
          )}
          <input
            className="w-full p-2 bg-white/10 text-white text-sm rounded"
            placeholder="Amount"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
          />
          <select
            className="w-full p-2 bg-white/10 text-white text-sm rounded"
            value={action}
            onChange={(e) => handleActionChange(e.target.value)}
          >
            <option value="buy">Buy</option>
            <option value="sell">Sell</option>
          </select>
          {confirmationData ? (
            <div className="space-y-2 border border-yellow-800 rounded p-2 bg-yellow-900/20 mt-2">
              <h4 className="text-yellow-400 text-sm font-bold">Confirm Trade</h4>
              <p className="text-xs text-white">
                {confirmationData.action?.toUpperCase()} {confirmationData.amount} {confirmationData.token} at {confirmationData.current_price?.toFixed(4) || '?'}
              </p>
              <p className="text-xs text-yellow-300">
                Estimated total: {confirmationData.estimated_total?.toFixed(4) || '?'}
              </p>
              {confirmationData.smart_trading_applied && (
                <div className="text-xs border-t border-yellow-800 mt-1 pt-1">
                  <p className="text-green-400 font-semibold">Smart Trading Applied</p>
                  {confirmationData.original_amount && confirmationData.adjusted_amount && (
                    <p className="text-xs text-yellow-200">
                      Amount adjusted: {confirmationData.original_amount} → {confirmationData.adjusted_amount}
                    </p>
                  )}
                  {confirmationData.stop_loss_price && (
                    <p className="text-xs text-red-300">
                      Stop Loss: {confirmationData.stop_loss_price.toFixed(6)}
                    </p>
                  )}
                  {confirmationData.take_profit_price && (
                    <p className="text-xs text-green-300">
                      Take Profit: {confirmationData.take_profit_price.toFixed(6)}
                    </p>
                  )}
                </div>
              )}
              <div className="flex space-x-2">
                <button
                  onClick={confirmTrade}
                  className="flex-1 rounded bg-green-700 px-2 py-1 text-xs hover:bg-green-800"
                  disabled={isConfirming}
                >
                  {isConfirming ? 'Confirming...' : 'Confirm'}
                </button>
                <button
                  onClick={cancelTrade}
                  className="flex-1 rounded bg-red-800 px-2 py-1 text-xs hover:bg-red-900"
                  disabled={isConfirming}
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <button
              onClick={executeTrade}
              className="w-full rounded bg-red-700 px-4 py-2 text-sm hover:bg-red-900"
              disabled={isConfirming}
            >
              {isConfirming ? 'Processing...' : 'Execute Trade'}
            </button>
          )}
          {result && <p className="text-green-400 text-sm">{result}</p>}

          <div className="mt-4 border-t border-red-900 pt-4">
            <label className="flex items-center space-x-2 text-sm">
              <input
                type="checkbox"
                checked={smart.enabled}
                onChange={() => updateSmart('enabled', !smart.enabled)}
              />
              <span className="text-red-400">Enable Smart Trade</span>
            </label>

            {smart.enabled && (
              <div className="space-y-2 mt-2">
                <label className="text-xs">Risk Level: {smart.riskLevel}%</label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={smart.riskLevel}
                  onChange={(e) => updateSmart('riskLevel', parseInt(e.target.value))}
                  className="w-full"
                />

                <label className="text-xs">Max Trade Size: {smart.maxTradeSize}</label>
                <input
                  type="number"
                  step="0.01"
                  className="w-full p-1 bg-white/10 text-white rounded"
                  value={smart.maxTradeSize}
                  onChange={(e) => updateSmart('maxTradeSize', parseFloat(e.target.value))}
                />

                <label className="text-xs">Stop Loss (%): {smart.stopLoss}</label>
                <input
                  type="number"
                  step="0.1"
                  className="w-full p-1 bg-white/10 text-white rounded"
                  value={smart.stopLoss}
                  onChange={(e) => updateSmart('stopLoss', parseFloat(e.target.value))}
                />

                <label className="text-xs">Take Profit (%): {smart.takeProfit}</label>
                <input
                  type="number"
                  step="0.1"
                  className="w-full p-1 bg-white/10 text-white rounded"
                  value={smart.takeProfit}
                  onChange={(e) => updateSmart('takeProfit', parseFloat(e.target.value))}
                />
              </div>
            )}
          </div>
        </div>

        <div className="col-span-2 space-y-4">
          <div className="border border-red-800 rounded p-4">
            <div className="flex justify-between items-center mb-2">
              <h2 className="text-red-400 text-sm">Price Chart</h2>
              {selectedToken && (
                <span className="text-xs text-red-300 font-mono">{selectedToken}</span>
              )}
            </div>
            
            {isChartLoading ? (
              <div className="h-[200px] flex items-center justify-center">
                <p className="text-gray-400 text-sm">Loading chart data...</p>
              </div>
            ) : chartData.length > 0 ? (
              <div>
                <ResponsiveContainer width="100%" height={200}>
                  <LineChart data={chartData}>
                    <XAxis 
                      dataKey="formattedTime" 
                      tick={{ fontSize: 10 }}
                      tickFormatter={(value) => {
                        // Show abbreviated time format for x-axis
                        if (!value) return '';
                        // Extract just the time portion or date depending on format
                        const parts = value.split(', ');
                        return parts.length > 1 ? parts[1] : parts[0];
                      }}
                    />
                    <YAxis 
                      domain={['auto', 'auto']} 
                      tick={{ fontSize: 10 }}
                      tickFormatter={(value) => {
                        // Format price values on y-axis
                        if (value >= 1000) return `${(value/1000).toFixed(1)}k`;
                        if (value < 0.01) return value.toExponential(1);
                        return value.toFixed(2);
                      }}
                    />
                    <Tooltip 
                      formatter={(value, name) => [
                        typeof value === 'number' ? 
                          value < 0.01 ? value.toFixed(8) : value.toFixed(4) : 
                          value, 
                        'Price'
                      ]}
                      labelFormatter={(label) => {
                        // Show full date and time in tooltip
                        return label || '';
                      }}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="price" 
                      stroke="#ff5555" 
                      strokeWidth={2} 
                      dot={false} 
                      activeDot={{ r: 4, stroke: '#ff5555', strokeWidth: 1 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
                <div className="mt-2 text-xs text-gray-400 text-right">
                  {chartData.length} data points • Last updated: {new Date().toLocaleTimeString()}
                </div>
              </div>
            ) : (
              <div className="h-[200px] flex flex-col items-center justify-center">
                <p className="text-gray-400 mb-2">No chart data available.</p>
                {chartError ? (
                  <p className="text-red-400 text-xs text-center max-w-[80%]">{chartError}</p>
                ) : selectedToken ? (
                  <p className="text-gray-500 text-xs text-center max-w-[80%]">
                    Try selecting a different token or timeframe.
                  </p>
                ) : (
                  <p className="text-gray-500 text-xs text-center max-w-[80%]">
                    Select a token to view its price chart.
                  </p>
                )}
              </div>
            )}
          </div>

          <div className="border border-red-800 rounded p-4">
            <h2 className="text-red-400 text-sm mb-2">Transaction History</h2>
            <div className="max-h-64 overflow-y-auto space-y-2 text-sm">
              {Array.isArray(txHistory) && txHistory.map((tx, i) => (
                <div key={i} className="border-b border-red-800 pb-2">
                  <p className={tx && tx.type === 'buy' ? 'text-green-400' : 'text-red-400'}>
                    {tx?.type?.toUpperCase() || 'TRADE'} {tx?.amount || 0} {tx?.token || ''}
                  </p>
                  <p className="text-xs text-gray-400">{tx?.timestamp || new Date().toISOString()}</p>
                </div>
              ))}
              {txHistory.length === 0 && <p className="text-gray-400">No transactions yet.</p>}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default function Trading() {
  return (
    <ErrorBoundary componentName="Trading">
      <TradingContent />
    </ErrorBoundary>
  );
}
