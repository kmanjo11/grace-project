import React from 'react';
import GMGNEmbeddedChart, { GMGNInterval, GMGNTheme } from './GMGNEmbeddedChart';
import LeverageCandlesChart from './LeverageCandlesChart';

export type UnifiedMode = 'spot' | 'leverage';

export interface UnifiedPriceChartProps {
  mode: UnifiedMode;
  // Spot (GMGN embed)
  chain?: string; // e.g., 'sol' | 'eth' | 'blast'
  tokenCA?: string; // contract address for spot
  // Leverage (Flash/HL) — for now placeholder until wired
  market?: string; // e.g., 'SOL-PERP'
  // Shared UI prefs
  theme?: GMGNTheme; // used directly for GMGN, can map later for leverage
  interval?: GMGNInterval; // GMGN set. We'll map for leverage later when wiring backend
  className?: string;
  height?: number | string;
}

const PlaceholderLeverageChart: React.FC<{ market?: string; height?: number | string }>
  = ({ market, height = 480 }) => (
  <div
    style={{
      height: typeof height === 'number' ? `${height}px` : height,
    }}
    className="w-full rounded border border-gray-700 bg-gray-900 text-gray-200 flex items-center justify-center"
  >
    <div className="p-4 text-center">
      <div className="text-sm opacity-75 mb-1">Leverage chart</div>
      <div className="text-lg font-semibold">{market || 'Select a market'}</div>
      <div className="text-xs opacity-60 mt-2">Candles will render here once wired to /api/ui/candles (mode=leverage)</div>
    </div>
  </div>
);

const UnifiedPriceChart: React.FC<UnifiedPriceChartProps> = ({
  mode,
  chain = 'sol',
  tokenCA,
  market,
  theme = 'dark',
  interval = '15',
  className,
  height = 480,
}) => {
  if (mode === 'spot') {
    if (!tokenCA) {
      return (
        <div className={`w-full ${className || ''}`}>
          <div
            style={{ height: typeof height === 'number' ? `${height}px` : height }}
            className="w-full rounded border border-gray-700 bg-gray-900 text-gray-300 flex items-center justify-center"
          >
            <div className="p-4 text-center">
              <div className="text-sm opacity-75 mb-1">Spot chart</div>
              <div className="text-lg font-semibold">Select a token</div>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className={`w-full ${className || ''}`}>
        <GMGNEmbeddedChart
          chain={chain}
          tokenCA={tokenCA}
          theme={theme}
          interval={interval}
          height={height}
        />
      </div>
    );
  }

  // mode === 'leverage'
  if (!market) {
    return (
      <div className={`w-full ${className || ''}`}>
        <PlaceholderLeverageChart market={market} height={height} />
      </div>
    );
  }

  return (
    <div className={`w-full ${className || ''}`}>
      <LeverageCandlesChart market={market} interval={interval} theme={theme} height={height} />
    </div>
  );
};

export default UnifiedPriceChart;
