import { API_BASE_URL } from "@/lib/constants";
import type { InsightsResponse, MetricsResponse, OHLCResponse, PortfolioResponse, Ticker } from "@/types";

async function fetchJson<T>(path: string): Promise<T> {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`);
  } catch {
    throw new Error(`Could not reach the backend at ${API_BASE_URL}.`);
  }

  if (!response.ok) {
    let message = `API request failed with status ${response.status}.`;
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) {
        message = body.detail;
      }
    } catch {
      // Keep the status-based message if the response is not JSON.
    }
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export function getPortfolio() {
  return fetchJson<PortfolioResponse>("/api/portfolio");
}

export function getOHLC(ticker: Ticker) {
  return fetchJson<OHLCResponse>(`/api/ohlc/${ticker}`);
}

export function getMetrics(ticker: Ticker) {
  return fetchJson<MetricsResponse>(`/api/metrics/${ticker}`);
}

export function getInsights(ticker: Ticker) {
  return fetchJson<InsightsResponse>(`/api/insights/${ticker}`);
}
