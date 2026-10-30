import { useEffect, useState } from "react";
import { createDepartment, listDepartments } from "../services/authService";

const initialForm = {
  name: "",
  description: "",
};

export default function Departments({ onNavigate }) {
  const [departments, setDepartments] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function loadDepartments() {
    try {
      setLoading(true);
      const result = await listDepartments();
      setDepartments(result.departments || []);
    } catch (err) {
      setError(err.message || "Unable to load departments.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDepartments();
  }, []);

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSaving(true);
    setError("");
    setSuccess("");

    try {
      await createDepartment(form);
      setForm(initialForm);
      setSuccess("Department created successfully.");
      await loadDepartments();
    } catch (err) {
      setError(err.message || "Unable to create department.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="auth-section">
      <div className="section-header-row">
        <div>
          <h2>Departments</h2>
          <p>Add and review the departments in your enterprise.</p>
        </div>
      </div>

      <div className="department-layout">
        <form className="profile-form" onSubmit={handleSubmit}>
          <div className="field-group">
            <label htmlFor="department-name">Department name</label>
            <input
              id="department-name"
              name="name"
              value={form.name}
              onChange={handleChange}
              placeholder="Operations"
              required
            />
          </div>

          <div className="field-group">
            <label htmlFor="department-description">Description</label>
            <textarea
              id="department-description"
              name="description"
              value={form.description}
              onChange={handleChange}
              rows="4"
              placeholder="Describe the department purpose"
            />
          </div>

          {error ? <div className="form-error">{error}</div> : null}
          {success ? <div className="form-success">{success}</div> : null}

          <div className="button-row">
            <button type="submit" className="primary-button" disabled={saving}>
              {saving ? "Saving..." : "Add department"}
            </button>
            <button type="button" className="secondary-button" onClick={() => onNavigate?.("enterprise")}>
              Back to profile
            </button>
          </div>
        </form>

        <div className="department-list">
          <h3>Current departments</h3>

          {loading ? (
            <div className="status-box">Loading departments...</div>
          ) : departments.length === 0 ? (
            <div className="status-box">No departments yet.</div>
          ) : (
            <ul>
              {departments.map((department) => (
                <li key={department.department_id} className="department-card">
                  <strong>{department.name}</strong>
                  {department.description ? <p>{department.description}</p> : null}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </section>
  );
}
