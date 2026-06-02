"use client";

import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import { TICKER_COLORS } from "@/lib/constants";
import { formatCurrency, formatPercent } from "@/lib/formatters";
import { SkeletonBlock, StatusBlock } from "@/components/StateViews";
import type { PortfolioResponse } from "@/types";

interface PortfolioChartsProps {
  portfolio: PortfolioResponse | null;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
}

export function PortfolioCharts({ portfolio, loading, error, onRetry }: PortfolioChartsProps) {
  if (loading) {
    return (
      <div className="portfolio-state">
        <SkeletonBlock rows={4} />
      </div>
    );
  }

  if (error) {
    return (
      <StatusBlock
        actionLabel="Retry portfolio charts"
        className="portfolio-state"
        message={error}
        onAction={onRetry}
        title="Could not load portfolio charts"
        tone="error"
      />
    );
  }

  if (!portfolio) {
    return (
      <StatusBlock
        className="portfolio-state"
        message="No portfolio data came back for these charts."
        title="Portfolio data is not available"
      />
    );
  }

  if (!portfolio.daily_values.length || !portfolio.holdings.length) {
    return (
      <StatusBlock
        className="portfolio-state"
        message="The portfolio response is missing daily values or holdings."
        title="Portfolio chart data is empty"
      />
    );
  }

  const allocationData = portfolio.holdings.map((holding) => ({
    ticker: holding.ticker,
    value: holding.current_value,
    percent: holding.current_weight * 100
  }));

  const holdingReturnData = portfolio.holdings.map((holding) => ({
    ticker: holding.ticker,
    return_pct: holding.return_pct,
    contribution_pct: holding.contribution_pct
  }));

  return (
    <section className="portfolio-section section" aria-label="Portfolio analytics">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Portfolio Analytics</p>
          <h2>Equal-weight portfolio</h2>
        </div>
        <p>
          The portfolio uses a $10,000 starting value split evenly across the
          five stocks so the results stay easy to explain.
        </p>
      </div>

      <div className="portfolio-chart-grid">
        <article className="panel chart-panel wide">
          <div className="panel-heading">
            <span>Growth</span>
            <strong>Portfolio Value</strong>
          </div>
          <div className="rechart-box">
            <ResponsiveContainer width="100%" height={280}>
              <AreaChart data={portfolio.daily_values}>
                <defs>
                  <linearGradient id="portfolioValue" x1="0" x2="0" y1="0" y2="1">
                    <stop offset="0%" stopColor="#15803d" stopOpacity={0.22} />
                    <stop offset="100%" stopColor="#15803d" stopOpacity={0.03} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="#e5e7eb" vertical={false} />
                <XAxis dataKey="date" minTickGap={36} stroke="#6b7280" tick={{ fontSize: 12 }} />
                <YAxis
                  domain={["dataMin", "dataMax"]}
                  stroke="#6b7280"
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value: number) => formatCurrency(value)}
                  width={76}
                />
                <Tooltip
                  contentStyle={tooltipStyle}
                  formatter={(value) => [formatCurrency(Number(value)), "Value"]}
                  labelFormatter={(label) => String(label)}
                />
                <Area
                  dataKey="value"
                  fill="url(#portfolioValue)"
                  isAnimationActive={false}
                  stroke="#15803d"
                  strokeWidth={2}
                  type="monotone"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </article>

        <article className="panel chart-panel">
          <div className="panel-heading">
            <span>Allocation</span>
            <strong>Current Weight</strong>
          </div>
          <div className="rechart-box">
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={allocationData}
                  dataKey="value"
                  innerRadius={64}
                  isAnimationActive={false}
                  nameKey="ticker"
                  outerRadius={94}
                  paddingAngle={2}
                >
                  {allocationData.map((item) => (
                    <Cell fill={TICKER_COLORS[item.ticker]} key={item.ticker} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={tooltipStyle}
                  formatter={(value, _name, item) => [
                    `${formatCurrency(Number(value))} (${Number(item.payload.percent).toFixed(1)}%)`,
                    "Value"
                  ]}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="chart-legend">
            {allocationData.map((item) => (
              <span key={item.ticker}>
                <i style={{ background: TICKER_COLORS[item.ticker] }} />
                {item.ticker} {item.percent.toFixed(1)}%
              </span>
            ))}
          </div>
        </article>

        <article className="panel chart-panel wide">
          <div className="panel-heading">
            <span>Holdings</span>
            <strong>Return by Stock</strong>
          </div>
          <div className="rechart-box">
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={holdingReturnData}>
                <CartesianGrid stroke="#e5e7eb" vertical={false} />
                <XAxis dataKey="ticker" stroke="#6b7280" tick={{ fontSize: 12 }} />
                <YAxis stroke="#6b7280" tick={{ fontSize: 12 }} tickFormatter={(value: number) => `${value}%`} />
                <Tooltip
                  contentStyle={tooltipStyle}
                  formatter={(value, name) => [formatPercent(Number(value)), name === "return_pct" ? "Return" : "Contribution"]}
                />
                <Bar dataKey="return_pct" isAnimationActive={false} radius={[6, 6, 0, 0]}>
                  {holdingReturnData.map((item) => (
                    <Cell fill={TICKER_COLORS[item.ticker]} key={item.ticker} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </article>

        <article className="panel chart-panel">
          <div className="panel-heading">
            <span>Drift</span>
            <strong>Weights vs Target</strong>
          </div>
          <div className="holding-list">
            {portfolio.holdings.map((holding) => (
              <div key={holding.ticker}>
                <span>{holding.ticker}</span>
                <strong>{(holding.current_weight * 100).toFixed(1)}%</strong>
                <small>target 20.0%</small>
              </div>
            ))}
          </div>
        </article>
      </div>
    </section>
  );
}

const tooltipStyle = {
  background: "#ffffff",
  border: "1px solid #e5e7eb",
  borderRadius: "8px",
  color: "#1f2937"
};
