import { getAuthHeaders } from "./authService";

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000";

const AI_URL = `${API_BASE_URL}/ai`;

async function handleResponse(response) {
  const data = await response.json();

  if (!response.ok) {
    const message =
      typeof data.detail === "string"
        ? data.detail
        : Array.isArray(data.detail)
          ? data.detail.map((error) => error.msg).join(", ")
          : "AI recommendations request failed";

    throw new Error(message);
  }

  return data;
}

/**
 * Request tailored carbon reduction recommendations for the authenticated enterprise.
 */
export async function getAIRecommendations() {
  const response = await fetch(`${AI_URL}/recommendations`, {
    method: "POST",
    headers: getAuthHeaders({
      "Content-Type": "application/json",
    }),
  });

  return handleResponse(response);
}
