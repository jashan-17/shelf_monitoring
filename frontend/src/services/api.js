const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";
const API_PREFIX = API_BASE_URL ? `${API_BASE_URL}/api` : "/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_PREFIX}${path}`, options);

  if (!response.ok) {
    let message = "Something went wrong while talking to the API.";
    try {
      const errorPayload = await response.json();
      message = errorPayload.detail || message;
    } catch {
      message = response.statusText || message;
    }
    throw new Error(message);
  }

  return response.json();
}

export function getSummary() {
  return request("/summary");
}

export function getPredictions(limit = 10) {
  return request(`/predictions?limit=${limit}`);
}

export function getStockLevels() {
  return request("/analytics/stock-levels");
}

export function getTrends(days = 7) {
  return request(`/analytics/trends?days=${days}`);
}

export function getSystemStatus() {
  return request("/status");
}

export function uploadPrediction(file) {
  const formData = new FormData();
  formData.append("file", file);

  return request("/predict", {
    method: "POST",
    body: formData,
  });
}

export function savePredictionResult(payload) {
  return request("/predictions/save", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}
