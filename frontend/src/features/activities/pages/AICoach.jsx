import { useEffect, useState } from "react";
import { getAIRecommendations } from "../services/aiService";

export default function AICoach({ onNavigate }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [refreshing, setRefreshing] = useState(false);

  async function loadRecommendations(isRefresh = false) {
    try {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      setError("");

      const result = await getAIRecommendations();
      setData(result);
    } catch (err) {
      setError(err.message || "Failed to load AI sustainability recommendations.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    loadRecommendations(false);
  }, []);

  const hasActivities = data && data.total_activities > 0;

  return (
    <section className="advisor-section">
      <div className="section-header-row">
        <div>
          <h2>AI Sustainability Advisor</h2>
          <p>
            Contextual carbon reduction strategies tailored to your enterprise emission footprint.
          </p>
        </div>

        <button
          type="button"
          className="secondary-button"
          onClick={() => loadRecommendations(true)}
          disabled={loading || refreshing}
        >
          {refreshing ? "Refreshing..." : "↻ Refresh Strategies"}
        </button>
      </div>

      {loading && (
        <div className="status-box">
          Analyzing corporate footprint and formulating strategic reduction advice...
        </div>
      )}

      {error && (
        <div className="form-error" role="alert">
          {error}
        </div>
      )}

      {!loading && !error && !hasActivities && (
        <div className="dashboard-empty-state">
          <div className="empty-icon" aria-hidden="true">🌱</div>
          <h3>No baseline emissions data available</h3>
          <p>
            The AI Advisor requires logged carbon operational data to formulate
            contextual reduction strategies. Log your first activity to unlock customized advice.
          </p>
          <button
            type="button"
            className="primary-button"
            onClick={() => onNavigate?.("new")}
          >
            Log Baseline Activity
          </button>
        </div>
      )}

      {!loading && !error && hasActivities && data && (
        <>
          {/* Executive Context Overview Card */}
          <div className="advisor-context-card">
            <div className="context-card-header">
              <div className="context-identity">
                <span className="context-company">{data.company_name}</span>
                <span className="context-industry">{data.industry}</span>
              </div>

              <div className="context-provenance">
                {data.is_fallback ? (
                  <span className="fallback-badge" title="Generated using rule-based sustainability catalog">
                    ⚡ Standard Catalogue
                  </span>
                ) : (
                  <span className="ai-badge" title="Generated via OpenAI LLM">
                    ✨ OpenAI ({data.model_used})
                  </span>
                )}
              </div>
            </div>

            <div className="context-metrics-row">
              <div className="context-metric">
                <span className="metric-label">Analyzed Footprint</span>
                <span className="metric-value">
                  {data.total_co2e_kg.toLocaleString(undefined, {
                    minimumFractionDigits: 1,
                    maximumFractionDigits: 2,
                  })}{" "}
                  kg CO2e
                </span>
              </div>

              <div className="context-metric">
                <span className="metric-label">Operational Events</span>
                <span className="metric-value">{data.total_activities} activities</span>
              </div>

              <div className="context-metric">
                <span className="metric-label">Primary Carbon Driver</span>
                <span className="metric-value highlight">
                  {data.top_category
                    ? data.top_category.charAt(0).toUpperCase() + data.top_category.slice(1)
                    : "None"}{" "}
                  ({data.top_category_percentage}%)
                </span>
              </div>
            </div>
          </div>

          {/* Concise Recommendation Cards Grid */}
          <div className="recommendations-container">
            <div className="recommendations-header">
              <h3>Priority Decarbonization Actions</h3>
              <p>Top operational measures to reduce your carbon footprint</p>
            </div>

            <div className="recommendations-grid">
              {data.recommendations.slice(0, 3).map((rec) => {
                const impactKey = (rec.impact || "Medium").toLowerCase();
                const impactClass =
                  impactKey === "high"
                    ? "impact-high"
                    : impactKey === "low"
                      ? "impact-low"
                      : "impact-medium";

                return (
                  <div key={rec.id} className="recommendation-card">
                    <div className="rec-card-top">
                      <span className="rec-category-badge">
                        {rec.category.toUpperCase()}
                      </span>
                      <span className={`impact-badge ${impactClass}`}>
                        {rec.impact} Impact
                      </span>
                    </div>

                    <h4 className="rec-title">{rec.title}</h4>
                    <p className="rec-action">{rec.action}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </>
      )}
    </section>
  );
}
