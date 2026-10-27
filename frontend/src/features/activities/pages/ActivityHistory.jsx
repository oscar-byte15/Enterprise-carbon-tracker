
import { useEffect, useState } from "react";
import {
  getActivities,
  deleteActivity,
} from "../services/activityStorage";

export default function ActivityHistory({ onEdit }) {
  const [activities, setActivities] = useState([]);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("all");

  // Load activities from localStorage
  useEffect(() => {
    setActivities(getActivities());
  }, []);

  // Delete an activity
  function handleDelete(id) {
    const confirmed = window.confirm(
      "Are you sure you want to delete this activity?"
    );

    if (!confirmed) return;

    deleteActivity(id);
    setActivities(getActivities());
  }

  // Filter activities by type and category
  const filteredActivities = activities.filter((activity) => {
    const matchesSearch = String(
      activity.type || ""
    )
      .toLowerCase()
      .includes(search.toLowerCase());

    const matchesCategory =
      category === "all" || activity.category === category;

    return matchesSearch && matchesCategory;
  });

  return (
    <div className="activity-history">
      <div className="history-heading">
        <div>
          <h2>Activity Records</h2>
          <p>Review and manage registered carbon activities.</p>
        </div>

        <span className="history-count">
          {activities.length} activities
        </span>
      </div>

      {/* Search and category filters */}
      <div className="history-filters">
        <input
          type="search"
          placeholder="Search activity type..."
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />

        <select
          value={category}
          onChange={(event) => setCategory(event.target.value)}
        >
          <option value="all">All categories</option>
          <option value="electricity">Electricity</option>
          <option value="heating">Heating</option>
          <option value="transport">Transport</option>
          <option value="waste">Waste</option>
        </select>
      </div>

      {/* Activities table */}
      <div className="history-table-wrapper">
        <table className="history-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Category</th>
              <th>Activity Type</th>
              <th>Amount</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody>
            {filteredActivities.map((activity) => (
              <tr key={activity.id}>
                <td>
                  {activity.date ||
                    activity.activityDate ||
                    "—"}
                </td>

                <td>{activity.category || "—"}</td>

                <td>{activity.type || "—"}</td>

                <td>
                  {activity.amount ??
                    activity.quantity ??
                    "—"}{" "}
                  {activity.unit || ""}
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
                      onClick={() => handleDelete(activity.id)}
                    >
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            ))}

            {filteredActivities.length === 0 && (
              <tr>
                <td colSpan={5} className="history-empty">
                  No activities found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
