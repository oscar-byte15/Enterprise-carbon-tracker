import { useState } from "react";
import AuthCard from "../components/AuthCard";
import { login } from "../services/authService";

export default function Login({ onAuthenticated, onNavigate }) {
  const [form, setForm] = useState({ email: "", password: "" });
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
    if (
      !String(form.email).trim() ||
      !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(form.email).trim())
    ) {
      setError("Please enter a valid email address.");
      return false;
    }

    if (String(form.password).length < 8) {
      setError("Password must be at least 8 characters long.");
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
      };

      const result = await login(payload);
      onAuthenticated?.(result);
      onNavigate?.("enterprise");
    } catch (err) {
      setError(err.message || "Unable to log in.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthCard
      title="Welcome back"
      subtitle="Sign in to manage your enterprise profile and departments."
      footer={
        <>
          Need an account?{" "}
          <button
            type="button"
            className="text-button"
            onClick={() => onNavigate?.("register")}
          >
            Create one
          </button>
        </>
      }
    >
      <form className="auth-form" onSubmit={handleSubmit} noValidate>
        <div className="field-group">
          <label htmlFor="login-email">Email</label>
          <input
            id="login-email"
            name="email"
            type="email"
            value={form.email}
            onChange={handleChange}
            placeholder="admin@company.com"
            required
          />
        </div>

        <div className="field-group">
          <label htmlFor="login-password">Password</label>
          <input
            id="login-password"
            name="password"
            type="password"
            value={form.password}
            onChange={handleChange}
            placeholder="Enter your password"
            required
            minLength={8}
          />
        </div>

        {error ? <div className="form-error">{error}</div> : null}

        <button type="submit" className="primary-button" disabled={loading}>
          {loading ? "Signing in..." : "Sign in"}
        </button>
      </form>
    </AuthCard>
  );
}
