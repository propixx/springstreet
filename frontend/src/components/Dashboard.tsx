"use client";

import { useMemo, useState } from "react";
import { useInsights } from "@/hooks/useInsights";
import { useMetrics } from "@/hooks/useMetrics";
import { useOHLCData } from "@/hooks/useOHLCData";
import { usePortfolio } from "@/hooks/usePortfolio";
import { TICKERS, TICKER_NAMES } from "@/lib/constants";
import { formatCurrency, formatNumber, formatPercent, formatPrice } from "@/lib/formatters";
import { InsightsPanel } from "@/components/InsightsPanel";
import { OHLCChart } from "@/components/OHLCChart";
import { PortfolioCharts } from "@/components/PortfolioCharts";
import { SkeletonBlock, SkeletonValue, StatusBlock } from "@/components/StateViews";
import type { Ticker } from "@/types";

export function Dashboard() {
  const [selectedTicker, setSelectedTicker] = useState<Ticker>("AAPL");
  const portfolio = usePortfolio();
  const ohlc = useOHLCData(selectedTicker);
  const metrics = useMetrics(selectedTicker);
  const insights = useInsights(selectedTicker);

  const latestPrice = useMemo(() => {
    if (!ohlc.data?.data.length) {
      return null;
    }

    return ohlc.data.data[ohlc.data.data.length - 1];
  }, [ohlc.data]);

  return (
    <>
      <section className="hero section">
        <div>
          <p className="eyebrow">Spring Street Internship Assignment</p>
          <h1>Market Insights Dashboard</h1>
          <p className="hero-copy">
            Built to visualize OHLC data, compare a simple portfolio, and
            understand basic risk-return metrics.
          </p>
        </div>

        <div className="ticker-strip" aria-label="Select ticker">
          {TICKERS.map((ticker) => (
            <button
              className={ticker === selectedTicker ? "active" : ""}
              key={ticker}
              onClick={() => setSelectedTicker(ticker)}
              type="button"
            >
              {ticker}
            </button>
          ))}
        </div>
      </section>

      <section className="metric-grid section" aria-label="Portfolio summary">
        <article className="metric-card">
          <span>Portfolio Value</span>
          <strong>{portfolio.loading ? <SkeletonValue /> : formatCurrency(portfolio.data?.current_value)}</strong>
          <small>{portfolio.error ?? `${formatPercent(portfolio.data?.total_return_pct)} total return`}</small>
        </article>
        <article className="metric-card">
          <span>Annualized Return</span>
          <strong>{portfolio.loading ? <SkeletonValue /> : formatPercent(portfolio.data?.annualized_return_pct)}</strong>
          <small>Equal-weight portfolio, $10,000 starting capital</small>
        </article>
        <article className="metric-card">
          <span>Sharpe Ratio</span>
          <strong>{portfolio.loading ? <SkeletonValue /> : (portfolio.data?.portfolio_sharpe ?? "N/A")}</strong>
          <small>Risk-adjusted return, using a 4.5% risk-free rate</small>
        </article>
        <article className="metric-card">
          <span>Max Drawdown</span>
          <strong>{portfolio.loading ? <SkeletonValue /> : formatPercent(portfolio.data?.portfolio_max_drawdown_pct)}</strong>
          <small>Worst peak-to-trough portfolio decline</small>
        </article>
      </section>

      <section className="dashboard-grid section" aria-label="Dashboard data">
        <article className="panel panel-large">
          <div className="panel-heading">
            <span>OHLC Chart</span>
            <strong>
              {selectedTicker} {TICKER_NAMES[selectedTicker]}
            </strong>
          </div>
          <div className="chart-frame">
            <OHLCChart
              data={ohlc.data?.data ?? []}
              error={ohlc.error}
              loading={ohlc.loading}
              onRetry={ohlc.refetch}
              ticker={selectedTicker}
            />
            <div className="price-summary compact">
              <div>
                <span>Last</span>
                <strong>{latestPrice?.date ?? "N/A"}</strong>
              </div>
              <div>
                <span>Open</span>
                <strong>{formatPrice(latestPrice?.open)}</strong>
              </div>
              <div>
                <span>High</span>
                <strong>{formatPrice(latestPrice?.high)}</strong>
              </div>
              <div>
                <span>Low</span>
                <strong>{formatPrice(latestPrice?.low)}</strong>
              </div>
              <div>
                <span>Volume</span>
                <strong>{formatNumber(latestPrice?.volume)}</strong>
              </div>
            </div>
          </div>
        </article>

        <article className="panel">
          <div className="panel-heading">
            <span>Portfolio</span>
            <strong>Holdings</strong>
          </div>
          {portfolio.error ? (
            <StatusBlock
              actionLabel="Retry portfolio"
              message={portfolio.error}
              onAction={portfolio.refetch}
              title="Could not load holdings"
              tone="error"
            />
          ) : portfolio.loading ? (
            <SkeletonBlock rows={5} />
          ) : portfolio.data?.holdings.length ? (
            <div className="holding-list">
              {portfolio.data.holdings.slice(0, 5).map((holding) => (
                <div key={holding.ticker}>
                  <span>{holding.ticker}</span>
                  <strong>{formatCurrency(holding.current_value)}</strong>
                  <small>{formatPercent(holding.return_pct)}</small>
                </div>
              ))}
            </div>
          ) : (
            <StatusBlock message="The portfolio response did not include any holdings." title="No holdings available" />
          )}
        </article>

        <article className="panel">
          <div className="panel-heading">
            <span>Risk Snapshot</span>
            <strong>{selectedTicker}</strong>
          </div>
          {metrics.error ? (
            <StatusBlock
              actionLabel="Retry metrics"
              message={metrics.error}
              onAction={metrics.refetch}
              title={`Could not load ${selectedTicker} metrics`}
              tone="error"
            />
          ) : metrics.loading ? (
            <SkeletonBlock rows={4} />
          ) : metrics.data ? (
            <dl className="stat-list">
              <div>
                <dt>Total Return</dt>
                <dd>{formatPercent(metrics.data.metrics.total_return_pct)}</dd>
              </div>
              <div>
                <dt>Volatility</dt>
                <dd>{formatPercent(metrics.data.metrics.volatility_pct)}</dd>
              </div>
              <div>
                <dt>Sharpe</dt>
                <dd>{metrics.data.metrics.sharpe_ratio ?? "N/A"}</dd>
              </div>
              <div>
                <dt>Max Drawdown</dt>
                <dd>{formatPercent(metrics.data.metrics.max_drawdown_pct)}</dd>
              </div>
            </dl>
          ) : (
            <StatusBlock message="No metric values came back for this ticker." title="No metrics available" />
          )}
        </article>
      </section>

      <PortfolioCharts
        error={portfolio.error}
        loading={portfolio.loading}
        onRetry={portfolio.refetch}
        portfolio={portfolio.data}
      />
      <InsightsPanel
        error={insights.error}
        loading={insights.loading}
        onRetry={insights.refetch}
        portfolio={portfolio.data}
        ticker={selectedTicker}
        tickerInsights={insights.data?.insights ?? []}
      />
    </>
  );
}
