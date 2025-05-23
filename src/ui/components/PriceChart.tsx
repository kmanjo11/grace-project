import React, { useEffect, useRef, useState, useCallback } from 'react';
import { 
  createChart, 
  IChartApi, 
  ISeriesApi, 
  Time, 
  ColorType, 
  CandlestickData,
  UTCTimestamp,
  CandlestickSeriesPartialOptions,
  ISeriesApi as ISeriesApiExtended
} from 'lightweight-charts';
import MangoV3Service, { OHLCVData, MangoV3Error } from '../../services/mangoV3Service';
import { TokenData } from '../api/tradingTypes';
import ErrorBoundary from './ErrorBoundary';

// Extend the IChartApi to include our enhanced addCandlestickSeries
declare module 'lightweight-charts' {
  interface IChartApi {
    addCandlestickSeries(options?: any): ISeriesApiExtended<'Candlestick', Time>;
  }
}

type CandlestickSeries = ISeriesApiExtended<'Candlestick', Time>;
type CandlestickDataPoint = CandlestickData<Time>;

interface PriceChartProps {
  tokenAddress: string;
  onTokenSelect?: (token: TokenData) => void;
  selectedToken?: TokenData | null;
  resolution: string;
  onResolutionChange: (resolution: string) => void;
  onError?: (error: string | null) => void;
  onLoading?: (loading: boolean) => void;
}

const RESOLUTIONS = [
  { label: '1m', value: '1m' },
  { label: '5m', value: '5m' },
  { label: '15m', value: '15m' },
  { label: '1h', value: '1h' },
  { label: '4h', value: '4h' },
  { label: '1d', value: '1d' },
];

// Cache types and configuration
interface ChartCacheEntry {
  data: OHLCVData[];
  timestamp: number;
  timeFrom?: number;
  timeTo?: number;
}

const chartDataCache = new Map<string, ChartCacheEntry>();
const CACHE_TTL = 30000; // 30 seconds cache

/**
 * Fetches OHLCV data with caching and time range support
 * @param marketName - The market identifier (e.g., 'BTC-PERP')
 * @param resolution - Resolution string (e.g., '1h', '4h')
 * @param timeFrom - Optional start time in seconds (Unix timestamp)
 * @param timeTo - Optional end time in seconds (Unix timestamp)
 * @returns Promise with OHLCV data
 */
async function fetchWithCache(
  marketName: string, 
  resolution: string,
  timeFrom?: number,
  timeTo?: number
): Promise<OHLCVData[]> {
  const cacheKey = `${marketName}:${resolution}:${timeFrom || 'all'}:${timeTo || 'all'}`;
  const now = Date.now();

  // Try to get from cache first
  const cached = chartDataCache.get(cacheKey);
  if (cached && (now - cached.timestamp) < CACHE_TTL) {
    // Check if cached data covers the requested time range
    if ((!timeFrom || (cached.timeFrom && cached.timeFrom <= timeFrom)) &&
        (!timeTo || (cached.timeTo && cached.timeTo >= timeTo))) {
      return cached.data;
    }
  }

  try {
    // Default to 24 hours if no time range provided
    const endTime = timeTo || Math.floor(Date.now() / 1000);
    const startTime = timeFrom || (endTime - 24 * 60 * 60);

    // Use MangoV3Service to fetch data
    const data = await MangoV3Service.getOHLCV(
      marketName,
      resolution, // MangoV3Service handles resolution mapping
      startTime,
      endTime
    );

    // Cache the result
    chartDataCache.set(cacheKey, {
      data,
      timestamp: now,
      timeFrom: startTime,
      timeTo: endTime
    });

    return data;
  } catch (error) {
    console.error('Error in fetchWithCache:', error);
    throw error;
  }
}

