// src/ui/types/market.ts

export interface UiMarket {
  // Display identifiers
  symbol: string; // e.g., SOL or SOL-PERP
  name: string;   // human friendly or market name

  // Addressing
  address?: string;     // token mint / market address if applicable
  tokenCA?: string;     // contract address for GMGN spot tokens

  // Pairing
  baseCurrency?: string;
  quoteCurrency?: string;

  // Last known pricing
  price?: number;
  change_24h?: number;
  volume_24h?: number;

  // Extra data from providers
  marketId?: string;
  canTrade?: boolean;
  canChart?: boolean;
  [key: string]: any;
}
