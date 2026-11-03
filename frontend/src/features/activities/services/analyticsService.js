import { getAuthHeaders } from "./authService";

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000";

const ANALYTICS_URL = `${API_BASE_URL}/analytics`;

async function handleResponse(response) {
  const data = await response.json();

  if (!response.ok) {
    const message =
      typeof data.detail === "string"
        ? data.detail
        : Array.isArray(data.detail)
          ? data.detail.map((error) => error.msg).join(", ")
          : "Analytics request failed";

    throw new Error(message);
  }

  return data;
}

/**
 * Fetch analytics summary for the authenticated enterprise.
 * @param {string|null} period - Optional period filter in YYYY-MM format.
 */
export async function getAnalyticsSummary(period = null) {
  const query = period ? `?period=${encodeURIComponent(period)}` : "";
  const response = await fetch(`${ANALYTICS_URL}/summary${query}`, {
    method: "GET",
    headers: getAuthHeaders(),
  });

  return handleResponse(response);
}

/**
 * Fetch month-over-month carbon emission trends for the authenticated enterprise.
 * @param {number|string|null} year - Optional 4-digit calendar year filter (e.g. 2026).
 */
export async function getAnalyticsTrends(year = null) {
  const query = year ? `?year=${encodeURIComponent(year)}` : "";
  const response = await fetch(`${ANALYTICS_URL}/trends${query}`, {
    method: "GET",
    headers: getAuthHeaders(),
  });

  return handleResponse(response);
}

