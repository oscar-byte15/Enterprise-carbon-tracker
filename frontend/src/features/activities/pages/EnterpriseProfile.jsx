import { useEffect, useState } from "react";
import { getProfile, updateProfile } from "../services/authService";

const emptyProfile = {
  company_name: "",
  industry: "",
  address: "",
  city: "",
  state: "",
  postal_code: "",
  country: "",
  website: "",
  phone: "",
};

export default function EnterpriseProfile({ onNavigate }) {
  const [profile, setProfile] = useState(emptyProfile);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    async function loadProfile() {
      try {
        setLoading(true);
        const data = await getProfile();
        setProfile({
          company_name: data.company_name || "",
          industry: data.industry || "",
          address: data.address || "",
          city: data.city || "",
          state: data.state || "",
          postal_code: data.postal_code || "",
          country: data.country || "",
          website: data.website || "",
          phone: data.phone || "",
        });
      } catch (err) {
        setError(err.message || "Unable to load profile.");
      } finally {
        setLoading(false);
      }
    }

    loadProfile();
  }, []);

  function handleChange(event) {
    const { name, value } = event.target;
    setProfile((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSaving(true);
    setError("");
    setSuccess("");

    try {
      const payload = Object.fromEntries(
        Object.entries(profile).filter(([_, value]) => value !== "")
      );

      await updateProfile(payload);
      setSuccess("Enterprise profile updated successfully.");
    } catch (err) {
      setError(err.message || "Unable to update profile.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="auth-section">
      <div className="section-header-row">
        <div>
          <h2>Enterprise profile</h2>
          <p>Review and update your company information.</p>
        </div>
      </div>

      {loading ? (
        <div className="status-box">Loading profile...</div>
      ) : (
        <form className="profile-form" onSubmit={handleSubmit}>
          <div className="grid-two">
            <div className="field-group">
              <label htmlFor="company_name">Company name</label>
              <input id="company_name" name="company_name" value={profile.company_name} onChange={handleChange} />
            </div>

            <div className="field-group">
              <label htmlFor="industry">Industry</label>
              <input id="industry" name="industry" value={profile.industry} onChange={handleChange} />
            </div>
          </div>

          <div className="field-group">
            <label htmlFor="address">Address</label>
            <input id="address" name="address" value={profile.address} onChange={handleChange} />
          </div>

          <div className="grid-three">
            <div className="field-group">
              <label htmlFor="city">City</label>
              <input id="city" name="city" value={profile.city} onChange={handleChange} />
            </div>

            <div className="field-group">
              <label htmlFor="state">State</label>
              <input id="state" name="state" value={profile.state} onChange={handleChange} />
            </div>

            <div className="field-group">
              <label htmlFor="postal_code">Postal code</label>
              <input id="postal_code" name="postal_code" value={profile.postal_code} onChange={handleChange} />
            </div>
          </div>

          <div className="grid-two">
            <div className="field-group">
              <label htmlFor="country">Country</label>
              <input id="country" name="country" value={profile.country} onChange={handleChange} />
            </div>

            <div className="field-group">
              <label htmlFor="phone">Phone</label>
              <input id="phone" name="phone" value={profile.phone} onChange={handleChange} />
            </div>
          </div>

          <div className="field-group">
            <label htmlFor="website">Website</label>
            <input id="website" name="website" value={profile.website} onChange={handleChange} />
          </div>

          {error ? <div className="form-error">{error}</div> : null}
          {success ? <div className="form-success">{success}</div> : null}

          <div className="button-row">
            <button type="submit" className="primary-button" disabled={saving}>
              {saving ? "Saving..." : "Save changes"}
            </button>
            <button type="button" className="secondary-button" onClick={() => onNavigate?.("departments")}>
              Manage departments
            </button>
          </div>
        </form>
      )}
    </section>
  );
}
