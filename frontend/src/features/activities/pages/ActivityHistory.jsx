
import { useEffect, useState } from "react";
import {
  getActivities,
  deleteActivity,
} from "../services/activityService";
import "./ActivityHistory.css";

export default function ActivityHistory({ onEdit }) {
  const [activities, setActivities] = useState([]);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [deletingId, setDeletingId] = useState(null);

  // Load activities from FastAPI
  useEffect(() => {
    let active = true;

    async function loadActivities() {
      try {
        setLoading(true);
        setError("");

        const data = await getActivities();

        if (active) {
          setActivities(data);
        }
      } catch (err) {
        if (active) {
          setError(
            err.message || "Unable to load activities."
          );
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadActivities();

    return () => {
      active = false;
    };
  }, []);

  // Delete from FastAPI and update local state
  async function handleDelete(id) {
    const confirmed = window.confirm(
      "Are you sure you want to delete this activity?"
    );

    if (!confirmed) return;

    try {
      setDeletingId(id);
      setError("");

      await deleteActivity(id);

      setActivities((previous) =>
        previous.filter((activity) => activity.id !== id)
      );
    } catch (err) {
      setError(
        err.message || "Unable to delete activity."
      );
    } finally {
      setDeletingId(null);
    }
  }

  // Search and category filtering
  const filteredActivities = activities.filter((activity) => {
    const query = search.toLowerCase().trim();

    const matchesSearch = [
      activity.type,
      activity.category,
      activity.date,
    ].some((value) =>
      String(value || "").toLowerCase().includes(query)
    );

    const matchesCategory =
      category === "all" ||
      activity.category === category;

    return matchesSearch && matchesCategory;
  });

  const formatCategory = (value) =>
    value
      ? value.charAt(0).toUpperCase() + value.slice(1)
      : "Unknown";

  return (
    <div className="activity-history">
      <div className="history-heading">
        <div className="history-title-group">
          <div className="history-eyebrow">
            CARBON ACTIVITY MANAGEMENT
          </div>
          <h2>Activity Records</h2>
          <p>
            Track, search and manage your enterprise
            carbon activities in one place.
          </p>
        </div>

        <div className="history-stat">
          <span className="history-stat-number">
            {activities.length}
          </span>
          <span className="history-stat-label">
            Total activities
          </span>
        </div>
      </div>

      <div className="history-toolbar">
        <div className="history-search">
          <span
            className="history-search-icon"
            aria-hidden="true"
          >
            ⌕
          </span>
          <input
            type="search"
            aria-label="Search activities"
            placeholder="Search by activity, category or date..."
            value={search}
            onChange={(event) =>
              setSearch(event.target.value)
            }
          />
        </div>

        <div className="history-select-wrapper">
          <label htmlFor="history-category">
            Category
          </label>
          <select
            id="history-category"
            value={category}
            onChange={(event) =>
              setCategory(event.target.value)
            }
          >
            <option value="all">All categories</option>
            <option value="electricity">Electricity</option>
            <option value="heating">Heating</option>
            <option value="transport">Transport</option>
            <option value="waste">Waste</option>
          </select>
        </div>
      </div>

      <div className="history-results">
        <span>
          Showing{" "}
          <strong>{filteredActivities.length}</strong>{" "}
          of <strong>{activities.length}</strong>{" "}
          activities
        </span>

        {(search || category !== "all") && (
          <button
            type="button"
            className="history-clear-btn"
            onClick={() => {
              setSearch("");
              setCategory("all");
            }}
          >
            Clear filters
          </button>
        )}
      </div>

      {error && (
        <div className="history-error" role="alert">
          {error}
        </div>
      )}

      {loading ? (
        <div className="history-loading" role="status">
          <div className="history-spinner" />
          <p>Loading your activities...</p>
        </div>
      ) : (
        <div className="history-table-wrapper">
          <table className="history-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Category</th>
                <th>Activity Type</th>
                <th>Amount</th>
                <th>CO₂e</th>
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>
              {filteredActivities.map((activity) => (
                <tr key={activity.id}>
                  <td className="history-date">
                    {activity.date || "—"}
                  </td>

                  <td>
                    <span
                      className={
                        `history-category-badge ${
                          activity.category || ""
                        }`
                      }
                    >
                      <span className="badge-dot" />
                      {formatCategory(activity.category)}
                    </span>
                  </td>

                  <td className="history-activity-type">
                    {activity.type || "—"}
                  </td>

                  <td className="history-amount">
                    <strong>
                      {activity.amount ?? "—"}
                    </strong>{" "}
                    <span>{activity.unit || ""}</span>
                  </td>

                  <td className="history-emissions">
                    {activity.co2e_kg != null ? (
                      <>
                        <strong>
                          {Number(
                            activity.co2e_kg
                          ).toFixed(2)}
                        </strong>
                        <span> kg CO₂e</span>
                      </>
                    ) : (
                      "—"
                    )}
                  </td>

                  <td>
                    <div className="history-actions">
                      <button
                        type="button"
                        className="history-edit-btn"
                        onClick={() => onEdit(activity)}
                      >
                        Edit
                      </button>

                      <button
                        type="button"
                        className="history-delete-btn"
                        disabled={deletingId !== null}
                        onClick={() =>
                          handleDelete(activity.id)
                        }
                      >
                        {deletingId === activity.id
                          ? "Deleting..."
                          : "Delete"}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}

              {filteredActivities.length === 0 && (
                <tr>
                  <td
                    colSpan={6}
                    className="history-empty"
                  >
                    <div className="history-empty-content">
                      <span className="history-empty-icon">
                        ◫
                      </span>
                      <h3>No activities found</h3>
                      <p>
                        {activities.length === 0
                          ? "Your registered carbon activities will appear here."
                          : "Try adjusting your search or category filter."}
                      </p>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      <div className="history-footer">
        <span>
          Enterprise Carbon Tracker
        </span>
        <span>
          Activity Management · Subsystem 2
        </span>
      </div>
    </div>
  );
}
