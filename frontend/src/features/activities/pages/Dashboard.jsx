import { useEffect, useState } from "react";
import KPICard from "../components/KPICard";
import { getAnalyticsSummary } from "../services/analyticsService";

export default function Dashboard({ onNavigate }) {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadSummary() {
      try {
        setLoading(true);
        setError("");
        const data = await getAnalyticsSummary();
        if (active) {
          setSummary(data);
        }
      } catch (err) {
        if (active) {
          setError(err.message || "Failed to load dashboard metrics.");
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadSummary();

    return () => {
      active = false;
    };
  }, []);

  return (
    <section className="dashboard-section">
      <div className="section-header-row">
        <div>
          <h2>Executive Dashboard</h2>
          <p>Real-time carbon footprint overview and key performance metrics.</p>
        </div>
        <button
          type="button"
          className="secondary-button"
          onClick={() => onNavigate?.("new")}
        >
          + Log Activity
        </button>
      </div>

      {loading && (
        <div className="status-box">Loading analytics summary...</div>
      )}

      {error && (
        <div className="form-error" role="alert">
          {error}
        </div>
      )}

      {!loading && !error && summary && summary.total_activities === 0 && (
        <div className="dashboard-empty-state">
          <div className="empty-icon" aria-hidden="true">🌱</div>
          <h3>No activity data logged yet</h3>
          <p>
            Start tracking your enterprise greenhouse gas emissions by logging
            your first energy, fuel, or waste activity.
          </p>
          <button
            type="button"
            className="primary-button"
            onClick={() => onNavigate?.("new")}
          >
            Log First Carbon Activity
          </button>
        </div>
      )}

      {!loading && !error && summary && summary.total_activities > 0 && (
        <>
          <div className="kpi-grid">
            <KPICard
              title="Total Emissions"
              value={`${summary.total_co2e_kg.toLocaleString(undefined, {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })} kg`}
              subtitle="All-time verified CO2e footprint"
              badge="All-time"
              icon="🌍"
            />

            <KPICard
              title="Total Activities"
              value={summary.total_activities}
              subtitle="Logged operational events"
              icon="📋"
            />

            <KPICard
              title="Top Emission Category"
              value={
                summary.top_category
                  ? summary.top_category.charAt(0).toUpperCase() +
                    summary.top_category.slice(1)
                  : "—"
              }
              subtitle="Primary emission driver"
              icon="⚡"
            />

            <KPICard
              title="Top Category Share"
              value={`${summary.top_category_percentage}%`}
              subtitle={`Proportion of total footprint`}
              icon="📊"
            />
          </div>

          <div className="breakdown-card">
            <div className="breakdown-header">
              <h3>Category Breakdown</h3>
              <span className="breakdown-subtitle">
                Distribution across recorded operational categories
              </span>
            </div>

            <ul className="breakdown-list">
              {summary.category_breakdown.map((item) => (
                <li key={item.category} className="breakdown-item">
                  <div className="breakdown-item-top">
                    <span className="breakdown-category">
                      {item.category.charAt(0).toUpperCase() +
                        item.category.slice(1)}
                    </span>
                    <div className="breakdown-stats">
                      <span className="breakdown-co2">
                        {item.co2e_kg.toLocaleString(undefined, {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        })}{" "}
                        kg CO2e
                      </span>
                      <span className="breakdown-percentage">
                        {item.percentage}%
                      </span>
                    </div>
                  </div>

                  <div
                    className="breakdown-bar-track"
                    role="progressbar"
                    aria-valuenow={item.percentage}
                    aria-valuemin="0"
                    aria-valuemax="100"
                  >
                    <div
                      className="breakdown-bar-fill"
                      style={{ width: `${Math.min(item.percentage, 100)}%` }}
                    />
                  </div>

                  <div className="breakdown-count">
                    {item.activity_count}{" "}
                    {item.activity_count === 1 ? "activity" : "activities"}
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </>
      )}
    </section>
  );
}
