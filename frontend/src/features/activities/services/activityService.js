
const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000";

const ACTIVITIES_URL = `${API_BASE_URL}/activities`;

// Handle HTTP response
async function handleResponse(response) {
  if (response.status === 204) {
    return null;
  }

  const data = await response.json();

  if (!response.ok) {
    const message =
      typeof data.detail === "string"
        ? data.detail
        : Array.isArray(data.detail)
          ? data.detail.map((error) => error.msg).join(", ")
          : "Activity request failed";

    throw new Error(message);
  }

  return data;
}

// CREATE
export async function createActivity(activity) {
  const response = await fetch(`${ACTIVITIES_URL}/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(activity),
  });

  const data = await handleResponse(response);
  return data.activity;
}

// READ ALL
export async function getActivities() {
  const response = await fetch(`${ACTIVITIES_URL}/`, {
    method: "GET",
  });

  return handleResponse(response);
}

// READ ONE
export async function getActivityById(id) {
  const response = await fetch(
    `${ACTIVITIES_URL}/${encodeURIComponent(id)}`,
    { method: "GET" }
  );

  return handleResponse(response);
}

// UPDATE
export async function updateActivity(id, activity) {
  const response = await fetch(
    `${ACTIVITIES_URL}/${encodeURIComponent(id)}`,
    {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(activity),
    }
  );

  const data = await handleResponse(response);
  return data.activity;
}

// DELETE
export async function deleteActivity(id) {
  const response = await fetch(
    `${ACTIVITIES_URL}/${encodeURIComponent(id)}`,
    { method: "DELETE" }
  );

  return handleResponse(response);
}
