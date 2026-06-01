"use client";

import { SkeletonBlock, StatusBlock } from "@/components/StateViews";
import { formatPercent } from "@/lib/formatters";
import type { Insight, InsightSeverity, PortfolioResponse, Ticker } from "@/types";

interface InsightsPanelProps {
  ticker: Ticker;
  tickerInsights: Insight[];
  portfolio: PortfolioResponse | null;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
}

interface DisplayInsight {
  id: string;
  source: string;
  severity: InsightSeverity;
  title: string;
  description: string;
}

export function InsightsPanel({ ticker, tickerInsights, portfolio, loading, error, onRetry }: InsightsPanelProps) {
  const portfolioInsights = buildPortfolioInsights(portfolio);

  return (
    <section className="insights-section section" aria-label="Market insights">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Insights</p>
          <h2>Notes from the calculations</h2>
        </div>
        <p>
          These notes are rule-based so each one can be traced back to a
          metric in the dashboard.
        </p>
      </div>

      <div className="insight-grid">
        <article className="panel insight-panel">
          <div className="panel-heading">
            <span>Ticker</span>
            <strong>{ticker}</strong>
          </div>
          {loading ? (
            <SkeletonBlock rows={4} />
          ) : error ? (
            <StatusBlock
              actionLabel="Retry insights"
              message={error}
              onAction={onRetry}
              title={`Could not load ${ticker} insights`}
              tone="error"
            />
          ) : tickerInsights.length === 0 ? (
            <StatusBlock message="No rule-based notes came back for this ticker." title="No ticker insights available" />
          ) : (
            <div className="insight-list">
              {tickerInsights.map((insight) => (
                <InsightCard
                  insight={{
                    id: `${ticker}-${insight.type}`,
                    source: insight.type,
                    severity: insight.severity,
                    title: insight.title,
                    description: insight.description
                  }}
                  key={`${ticker}-${insight.type}`}
                />
              ))}
            </div>
          )}
        </article>

        <article className="panel insight-panel">
          <div className="panel-heading">
            <span>Portfolio</span>
            <strong>Basket Notes</strong>
          </div>
          {!portfolio ? (
            <StatusBlock message="Portfolio notes will appear once the basket data loads." title="Waiting for portfolio data" />
          ) : portfolioInsights.length === 0 ? (
            <StatusBlock message="The portfolio response did not include enough holdings to summarize." title="No portfolio insights available" />
          ) : (
            <div className="insight-list">
              {portfolioInsights.map((insight) => (
                <InsightCard insight={insight} key={insight.id} />
              ))}
            </div>
          )}
        </article>
      </div>
    </section>
  );
}

function InsightCard({ insight }: { insight: DisplayInsight }) {
  return (
    <article className={`insight-card ${insight.severity}`}>
      <div>
        <span>{insight.source}</span>
        <strong>{insight.title}</strong>
      </div>
      <p>{insight.description}</p>
    </article>
  );
}

function buildPortfolioInsights(portfolio: PortfolioResponse | null): DisplayInsight[] {
  if (!portfolio || !portfolio.holdings.length) {
    return [];
  }

  const bestHolding = [...portfolio.holdings].sort((a, b) => b.return_pct - a.return_pct)[0];
  const worstHolding = [...portfolio.holdings].sort((a, b) => a.return_pct - b.return_pct)[0];
  const largestDrift = [...portfolio.holdings].sort(
    (a, b) => Math.abs(b.current_weight - b.weight) - Math.abs(a.current_weight - a.weight)
  )[0];

  return [
    {
      id: "portfolio-sharpe",
      source: "risk",
      severity: portfolio.portfolio_sharpe != null && portfolio.portfolio_sharpe >= 1 ? "positive" : "info",
      title: "Risk-Adjusted Return",
      description: `The portfolio Sharpe ratio is ${portfolio.portfolio_sharpe ?? "N/A"}, with annualized volatility of ${formatPercent(portfolio.portfolio_volatility_pct)}.`
    },
    {
      id: "portfolio-best-worst",
      source: "performance",
      severity: "info",
      title: "Best and Worst Holdings",
      description: `${bestHolding.ticker} is the best performer at ${formatPercent(bestHolding.return_pct)}, while ${worstHolding.ticker} is the lowest at ${formatPercent(worstHolding.return_pct)}.`
    },
    {
      id: "portfolio-drift",
      source: "allocation",
      severity: Math.abs(largestDrift.current_weight - largestDrift.weight) > 0.04 ? "warning" : "info",
      title: "Allocation Drift",
      description: `${largestDrift.ticker} has moved from ${formatPercent(largestDrift.weight * 100)} target weight to ${formatPercent(largestDrift.current_weight * 100)}.`
    }
  ];
}
