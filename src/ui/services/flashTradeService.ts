// src/ui/services/flashTradeService.ts
import api from '../api/apiClient';

export type FlashSide = 'buy' | 'sell' | 'long' | 'short';

export interface FlashOrderParams {
  market: string;          // e.g., SOL-PERP
  side: FlashSide;         // 'buy' | 'sell'
  size: number;            // base size
  leverage?: number;       // e.g., 5
  reduceOnly?: boolean;
  payoutTokenSymbol?: string;
  collateralTokenSymbol?: string;
  // Optional slippage in basis points (e.g., 80 = 0.8%)
  slippageBps?: number;
  // Optional risk params
  takeProfitPrice?: number;
  stopLossPrice?: number;
  // Optional wallet routing hint
  walletType?: 'internal' | 'phantom';
}

export interface FlashOrderResponse {
  success: boolean;
  message?: string;
  error?: string;
  // Adapter payload passthrough
  data?: any;
}

export interface FlashQuoteParams {
  market: string;
  side: FlashSide;
  size: number;
  leverage?: number;
  walletType?: 'internal' | 'phantom';
}

export const flashTradeService = {
  async getQuote(params: FlashQuoteParams) {
    const res = await api.post<any>('/api/flash/quote', params);
    return res;
  },

  async placeOrder(params: FlashOrderParams) {
    // Backend injects ownerPubkey if missing; walletType optionally routes server-side signing
    const res = await api.post<FlashOrderResponse>('/api/flash/order', params);
    return res;
  },

  async getLiquidationPrice(params: { market: string; ownerPubkey?: string; walletType?: 'internal' | 'phantom' }) {
    // Owner pubkey may be injected by backend if authenticated
    const res = await api.post<any>('/api/flash/liquidation-price', params);
    return res;
  },
};

export default flashTradeService;
