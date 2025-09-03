import React, { useEffect, useMemo, useRef, useState } from 'react';
import { createChart, ColorType, IChartApi, UTCTimestamp, ISeriesApi } from 'lightweight-charts';
import MarketDataService, { Candle } from '../services/MarketDataService';

export type LeverageTheme = 'light' | 'dark';

export interface LeverageCandlesChartProps {
  market: string; // e.g., 'SOL-PERP'
  interval: string; // '1','5','15','60','240','720','1D'
  theme?: LeverageTheme;
  height?: number | string;
  className?: string;
}

const themeOptions = {
  light: {
    background: '#ffffff',
    text: '#191919',
    grid: '#e6e6e6',
    up: '#26a69a',
    down: '#ef5350',
  },
  dark: {
    background: '#1E1E1E',
    text: '#d9d9d9',
    grid: '#2b2b43',
    up: '#26a69a',
    down: '#ef5350',
  },
};

function toSeries(c: Candle) {
  return {
    time: Math.floor((c.ts > 1e12 ? c.ts / 1000 : c.ts)) as UTCTimestamp,
    open: c.open,
    high: c.high,
    low: c.low,
    close: c.close,
  };
}

const LeverageCandlesChart: React.FC<LeverageCandlesChartProps> = ({ market, interval, theme = 'dark', height = 480, className }) => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const [loading, setLoading] = useState(false);
  const colors = useMemo(() => themeOptions[theme], [theme]);

  useEffect(() => {
    if (!containerRef.current) return;

    if (chartRef.current) {
      chartRef.current.remove();
      chartRef.current = null;
      seriesRef.current = null;
    }

    const chart = createChart(containerRef.current, {
      layout: { background: { type: ColorType.Solid, color: colors.background }, textColor: colors.text },
      grid: { vertLines: { color: colors.grid }, horzLines: { color: colors.grid } },
      width: containerRef.current.clientWidth,
      height: typeof height === 'number' ? height : 480,
      timeScale: { timeVisible: true, secondsVisible: false },
    });

    const series = chart.addCandlestickSeries({
      upColor: colors.up,
      downColor: colors.down,
      borderVisible: false,
      wickUpColor: colors.up,
      wickDownColor: colors.down,
    });

    chartRef.current = chart;
    seriesRef.current = series;

    const onResize = () => {
      if (chartRef.current && containerRef.current) {
        chartRef.current.applyOptions({ width: containerRef.current.clientWidth });
      }
    };
    window.addEventListener('resize', onResize);
    return () => {
      window.removeEventListener('resize', onResize);
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }
    };
  }, [colors, height]);

  useEffect(() => {
    if (!market || !interval || !seriesRef.current) return;
    let cancelled = false;

    const load = async () => {
      try {
        setLoading(true);
        const rows = await MarketDataService.getCandles({ mode: 'leverage', market, interval });
        if (cancelled) return;
        const data = rows.map(toSeries);
        seriesRef.current!.setData(data);
        if (chartRef.current) chartRef.current.timeScale().fitContent();
      } catch (e) {
        // silent for now; UI wrapper can add error boundary
        // console.error('Leverage chart load error', e);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    load();

    // Optionally, refresh periodically (e.g., every 5s)
    const id = setInterval(load, 5000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, [market, interval]);

  return (
    <div className={`w-full relative ${className || ''}`}>
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/10 z-10">
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500" />
        </div>
      )}
      <div ref={containerRef} style={{ height: typeof height === 'number' ? `${height}px` : height }} />
    </div>
  );
};

export default LeverageCandlesChart;
