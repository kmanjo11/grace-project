import axios from 'axios';

/**
 * Get environment variable with fallback
 * Compatible with both Vite and Next.js
 */
function getEnv(key: string, defaultValue: string = ''): string {
  // Check for Next.js environment variables first
  if (typeof process !== 'undefined' && process.env && process.env[key]) {
    return process.env[key] || defaultValue;
  }
  // Fallback to Vite environment variables
  if (typeof window !== 'undefined' && (window as any).import?.meta?.env) {
    return (window as any).import.meta.env[key] || defaultValue;
  }
  return defaultValue;
}

// Type definition for Axios errors
interface AxiosError extends Error {
  isAxiosError: boolean;
  response?: {
    status?: number;
    data?: any;
  };
  message: string;
}

/**
 * Base URL for Mango V3 API
 * @default 'http://mango-v3-service:8080'
 */
const MANGO_V3_BASE_URL = getEnv('NEXT_PUBLIC_MANGO_V3_BASE_URL', 'http://mango-v3-service:8080');

/**
 * Time in seconds for different resolution aliases
 */
const RESOLUTION_MAP: Record<string, number> = {
  '1m': 60,     // 1 minute
  '5m': 300,    // 5 minutes
  '15m': 900,   // 15 minutes
  '1h': 3600,   // 1 hour
  '4h': 14400,  // 4 hours
  '1d': 86400,  // 1 day
};

/**
 * OHLCV (Open-High-Low-Close-Volume) data point
 */
export interface OHLCVData {
  /** Unix timestamp in seconds */
  time: number;
  /** Opening price */
  open: number;
  /** Highest price */
  high: number;
  /** Lowest price */
  low: number;
  /** Closing price */
  close: number;
  /** Trading volume */
  volume: number;
  /** Additional properties */
  [key: string]: any;
}

/**
 * Market data for a trading pair
 */
export interface MarketData {
  /** Market name (e.g., 'BTC-PERP') */
  name: string;
  /** Contract address */
  address: string;
  /** Base currency symbol (e.g., 'BTC') */
  baseCurrency: string;
  /** Quote currency symbol (e.g., 'USDC') */
  quoteCurrency: string;
  /** Current price, if available */
  price?: number;
  /** Market identifier */
  marketId?: string;
  /** Additional properties */
  [key: string]: any;
}

/**
 * Custom error class for Mango V3 API errors
 */
export class MangoV3Error extends Error {
  /**
   * @param message - Error message
   * @param statusCode - HTTP status code, if available
   * @param details - Additional error details
   */
  constructor(
    message: string,
    public statusCode?: number,
    public details?: any
  ) {
    super(message);
    this.name = 'MangoV3Error';
  }
}

export class MangoV3Service {
  /**
   * Validates that the market name is a non-empty string
   * @param marketName - The market name to validate
   * @throws {MangoV3Error} If validation fails
   */
  private static validateMarketName(marketName: string): void {
    if (!marketName || typeof marketName !== 'string') {
      throw new MangoV3Error('Market name is required and must be a string');
    }
  }

  /**
   * Validates and converts resolution to seconds
   * @param resolution - Resolution as string alias or seconds
   * @returns Resolution in seconds
   * @throws {MangoV3Error} If resolution is invalid
   */
  private static validateResolution(resolution: string | number): number {
    if (typeof resolution === 'string') {
      if (!(resolution in RESOLUTION_MAP)) {
        throw new MangoV3Error(`Unsupported resolution: ${resolution}`);
      }
      return RESOLUTION_MAP[resolution];
    }
    return resolution;
  }

  /**
   * Fetches OHLCV (candlestick) data for a specific market
   * @param marketName - The market identifier (e.g., 'BTC-PERP')
   * @param resolution - Resolution as string alias (e.g., '1h') or seconds (default: '1h')
   * @param startTime - Optional start time in seconds (Unix timestamp)
   * @param endTime - Optional end time in seconds (Unix timestamp)
   * @returns Array of OHLCV data points
   * @throws {MangoV3Error} If the request fails or data is invalid
   */
  static async getOHLCV(
    marketName: string,
    resolution: string | number = '1h',
    startTime?: number,
    endTime?: number
  ): Promise<OHLCVData[]> {
    try {
      this.validateMarketName(marketName);
      const resolutionInSeconds = this.validateResolution(resolution);

      const params: Record<string, string> = {
        resolution: resolutionInSeconds.toString(),
      };

      // Use timestamps as-is (expected in seconds)
      if (startTime !== undefined) params.start_time = Math.floor(startTime).toString();
      if (endTime !== undefined) params.end_time = Math.floor(endTime).toString();

      const response = await axios.get<OHLCVData[]>(
        `${MANGO_V3_BASE_URL}/api/markets/${encodeURIComponent(marketName)}/candles`,
        {
          params,
          validateStatus: (status) => status < 500,
        }
      );

      if (response.status !== 200) {
        throw new MangoV3Error(
          `Failed to fetch OHLCV data: ${response.statusText}`,
          response.status,
          response.data
        );
      }

      const responseData = Array.isArray(response.data) ? response.data : [];

      // Validate response data structure
      const isValidData = responseData.every(item => 
        item && 
        typeof item.time === 'number' &&
        'open' in item &&
        'high' in item &&
        'low' in item &&
        'close' in item &&
        'volume' in item
      );

      if (!isValidData) {
        throw new MangoV3Error('Invalid OHLCV data format received from API');
      }

      return responseData;
    } catch (error) {
      if (error instanceof MangoV3Error) throw error;
      
      const axiosError = error as AxiosError;
      if (axiosError.isAxiosError) {
        throw new MangoV3Error(
          `Network error: ${axiosError.message}`,
          axiosError.response?.status,
          axiosError.response?.data
        );
      }
      throw new MangoV3Error(
        `Failed to fetch OHLCV data: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  /**
   * Searches for markets matching the query
   * @param query - Search query (empty returns all markets)
   * @returns Array of matching markets
   * @throws {MangoV3Error} If the request fails
   */
  static async searchMarkets(query: string = ''): Promise<MarketData[]> {
    try {
      const response = await axios.get<MarketData[]>(
        `${MANGO_V3_BASE_URL}/api/markets`,
        { 
          validateStatus: (status) => status < 500,
          params: { q: query }
        }
      );

      if (response.status !== 200) {
        throw new MangoV3Error(
          `Failed to search markets: ${response.statusText}`,
          response.status,
          response.data
        );
      }

      const markets = Array.isArray(response.data) ? response.data : [];
      
      if (!query) return markets;
      
      // Filter results based on query
      const queryLower = query.toLowerCase().trim();
      return markets.filter(market => 
        market.name?.toLowerCase().includes(queryLower) ||
        market.baseCurrency?.toLowerCase().includes(queryLower) ||
        market.quoteCurrency?.toLowerCase().includes(queryLower) ||
        market.address?.toLowerCase() === queryLower
      );
    } catch (error) {
      if (error instanceof MangoV3Error) throw error;
      
      const axiosError = error as AxiosError;
      if (axiosError.isAxiosError) {
        throw new MangoV3Error(
          `Network error while searching markets: ${axiosError.message}`,
          axiosError.response?.status,
          axiosError.response?.data
        );
      }
      throw new MangoV3Error(
        `Failed to search markets: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }
}

export default MangoV3Service;
