"use client";

import { useEffect, useMemo, useRef } from "react";
import {
  CandlestickSeries,
  ColorType,
  createChart,
  HistogramSeries,
  type CandlestickData,
  type HistogramData,
  type Time
} from "lightweight-charts";
import { SkeletonBlock, StatusBlock } from "@/components/StateViews";
import type { OHLCDatum, Ticker } from "@/types";

interface OHLCChartProps {
  data: OHLCDatum[];
  loading: boolean;
  error: string | null;
  onRetry: () => void;
  ticker: Ticker;
}

export function OHLCChart({ data, loading, error, onRetry, ticker }: OHLCChartProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  const candleData = useMemo<CandlestickData<Time>[]>(
    () =>
      data.map((point) => ({
        time: point.date,
        open: point.open,
        high: point.high,
        low: point.low,
        close: point.close
      })),
    [data]
  );

  const volumeData = useMemo<HistogramData<Time>[]>(
    () =>
      data.map((point) => ({
        time: point.date,
        value: point.volume,
        color: point.close >= point.open ? "rgba(54, 211, 153, 0.38)" : "rgba(255, 107, 107, 0.38)"
      })),
    [data]
  );

  useEffect(() => {
    if (!containerRef.current || !candleData.length) {
      return;
    }

    const container = containerRef.current;
    const chart = createChart(container, {
      width: container.clientWidth,
      height: 430,
      layout: {
        background: { type: ColorType.Solid, color: "#161d23" },
        textColor: "#98a7a3"
      },
      grid: {
        vertLines: { color: "rgba(255, 255, 255, 0.05)" },
        horzLines: { color: "rgba(255, 255, 255, 0.05)" }
      },
      rightPriceScale: {
        borderColor: "rgba(255, 255, 255, 0.12)"
      },
      timeScale: {
        borderColor: "rgba(255, 255, 255, 0.12)",
        timeVisible: false
      },
      crosshair: {
        mode: 1
      }
    });

    const candles = chart.addSeries(CandlestickSeries, {
      upColor: "#36d399",
      downColor: "#ff6b6b",
      borderUpColor: "#36d399",
      borderDownColor: "#ff6b6b",
      wickUpColor: "#36d399",
      wickDownColor: "#ff6b6b"
    });

    const volume = chart.addSeries(
      HistogramSeries,
      {
        priceFormat: { type: "volume" },
        priceScaleId: "",
        lastValueVisible: false,
        priceLineVisible: false
      },
      1
    );

    candles.setData(candleData);
    volume.setData(volumeData);
    chart.timeScale().fitContent();

    const resizeObserver = new ResizeObserver(([entry]) => {
      chart.applyOptions({
        width: Math.floor(entry.contentRect.width)
      });
    });

    resizeObserver.observe(container);

    return () => {
      resizeObserver.disconnect();
      chart.remove();
    };
  }, [candleData, volumeData]);

  if (loading) {
    return (
      <div className="chart-state">
        <SkeletonBlock rows={5} />
      </div>
    );
  }

  if (error) {
    return (
      <StatusBlock
        actionLabel="Retry price data"
        className="chart-state"
        message={error}
        onAction={onRetry}
        title={`Could not load ${ticker} prices`}
        tone="error"
      />
    );
  }

  if (!data.length) {
    return (
      <StatusBlock
        className="chart-state"
        message="The backend returned an empty price series for this ticker."
        title={`No price data for ${ticker}`}
      />
    );
  }

  return <div ref={containerRef} className="ohlc-chart" aria-label={`${ticker} candlestick chart`} />;
}
