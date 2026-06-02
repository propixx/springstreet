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
        color: point.close >= point.open ? "rgba(21, 128, 61, 0.26)" : "rgba(220, 38, 38, 0.24)"
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
        background: { type: ColorType.Solid, color: "#ffffff" },
        textColor: "#6b7280"
      },
      grid: {
        vertLines: { color: "rgba(229, 231, 235, 0.72)" },
        horzLines: { color: "rgba(229, 231, 235, 0.72)" }
      },
      rightPriceScale: {
        borderColor: "#e5e7eb"
      },
      timeScale: {
        borderColor: "#e5e7eb",
        timeVisible: false
      },
      crosshair: {
        mode: 1
      }
    });

    const candles = chart.addSeries(CandlestickSeries, {
      upColor: "#15803d",
      downColor: "#dc2626",
      borderUpColor: "#15803d",
      borderDownColor: "#dc2626",
      wickUpColor: "#15803d",
      wickDownColor: "#dc2626"
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
