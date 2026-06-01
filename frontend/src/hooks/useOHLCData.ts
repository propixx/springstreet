"use client";

import { useCallback, useEffect, useState } from "react";
import { getOHLC } from "@/lib/api";
import type { OHLCResponse, Ticker } from "@/types";

export function useOHLCData(ticker: Ticker) {
  const [data, setData] = useState<OHLCResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      setData(await getOHLC(ticker));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : `Unable to load ${ticker} prices.`);
    } finally {
      setLoading(false);
    }
  }, [ticker]);

  useEffect(() => {
    void load();
  }, [load]);

  return { data, error, loading, refetch: load };
}
