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
  AAPL: "#4fb3ff",
  MSFT: "#36d399",
  AMZN: "#f4b860",
  JPM: "#7aa2ff",
  JNJ: "#ff7ab6"
};
