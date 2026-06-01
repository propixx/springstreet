"use client";

import { useCallback, useEffect, useState } from "react";
import { getMetrics } from "@/lib/api";
import type { MetricsResponse, Ticker } from "@/types";

export function useMetrics(ticker: Ticker) {
  const [data, setData] = useState<MetricsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      setData(await getMetrics(ticker));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : `Unable to load ${ticker} metrics.`);
    } finally {
      setLoading(false);
    }
  }, [ticker]);

  useEffect(() => {
    void load();
  }, [load]);

  return { data, error, loading, refetch: load };
}
