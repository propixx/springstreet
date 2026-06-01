"use client";

import { useCallback, useEffect, useState } from "react";
import { getInsights } from "@/lib/api";
import type { InsightsResponse, Ticker } from "@/types";

export function useInsights(ticker: Ticker) {
  const [data, setData] = useState<InsightsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      setData(await getInsights(ticker));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : `Unable to load ${ticker} insights.`);
    } finally {
      setLoading(false);
    }
  }, [ticker]);

  useEffect(() => {
    void load();
  }, [load]);

  return { data, error, loading, refetch: load };
}
