import { useState } from "react";
import AuthCard from "../components/AuthCard";
import { register } from "../services/authService";

const initialForm = {
  email: "",
  password: "",
  company_name: "",
  industry: "",
};

export default function Register({ onAuthenticated, onNavigate }) {
  const [form, setForm] = useState(initialForm);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    if (error) {
      setError("");
    }
  }

  function validateForm() {
    if (!String(form.email).trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(form.email).trim())) {
      setError("Please enter a valid email address.");
      return false;
    }

    if (String(form.password).length < 8) {
      setError("Password must be at least 8 characters long.");
      return false;
    }

    if (!String(form.company_name).trim()) {
      setError("Company name is required.");
      return false;
    }

    if (!String(form.industry).trim()) {
      setError("Industry is required.");
      return false;
    }

    return true;
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");

    if (!validateForm()) {
      setLoading(false);
      return;
    }

    try {
      const payload = {
        email: String(form.email).trim(),
        password: String(form.password),
        company_name: String(form.company_name).trim(),
        industry: String(form.industry).trim(),
      };

      const result = await register(payload);
      onAuthenticated?.(result);
      onNavigate?.("enterprise");
    } catch (err) {
      setError(err.message || "Unable to create account.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthCard
      title="Create your enterprise"
      subtitle="Set up your company account and get started with enterprise profile management."
      footer={
        <>
          Already have an account?{" "}
          <button
            type="button"
            className="text-button"
            onClick={() => onNavigate?.("login")}
          >
            Log in
          </button>
        </>
      }
    >
      <form className="auth-form" onSubmit={handleSubmit} noValidate>
        <div className="field-group">
          <label htmlFor="register-email">Email</label>
          <input
            id="register-email"
            name="email"
            type="email"
            value={form.email}
            onChange={handleChange}
            placeholder="admin@company.com"
            required
          />
        </div>

        <div className="field-group">
          <label htmlFor="register-password">Password</label>
          <input
            id="register-password"
            name="password"
            type="password"
            value={form.password}
            onChange={handleChange}
            placeholder="Create a password"
            required
            minLength={8}
          />
        </div>

        <div className="field-group">
          <label htmlFor="register-company">Company name</label>
          <input
            id="register-company"
            name="company_name"
            value={form.company_name}
            onChange={handleChange}
            placeholder="GreenWorks Ltd"
            required
          />
        </div>

        <div className="field-group">
          <label htmlFor="register-industry">Industry</label>
          <input
            id="register-industry"
            name="industry"
            value={form.industry}
            onChange={handleChange}
            placeholder="Manufacturing"
            required
          />
        </div>

        {error ? <div className="form-error">{error}</div> : null}

        <button type="submit" className="primary-button" disabled={loading}>
          {loading ? "Creating account..." : "Create account"}
        </button>
      </form>
    </AuthCard>
  );
}
