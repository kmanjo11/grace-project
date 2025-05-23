// Standard error codes for the application
export enum ErrorCode {
  // API Errors (1000-1999)
  API_REQUEST_FAILED = 1000,
  RATE_LIMIT_EXCEEDED = 1001,
  INVALID_RESPONSE = 1002,
  
  // Validation Errors (2000-2999)
  INVALID_INPUT = 2000,
  MISSING_REQUIRED_FIELD = 2001,
  
  // Network Errors (3000-3999)
  NETWORK_ERROR = 3000,
  TIMEOUT = 3001,
  
  // Wallet/Connection Errors (4000-4999)
  WALLET_NOT_CONNECTED = 4000,
  INSUFFICIENT_BALANCE = 4001,
  
  // Trading Errors (5000-5999)
  TRADE_VALIDATION_FAILED = 5000,
  ORDER_EXECUTION_FAILED = 5001,
  
  // Unknown Error
  UNKNOWN_ERROR = 9999
}

export interface AppError extends Error {
  code: ErrorCode;
  details?: any;
  retryable: boolean;
  retryAfter?: number; // in milliseconds
  cause?: Error;
}

export function createError(
  message: string,
  code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
  options: {
    details?: any;
    retryable?: boolean;
    retryAfter?: number;
    cause?: Error;
  } = {}
): AppError {
  const error = new Error(message) as AppError;
  error.code = code;
  error.details = options.details;
  error.retryable = options.retryable ?? false;
  error.retryAfter = options.retryAfter;
  
  if (options.cause) {
    error.cause = options.cause;
  }
  
  return error;
}

export function isAppError(error: unknown): error is AppError {
  return error instanceof Error && 'code' in error && 'retryable' in error;
}

export function withRetry<T>(
  fn: () => Promise<T>,
  options: {
    maxRetries?: number;
    initialDelay?: number;
    maxDelay?: number;
    backoffFactor?: number;
    retryOn?: (error: unknown) => boolean;
  } = {}
): Promise<T> {
  const {
    maxRetries = 3,
    initialDelay = 1000,
    maxDelay = 30000,
    backoffFactor = 2,
    retryOn = (error: unknown) => {
      if (isAppError(error)) {
        return error.retryable;
      }
      return false;
    },
  } = options;

  let retries = 0;
  let currentDelay = initialDelay;

  const attempt = async (): Promise<T> => {
    try {
      return await fn();
    } catch (error) {
      if (!retryOn(error) || retries >= maxRetries) {
        throw error;
      }

      retries++;
      
      // Calculate next delay with exponential backoff
      const delay = Math.min(currentDelay, maxDelay);
      currentDelay *= backoffFactor;
      
      // Add jitter
      const jitter = delay * 0.2 * Math.random();
      const waitTime = delay + jitter;
      
      console.log(`Retry ${retries}/${maxRetries} after ${waitTime.toFixed(0)}ms...`);
      
      await new Promise(resolve => setTimeout(resolve, waitTime));
      return attempt();
    }
  };

  return attempt();
}
