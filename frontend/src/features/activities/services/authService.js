const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function parseResponse(response) {
  return response.text().then((text) => {
    if (!text) return {};

    let data;
    try {
      data = JSON.parse(text);
    } catch (error) {
      if (!response.ok) {
        throw new Error("Request failed");
      }
      return {};
    }

    if (!response.ok) {
      if (Array.isArray(data.detail)) {
        const firstError = data.detail[0];
        const message = firstError?.msg || "Validation failed";
        throw new Error(message);
      }

      if (typeof data.detail === "string") {
        throw new Error(data.detail);
      }

      if (typeof data.message === "string") {
        throw new Error(data.message);
      }

      throw new Error("Request failed");
    }

    return data;
  });
}

function getStoredToken() {
  return localStorage.getItem("enterprise_token");
}

export function getAuthHeaders(extraHeaders = {}) {
  const token = getStoredToken();
  return {
    ...extraHeaders,
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export function saveAuthSession(data) {
  if (data.access_token) {
    localStorage.setItem("enterprise_token", data.access_token);
  }

  if (data.enterprise_id) {
    localStorage.setItem("enterprise_id", data.enterprise_id);
  }

  if (data.company_name) {
    localStorage.setItem("enterprise_name", data.company_name);
  }

  if (data.email) {
    localStorage.setItem("enterprise_email", data.email);
  }
}

export function clearAuthSession() {
  localStorage.removeItem("enterprise_token");
  localStorage.removeItem("enterprise_id");
  localStorage.removeItem("enterprise_name");
  localStorage.removeItem("enterprise_email");
}

export async function login(payload) {
  const response = await fetch(`${API_BASE_URL}/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const data = await parseResponse(response);
  saveAuthSession(data);
  return data;
}

export async function register(payload) {
  const response = await fetch(`${API_BASE_URL}/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const data = await parseResponse(response);
  saveAuthSession(data);
  return data;
}

export async function getProfile() {
  const response = await fetch(`${API_BASE_URL}/profile`, {
    method: "GET",
    headers: getAuthHeaders(),
  });

  return parseResponse(response);
}

export async function updateProfile(payload) {
  const response = await fetch(`${API_BASE_URL}/profile`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
    },
    body: JSON.stringify(payload),
  });

  return parseResponse(response);
}

export async function listDepartments() {
  const response = await fetch(`${API_BASE_URL}/departments`, {
    method: "GET",
    headers: getAuthHeaders(),
  });

  return parseResponse(response);
}

export async function createDepartment(payload) {
  const response = await fetch(`${API_BASE_URL}/departments`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
    },
    body: JSON.stringify(payload),
  });

  return parseResponse(response);
}
