import React from 'react';

// Allowed themes and intervals per GMGN embed
export type GMGNTheme = 'light' | 'dark';
export type GMGNInterval = '1S' | '1' | '5' | '15' | '60' | '240' | '720' | '1D';

export interface GMGNEmbeddedChartProps {
  chain: 'sol' | 'eth' | 'blast' | string; // keep flexible in case GMGN adds more
  tokenCA: string;
  theme?: GMGNTheme;
  interval?: GMGNInterval;
  className?: string;
  style?: React.CSSProperties;
  // Dimensions (responsive by default via style, but allow explicit control)
  width?: string | number;
  height?: string | number;
  // For accessibility and testing
  title?: string;
}

const BASE = 'https://www.gmgn.cc/kline';

function sanitizeInterval(v?: string): GMGNInterval {
  const allowed: GMGNInterval[] = ['1S', '1', '5', '15', '60', '240', '720', '1D'];
  if (!v) return '15';
  const vv = v.toUpperCase();
  // Normalize common aliases
  const alias: Record<string, GMGNInterval> = {
    '1M': '1',
    '5M': '5',
    '15M': '15',
    '1H': '60',
    '4H': '240',
    '12H': '720',
    'D': '1D',
    '1D': '1D',
    'S': '1S',
  };
  const mapped = (alias[vv] as GMGNInterval) || (vv as GMGNInterval);
  return (allowed as string[]).includes(mapped) ? mapped : '15';
}

function sanitizeTheme(v?: string): GMGNTheme {
  return v === 'dark' ? 'dark' : 'light';
}

export const GMGNEmbeddedChart: React.FC<GMGNEmbeddedChartProps> = ({
  chain,
  tokenCA,
  theme = 'light',
  interval = '15',
  className,
  style,
  width = '100%',
  height = 480,
  title = 'GMGN Price Chart',
}) => {
  const t = sanitizeTheme(theme);
  const i = sanitizeInterval(interval);
  const src = `${BASE}/${encodeURIComponent(chain)}/${encodeURIComponent(tokenCA)}?theme=${t}&interval=${i}`;

  return (
    <iframe
      src={src}
      title={title}
      className={className}
      style={{
        border: 'none',
        width: typeof width === 'number' ? `${width}px` : width,
        height: typeof height === 'number' ? `${height}px` : height,
        borderRadius: 8,
        ...style,
      }}
      // Ensure safe embedding
      sandbox="allow-same-origin allow-scripts allow-popups allow-forms"
      loading="lazy"
    />
  );
};

export default GMGNEmbeddedChart;
