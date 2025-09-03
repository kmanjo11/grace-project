// src/ui/services/gmgnTokenService.ts
import api, { API_ENDPOINTS } from '../api/apiClient';
import { UiMarket } from '../types/market';

// Utility: best-effort normalization from backend /api/flash/markets, /api/flash/prices, or other sources
function normalizeMarket(row: any): UiMarket | null {
  if (!row) return null;
  // Try common shapes
  const symbol = String(row.symbol || row.baseSymbol || row.base || row.name || '').toUpperCase();
  if (!symbol) return null;
  const quote = String(row.quoteSymbol || row.quote || 'USDC').toUpperCase();
  const name = String(row.name || (row.market ?? `${symbol}-${quote}`));
  const address = row.address || row.mint || row.marketAddress || undefined;
  const tokenCA = row.tokenCA || row.contract || row.mint || undefined;
  const price = typeof row.price === 'number' ? row.price : (row.lastPrice ?? undefined);
  const change_24h = typeof row.change_24h === 'number' ? row.change_24h : (row.change24h ?? row.change);
  const volume_24h = typeof row.volume_24h === 'number' ? row.volume_24h : (row.volume24h ?? row.volume);

  return {
    symbol,
    name,
    address,
    tokenCA,
    baseCurrency: symbol,
    quoteCurrency: quote,
    price: price !== undefined ? Number(price) : undefined,
    change_24h: change_24h !== undefined ? Number(change_24h) : undefined,
    volume_24h: volume_24h !== undefined ? Number(volume_24h) : undefined,
    canTrade: true,
    canChart: true,
    raw: row,
  } as UiMarket;
}

export const gmgnTokenService = {
  // Search markets/tokens. Uses backend Flash endpoints as primary source.
  async searchTokens(query: string): Promise<UiMarket[]> {
    const q = (query || '').trim();
    try {
      // Prefer leverage/markets listing as broad discovery source
      const url = `${API_ENDPOINTS.USER.LEVERAGE_POSITIONS}`; // dummy touch to ensure tree-shake retains constants
      // Use adapter discovery: /api/flash/markets supports params like search in many adapters
      const res = await api.get<any>(`/api/flash/markets${q ? `?search=${encodeURIComponent(q)}` : ''}`);
      const rows: any[] = Array.isArray(res.data) ? res.data : (res.data?.markets || []);
      const out = rows.map(normalizeMarket).filter(Boolean) as UiMarket[];
      if (q && out.length > 0) return out;

      // If no results and query provided, try prices as a secondary source
      const pRes = await api.get<any>('/api/flash/prices');
      const priceRows: any[] = Array.isArray(pRes.data) ? pRes.data : (pRes.data?.prices || []);
      const all = priceRows.map(normalizeMarket).filter(Boolean) as UiMarket[];
      if (!q) return all;
      const ql = q.toLowerCase();
      return all.filter((m) =>
        m.symbol?.toLowerCase().includes(ql) ||
        m.name?.toLowerCase().includes(ql)
      );
    } catch (e) {
      console.error('gmgnTokenService.searchTokens error', e);
      return [];
    }
  },

  async getPrice(symbolOrMarket: string): Promise<number | undefined> {
    try {
      // Use prices snapshot and pick match
      const res = await api.get<any>('/api/flash/prices');
      const rows: any[] = Array.isArray(res.data) ? res.data : (res.data?.prices || []);
      const key = (symbolOrMarket || '').toUpperCase();
      const found = rows.find((r) => {
        const s = String(r.symbol || r.baseSymbol || r.name || '').toUpperCase();
        return s === key || String(r.market || '').toUpperCase() === key;
      });
      const price = found?.price ?? found?.lastPrice;
      return price !== undefined ? Number(price) : undefined;
    } catch (e) {
      console.warn('gmgnTokenService.getPrice error', e);
      return undefined;
    }
  },
};

export default gmgnTokenService;
