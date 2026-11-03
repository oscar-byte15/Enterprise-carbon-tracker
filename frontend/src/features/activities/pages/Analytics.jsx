import { useEffect, useState } from "react";
import CategoryChart from "../components/CategoryChart";
import TrendChart from "../components/TrendChart";
import {
  getAnalyticsSummary,
  getAnalyticsTrends,
} from "../services/analyticsService";

const AVAILABLE_YEARS = ["", "2026", "2025", "2024"];

export default function Analytics({ onNavigate }) {
  const [summary, setSummary] = useState(null);
  const [trends, setTrends] = useState([]);
  const [selectedYear, setSelectedYear] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadData() {
      try {
        setLoading(true);
        setError("");

        const [summaryData, trendsData] = await Promise.all([
          getAnalyticsSummary(),
          getAnalyticsTrends(selectedYear ? Number(selectedYear) : null),
        ]);

        if (active) {
          setSummary(summaryData);
          setTrends(trendsData.trends || []);
        }
      } catch (err) {
        if (active) {
          setError(err.message || "Failed to load analytics visualizations.");
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadData();

    return () => {
      active = false;
    };
  }, [selectedYear]);

  const hasActivities = summary && summary.total_activities > 0;

  return (
    <section className="analytics-section">
      <div className="section-header-row">
        <div>
          <h2>Emissions Analytics & Trends</h2>
          <p>Visual breakdown of corporate emissions and monthly timeline progression.</p>
        </div>

        <div className="analytics-filter-group">
          <label htmlFor="analytics-year-filter">Year:</label>
          <select
            id="analytics-year-filter"
            value={selectedYear}
            onChange={(e) => setSelectedYear(e.target.value)}
            disabled={loading}
          >
            <option value="">All Years</option>
            <option value="2026">2026</option>
            <option value="2025">2025</option>
            <option value="2024">2024</option>
          </select>
        </div>
      </div>

      {loading && (
        <div className="status-box">Loading analytics visualizations...</div>
      )}

      {error && (
        <div className="form-error" role="alert">
          {error}
        </div>
      )}

      {!loading && !error && !hasActivities && (
        <div className="dashboard-empty-state">
          <div className="empty-icon" aria-hidden="true">📊</div>
          <h3>No activity data available for analytics</h3>
          <p>
            Log activities across electricity, heating, transport, or waste to
            generate visual trendlines and category breakdown charts.
          </p>
          <button
            type="button"
            className="primary-button"
            onClick={() => onNavigate?.("new")}
          >
            Log Carbon Activity
          </button>
        </div>
      )}

      {!loading && !error && hasActivities && (
        <div className="analytics-grid">
          {/* Monthly Trend Visual */}
          <div className="chart-card">
            <div className="chart-header">
              <div>
                <h3>Monthly Emissions Trend</h3>
                <span className="chart-subtitle">
                  Historical monthly totals ({selectedYear || "All recorded periods"})
                </span>
              </div>
              <span className="chart-badge">
                {trends.length} {trends.length === 1 ? "Period" : "Periods"}
              </span>
            </div>

            <TrendChart trends={trends} />
          </div>

          {/* Category Distribution Visual */}
          <div className="chart-card">
            <div className="chart-header">
              <div>
                <h3>Category Share Distribution</h3>
                <span className="chart-subtitle">
                  Proportion of overall carbon footprint by activity type
                </span>
              </div>
              <span className="chart-badge">
                Top: {summary?.top_category || "N/A"}
              </span>
            </div>

            <CategoryChart
              breakdown={summary?.category_breakdown || []}
              totalCo2e={summary?.total_co2e_kg || 0}
            />
          </div>
        </div>
      )}
    </section>
  );
}
