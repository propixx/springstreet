import type { Ticker } from "@/types";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const TICKERS: Ticker[] = ["AAPL", "MSFT", "AMZN", "JPM", "JNJ"];

export const TICKER_NAMES: Record<Ticker, string> = {
  AAPL: "Apple",
  MSFT: "Microsoft",
  AMZN: "Amazon",
  JPM: "JPMorgan Chase",
  JNJ: "Johnson & Johnson"
};

export const TICKER_COLORS: Record<Ticker, string> = {
  AAPL: "#2563eb",
  MSFT: "#15803d",
  AMZN: "#b7791f",
  JPM: "#7c3aed",
  JNJ: "#be185d"
};
