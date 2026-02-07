import { useEffect, useRef } from 'react';

interface StockChartProps {
  ticker: string;
  height?: number;
  /** Show just the chart area, or include price info header */
  compact?: boolean;
}

/**
 * Embeds a TradingView Mini Symbol Overview widget.
 * Free, no API key, interactive, dark-themed.
 */
export default function StockChart({ ticker, height = 220, compact = false }: StockChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    // Clear any previous widget
    container.innerHTML = '';

    // Create the widget container structure TradingView expects
    const widgetDiv = document.createElement('div');
    widgetDiv.className = 'tradingview-widget-container__widget';
    container.appendChild(widgetDiv);

    const script = document.createElement('script');
    script.src =
      'https://s3.tradingview.com/external-embedding/embed-widget-symbol-overview.js';
    script.type = 'text/javascript';
    script.async = true;
    script.innerHTML = JSON.stringify({
      symbols: [[ticker]],
      chartOnly: compact,
      width: '100%',
      height: '100%',
      locale: 'en',
      colorTheme: 'dark',
      autosize: true,
      showVolume: false,
      showMA: false,
      hideDateRanges: false,
      hideMarketStatus: true,
      hideSymbolLogo: false,
      scalePosition: 'right',
      scaleMode: 'Normal',
      fontFamily:
        '-apple-system, BlinkMacSystemFont, Trebuchet MS, Roboto, Ubuntu, sans-serif',
      fontSize: '10',
      noTimeScale: false,
      valuesTracking: '1',
      changeMode: 'price-and-percent',
      chartType: 'area',
      lineWidth: 2,
      lineType: 0,
      dateRanges: ['1m|1D', '3m|1D', '12m|1W', 'all|1M'],
      dateFormat: 'dd MMM \'yy',
    });

    container.appendChild(script);

    return () => {
      // Clean up on unmount or ticker change
      if (container) container.innerHTML = '';
    };
  }, [ticker, compact]);

  return (
    <div
      ref={containerRef}
      className="tradingview-widget-container rounded-xl overflow-hidden border border-surface-light/30"
      style={{ height: `${height}px` }}
    />
  );
}
