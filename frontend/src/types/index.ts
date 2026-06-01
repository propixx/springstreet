export type Ticker = "AAPL" | "MSFT" | "AMZN" | "JPM" | "JNJ";

export interface OHLCDatum {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface TickerMetadata {
  name: string | null;
  sector: string | null;
  market_cap: number | null;
  pe_ratio: number | null;
  dividend_yield: number | null;
  "52w_high": number | null;
  "52w_low": number | null;
  current_price: number | null;
}

export interface OHLCResponse {
  ticker: Ticker;
  currency: string;
  data: OHLCDatum[];
  metadata: TickerMetadata;
}

export interface DayReturn {
  date: string;
  return_pct: number;
}

export interface Streak {
  direction: "up" | "down" | "flat";
  days: number;
}

export interface TickerMetrics {
  total_return_pct: number;
  annualized_return_pct: number;
  volatility_pct: number;
  sharpe_ratio: number | null;
  sortino_ratio: number | null;
  max_drawdown_pct: number;
  max_drawdown_start: string | null;
  max_drawdown_end: string | null;
  beta: number | null;
  avg_daily_volume: number;
  best_day: DayReturn | null;
  worst_day: DayReturn | null;
  positive_days_pct: number;
  current_streak: Streak;
}

export interface MetricsResponse {
  ticker: Ticker;
  metrics: TickerMetrics;
}

export type InsightSeverity = "positive" | "warning" | "negative" | "info";

export interface Insight {
  type: string;
  severity: InsightSeverity;
  title: string;
  description: string;
  metric_value: number | null;
}

export interface InsightsResponse {
  ticker: Ticker;
  insights: Insight[];
}

export interface PortfolioHolding {
  ticker: Ticker;
  weight: number;
  current_weight: number;
  investment: number;
  current_value: number;
  return_pct: number;
  contribution_pct: number;
}

export interface MonthlyReturn {
  month: string;
  return_pct: number;
}

export interface DailyPortfolioValue {
  date: string;
  value: number;
  AAPL: number;
  MSFT: number;
  AMZN: number;
  JPM: number;
  JNJ: number;
}

export interface PortfolioResponse {
  initial_investment: number;
  current_value: number;
  total_return_pct: number;
  annualized_return_pct: number;
  portfolio_sharpe: number | null;
  portfolio_max_drawdown_pct: number;
  portfolio_volatility_pct: number;
  portfolio_beta: number | null;
  holdings: PortfolioHolding[];
  daily_values: DailyPortfolioValue[];
  monthly_returns: MonthlyReturn[];
}