const PriceChart: React.FC<PriceChartProps> = ({
  tokenAddress,
  onTokenSelect,
  selectedToken: propSelectedToken,
  resolution,
  onResolutionChange: propOnResolutionChange,
  onError: propOnError,
  onLoading: propOnLoading,
}) => {
  // State management
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  // Resolution is now fully controlled by parent
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [searchResults, setSearchResults] = useState<TokenData[]>([]);
  const [showSearchResults, setShowSearchResults] = useState<boolean>(false);
  const [localSelectedToken, setLocalSelectedToken] = useState<TokenData | null>(
    propSelectedToken || null
  );

  // Notify parent of loading state changes
  useEffect(() => {
    propOnLoading?.(isLoading);
    
    // Cleanup function
    return () => {
      propOnLoading?.(false);
    };
  }, [isLoading, propOnLoading]);
  
  // Notify parent of error state changes
  useEffect(() => {
    propOnError?.(error);
    
    // Cleanup function
    return () => {
      propOnError?.(null);
    };
  }, [error, propOnError]);

  // Refs
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chart = useRef<IChartApi | null>(null);
  const candlestickSeries = useRef<CandlestickSeries | null>(null);
  const abortController = useRef<AbortController | null>(null);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      // Cleanup chart instance
      if (chart.current) {
        chart.current.remove();
        chart.current = null;
      }
      
      // Cleanup any pending requests
      if (abortController.current) {
        abortController.current.abort();
        abortController.current = null;
      }
    };
  }, []);

  /**
   * Fetches and updates chart data
   */
  const fetchChartData = useCallback(async () => {
    if (!tokenAddress || !candlestickSeries.current) return;

    // Cancel any pending requests
    if (abortController.current) {
      abortController.current.abort();
    }
    abortController.current = new AbortController();

    try {
      setIsLoading(true);
      setError(null);
      
      // Fetch data using MangoV3Service with caching
      const ohlcvData = await fetchWithCache(tokenAddress, resolution);
      
      if (ohlcvData?.length > 0) {
        // Format data for Lightweight Charts
        const formattedData = ohlcvData.map(item => {
          // Mango V3 returns timestamps in seconds, ensure it's a number
          const timestamp = typeof item.time === 'number' ? item.time : 0;
          
          return {
            time: Math.floor(timestamp) as UTCTimestamp, // Ensure it's a whole number
            open: item.open,
            high: item.high,
            low: item.low,
            close: item.close,
          };
        });
        
        if (formattedData.length > 0 && candlestickSeries.current) {
          candlestickSeries.current.setData(formattedData);
          
          // Auto-resize chart to fit data
          if (chart.current) {
            chart.current.timeScale().fitContent();
          }
        } else {
          throw new MangoV3Error('No valid price data available');
        }
      } else {
        throw new MangoV3Error('No data available for the selected token');
      }
    } catch (err) {
      if ((err as Error).name !== 'AbortError') {
        const errorMsg = err instanceof MangoV3Error 
          ? err.message 
          : 'Failed to load chart data';
          
        console.error('Error fetching OHLCV data:', err);
        setError(errorMsg);
        if (propOnError) propOnError(errorMsg);
      }
    } finally {
      setIsLoading(false);
      if (propOnLoading) propOnLoading(false);
    }
  }, [tokenAddress, resolution, propOnError, propOnLoading]);

  // Handle resolution changes - delegate to parent
  const handleResolutionChange = useCallback((newResolution: string) => {
    propOnResolutionChange(newResolution);
  }, [propOnResolutionChange]);

  // Initialize the candlestick series with proper styling
  const initChart = useCallback(() => {
    if (!chartContainerRef.current) return;

    // Clear previous chart if it exists
    if (chart.current) {
      chart.current.remove();
      chart.current = null;
    }

    // Create new chart with proper types
    const newChart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#1E1E1E' },
        textColor: '#d9d9d9',
      },
      grid: {
        vertLines: { color: '#2b2b43' },
        horzLines: { color: '#2b2b43' },
      },
      width: chartContainerRef.current.clientWidth,
      height: 400,
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
      },
    });

    // Store chart reference
    chart.current = newChart;

    // Add candlestick series with proper styling
    const series = newChart.addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    });
    
    candlestickSeries.current = series;
    
    // Fit the content to the visible area
    newChart.timeScale().fitContent();

    // Add window resize handler
    const handleResize = () => {
      if (chart.current && chartContainerRef.current) {
        chart.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
      if (chart.current) {
        chart.current.remove();
        chart.current = null;
      }
    };
  }, []);

  // Fetch chart data when token or resolution changes
  useEffect(() => {
    if (tokenAddress) {
      fetchChartData();
    }
  }, [tokenAddress, resolution, fetchChartData]);

  // Handle search input changes
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchQuery(value);
    // TODO: Implement search functionality
  };

  // Handle token selection from search results
  const handleTokenSelect = (token: TokenData) => {
    setLocalSelectedToken(token);
    setShowSearchResults(false);
    if (onTokenSelect) {
      onTokenSelect(token);
    }
  };

  // Wrap the chart in an error boundary
  const ChartWithErrorBoundary = () => (
    <ErrorBoundary 
      fallback={
        <div className="flex items-center justify-center h-full bg-red-900/20 text-red-200 p-4">
          <p>Chart failed to load. Please try again.</p>
        </div>
      }
    >
      <div ref={chartContainerRef} className="w-full h-full" />
    </ErrorBoundary>
  );

  return (
    <div className="flex flex-col h-full">
      {/* Chart controls */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-4 gap-2">
        {/* Search input */}
        <div className="relative w-full md:w-64">
          <input
            type="text"
            value={searchQuery}
            onChange={handleSearchChange}
            onFocus={() => setShowSearchResults(true)}
            onBlur={() => setTimeout(() => setShowSearchResults(false), 200)}
            placeholder="Search for a token..."
            className="w-full p-2 rounded bg-gray-800 text-white"
          />
          {showSearchResults && searchResults.length > 0 && (
            <div className="absolute z-10 mt-1 w-full bg-gray-800 rounded-md shadow-lg max-h-60 overflow-auto">
              {searchResults.map((token) => (
                <div
                  key={token.address}
                  className="p-2 hover:bg-gray-700 cursor-pointer flex items-center"
                  onMouseDown={() => handleTokenSelect(token)}
                >
                  {token.logoURI && (
                    <img 
                      src={token.logoURI} 
                      alt={token.name || token.symbol || 'Token'} 
                      className="w-6 h-6 mr-2 rounded-full"
                    />
                  )}
                  <div>
                    <div className="font-medium">{token.name || 'Unknown Token'}</div>
                    <div className="text-sm text-gray-400">
                      {token.symbol || (token.address ? token.address.slice(0, 8) : 'N/A')}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Resolution selector */}
        <div className="flex space-x-2 overflow-x-auto w-full md:w-auto">
          {RESOLUTIONS.map((res) => (
            <button
              key={res.value}
              className={`px-3 py-1 rounded ${
                resolution === res.value ? 'bg-blue-600' : 'bg-gray-700 hover:bg-gray-600'
              }`}
              onClick={() => handleResolutionChange(res.value)}
            >
              {res.label}
            </button>
          ))}
        </div>
      </div>

      {/* Chart container */}
      <div className="flex-1 relative">
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-900/80 z-20">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          </div>
        )}
        
        {error && !isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-red-900/50 text-red-100 p-4 z-10">
            <p>{error}</p>
            <button 
              onClick={fetchChartData}
              className="ml-3 px-3 py-1 bg-red-700 rounded hover:bg-red-600 transition-colors"
            >
              Retry
            </button>
          </div>
        )}
        
        <ChartWithErrorBoundary />
      </div>
    </div>
  );
};

export default PriceChart;