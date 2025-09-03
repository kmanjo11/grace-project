export type UIMode = 'spot' | 'leverage';

export interface Candle {
  ts: number; // ms
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface GetCandlesParams {
  mode: UIMode;
  market?: string;
  chain?: string;
  tokenCA?: string;
  interval: string; // '1','5','15','60','240','720','1D' etc.
  from?: number; // seconds or ms accepted; backend normalizes
  to?: number;   // seconds or ms accepted; backend normalizes
}

const API_BASE = '';

function toQuery(params: Record<string, any>) {
  const q = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v === undefined || v === null || v === '') return;
    q.set(k, String(v));
  });
  return q.toString();
}

export const MarketDataService = {
  async getCandles(p: GetCandlesParams): Promise<Candle[]> {
    const qs = toQuery({
      mode: p.mode,
      market: p.market,
      chain: p.chain,
      tokenCA: p.tokenCA,
      interval: p.interval,
      from: p.from,
      to: p.to,
    });
    const res = await fetch(`${API_BASE}/api/ui/candles?${qs}`);
    if (!res.ok) throw new Error(`candles http ${res.status}`);
    const json = await res.json();
    const rows: any[] = json?.candles || [];
    return rows.map((r) => ({
      ts: Number(r.ts),
      open: Number(r.open),
      high: Number(r.high),
      low: Number(r.low),
      close: Number(r.close),
      volume: Number(r.volume ?? 0),
    }));
  },
};

export default MarketDataService;
