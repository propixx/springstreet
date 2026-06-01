"use client";

import { useCallback, useEffect, useState } from "react";
import { getPortfolio } from "@/lib/api";
import type { PortfolioResponse } from "@/types";

export function usePortfolio() {
  const [data, setData] = useState<PortfolioResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      setData(await getPortfolio());
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to load portfolio data.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return { data, error, loading, refetch: load };
}
