// frontend/src/api/client.js
// Central API module — ALL fetch() calls live here.
// Components import named functions from this file.
// They never call fetch() directly.
//
// This keeps network logic in one place so:
//   - If the backend URL changes, you change it here once
//   - If you need to add auth headers later, you add them here once
//   - Each function has a clear name describing what it does
//
// Day 37 addition: updateIncidentStatus()

// The base URL of the backend API.
// Vite exposes environment variables prefixed with VITE_ via import.meta.env
// If not set in .env, defaults to localhost:8000
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// ============================================================
// HELPER: apiRequest
// ============================================================
// Shared wrapper around fetch() used by every function below.
// Handles:
//   - Building the full URL
//   - Logging the request for debugging
//   - Checking for non-2xx HTTP status codes
//   - Parsing the JSON response body
//   - Throwing a descriptive error on failure
//
// args:
//   endpoint - the path after the base URL, e.g. '/incidents/12'
//   options  - optional fetch() options (method, headers, body, etc.)
async function apiRequest(endpoint, options = {}) {
  // Build the complete URL by joining base + endpoint
  const url = `${API_BASE_URL}${endpoint}`

  // Log every request so we can debug network issues in the browser console
  console.log(`[API] ${options.method || 'GET'} ${url}`)

  // Make the actual HTTP request
  // fetch() returns a Promise that resolves to a Response object
  const response = await fetch(url, options)

  // response.ok is true for 2xx status codes (200, 201, 204, etc.)
  // If the server returned 4xx or 5xx, we throw an error
  if (!response.ok) {
    // Try to parse the error body — FastAPI returns { detail: "..." }
    let errorMessage = `HTTP ${response.status}`
    try {
      const errorData = await response.json()
      // FastAPI puts error details in a 'detail' field
      errorMessage = errorData.detail || errorMessage
    } catch {
      // If the body isn't JSON, just use the status code message
    }
    // Throw so the calling function's catch block handles it
    throw new Error(errorMessage)
  }

  // 204 No Content means success but no body — return null
  if (response.status === 204) return null

  // Parse and return the JSON response body
  return response.json()
}

// ============================================================
// CHECK HEALTH
// ============================================================
// Calls GET /health to verify the backend is running.
// Used by HealthCheck.jsx to show the green/red indicator.
export async function checkHealth() {
  return apiRequest('/health')
}

// ============================================================
// GET INCIDENTS
// ============================================================
// Fetches the list of all incidents.
// Optional filters object: { incident_type: 'fire', status: 'pending' }
// These become URL query parameters: /incidents?incident_type=fire
export async function getIncidents(filters = {}) {
  // Build query string from filters object
  // Object.keys returns ['incident_type', 'status'] etc.
  const params = Object.keys(filters)
    // Remove keys with empty/null values — don't send empty params
    .filter(key => filters[key] !== '' && filters[key] !== null && filters[key] !== undefined)
    // Convert each key/value to "key=value" string
    .map(key => `${key}=${encodeURIComponent(filters[key])}`)
    // Join with & to form the full query string
    .join('&')

  // Build the endpoint with or without query string
  const endpoint = params ? `/incidents?${params}` : '/incidents'
  return apiRequest(endpoint)
}

// ============================================================
// GET SINGLE INCIDENT
// ============================================================
// Fetches one incident by its ID.
// Used when we need fresh data after an update.
export async function getIncident(id) {
  return apiRequest(`/incidents/${id}`)
}

// ============================================================
// CREATE INCIDENT
// ============================================================
// Sends a POST request to create a new incident.
// incidentData: object with description, location, source, etc.
export async function createIncident(incidentData) {
  return apiRequest('/incidents', {
    method: 'POST',
    headers: {
      // Tell the server we're sending JSON
      'Content-Type': 'application/json',
    },
    // JSON.stringify converts the JS object to a JSON string for the request body
    body: JSON.stringify(incidentData),
  })
}

// ============================================================
// UPDATE INCIDENT STATUS  ← NEW IN DAY 37
// ============================================================
// Sends a PATCH request to update just the status field of an incident.
// Uses PATCH (not PUT) because we're changing one field, not replacing everything.
//
// Parameters:
//   id        - the incident's database ID (e.g., 12)
//   newStatus - one of: 'pending' | 'active' | 'resolved'
//
// Example usage:
//   await updateIncidentStatus(12, 'active')
//   → PATCH /incidents/12  with body { "status": "active" }
export async function updateIncidentStatus(id, newStatus) {
  return apiRequest(`/incidents/${id}`, {
    // PATCH = partial update (only the fields in the body are changed)
    method: 'PATCH',
    headers: {
      // Required so FastAPI parses the body as JSON, not raw text
      'Content-Type': 'application/json',
    },
    // Only send the status field — all other incident fields stay unchanged
    body: JSON.stringify({ status: newStatus }),
  })
}

// ============================================================
// UPLOAD AUDIO
// ============================================================
// Sends an audio file to POST /incidents/{id}/audio
// Uses FormData (multipart/form-data) — not JSON — because it's a file
export async function uploadAudio(incidentId, audioFile) {
  // FormData is a browser API for sending files
  const formData = new FormData()
  // 'file' must match the parameter name expected by the FastAPI endpoint
  formData.append('file', audioFile)

  // Note: Do NOT set Content-Type header manually for FormData
  // The browser sets it automatically with the correct multipart boundary
  const response = await fetch(`${API_BASE_URL}/incidents/${incidentId}/audio`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    throw new Error(`Audio upload failed: HTTP ${response.status}`)
  }

  return response.json()
}

// ============================================================
// UPLOAD IMAGE
// ============================================================
// Sends an image file to POST /incidents/{id}/image
// Same pattern as uploadAudio above
export async function uploadImage(incidentId, imageFile) {
  const formData = new FormData()
  formData.append('file', imageFile)

  const response = await fetch(`${API_BASE_URL}/incidents/${incidentId}/image`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    throw new Error(`Image upload failed: HTTP ${response.status}`)
  }

  return response.json()
}