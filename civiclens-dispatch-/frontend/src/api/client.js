// frontend/src/api/client.js
// Central API module — ALL fetch() calls live here.
// Components import named functions from this file.
// They never call fetch() directly.
//
// Day 41 addition: getStats()
// Day 52 additions: reprocessIncident(), getAIStatus()
// Day 70 additions: getAnalyticsSummary(), getTimeseries(), getRiskDistribution()
// Day 72 additions: auth header injection, deleteIncident(), loginUser()

// Base URL of the backend API
// Uses environment variable if set, otherwise defaults to localhost:8000
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// ── SHARED REQUEST HELPER ────────────────────────────────
// All API functions call this helper.
// It handles URL construction, auth headers, error checking, and JSON parsing.
async function apiRequest(endpoint, options = {}) {
  // Build the full URL from base + endpoint
  const url = `${API_BASE_URL}${endpoint}`
  // Log every API call for debugging in the browser console
  console.log(`[API] ${options.method || 'GET'} ${url}`)

  // Read the auth token from sessionStorage (set by AuthContext on login)
  // sessionStorage is cleared when the browser tab is closed — safer than localStorage
  const token = sessionStorage.getItem('auth_token')

  // Build headers: start with any caller-provided headers, then add auth
  const headers = {
    ...options.headers,
  }
  // Attach the bearer token if one exists — backend will 401 without it
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  // Make the actual HTTP request using the browser's fetch() API
  const response = await fetch(url, { ...options, headers })

  // response.ok is true for 2xx status codes (200, 201, 204, etc.)
  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}`
    try {
      // Try to parse error details from the JSON response body
      const errorData = await response.json()
      // FastAPI returns errors in a 'detail' field
      errorMessage = errorData.detail || errorMessage
    } catch { /* body wasn't JSON — use status code */ }
    throw new Error(errorMessage)
  }

  // 204 No Content has no body (e.g., DELETE responses)
  if (response.status === 204) return null

  // Parse and return the JSON response body
  return response.json()
}

// ── CHECK HEALTH ─────────────────────────────────────────
// Called by HealthCheck.jsx to verify the backend is reachable
// Endpoint: GET /health
export async function checkHealth() {
  return apiRequest('/health')
}

// ── GET INCIDENTS ─────────────────────────────────────────
// Fetches all incidents, optionally filtered by query params
// Endpoint: GET /incidents?incident_type=fire&severity=high&search=keyword
export async function getIncidents(filters = {}) {
  // Build query string from the filters object
  // Skips empty or null values so we don't send ?severity=&type=
  const params = Object.keys(filters)
    .filter(key => filters[key] !== '' && filters[key] != null)
    .map(key => `${key}=${encodeURIComponent(filters[key])}`)
    .join('&')
  // Append query string only if there are actual filters
  const endpoint = params ? `/incidents?${params}` : '/incidents'
  return apiRequest(endpoint)
}

// ── GET STATS ─────────────────────────────────────────────
// Fetches aggregate statistics about all incidents.
// Used by the StatsBar component to show dashboard KPIs.
// Endpoint: GET /incidents/stats
export async function getStats() {
  return apiRequest('/incidents/stats')
}

// ── GET SINGLE INCIDENT ───────────────────────────────────
// Fetches one incident by its ID
// Endpoint: GET /incidents/{id}
export async function getIncident(id) {
  return apiRequest(`/incidents/${id}`)
}

// ── CREATE INCIDENT ───────────────────────────────────────
// Creates a new incident from the submission form data
// Endpoint: POST /incidents
export async function createIncident(incidentData) {
  return apiRequest('/incidents', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(incidentData),
  })
}

// ── UPDATE INCIDENT STATUS ────────────────────────────────
// Changes the status of an incident (pending → active → resolved)
// Endpoint: PATCH /incidents/{id}
export async function updateIncidentStatus(id, newStatus) {
  return apiRequest(`/incidents/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status: newStatus }),
  })
}

// ── DELETE INCIDENT (Day 72) ──────────────────────────────
// Permanently deletes an incident — admin only (backend enforces role)
// Endpoint: DELETE /incidents/{id}
// Returns null (204 No Content)
export async function deleteIncident(id) {
  return apiRequest(`/incidents/${id}`, { method: 'DELETE' })
}

// ── UPLOAD AUDIO ──────────────────────────────────────────
// Uploads an audio file for an existing incident
// Endpoint: POST /incidents/{id}/audio
// Uses FormData instead of JSON because we're sending a file
export async function uploadAudio(incidentId, audioFile) {
  const formData = new FormData()
  formData.append('file', audioFile)
  // Auth header must be added manually here since we bypass apiRequest
  const token = sessionStorage.getItem('auth_token')
  const headers = token ? { Authorization: `Bearer ${token}` } : {}
  const response = await fetch(
    `${API_BASE_URL}/incidents/${incidentId}/audio`,
    { method: 'POST', body: formData, headers }
  )
  if (!response.ok) throw new Error(`Audio upload failed: HTTP ${response.status}`)
  return response.json()
}

// ── UPLOAD IMAGE ──────────────────────────────────────────
// Uploads an image file for an existing incident
// Endpoint: POST /incidents/{id}/image
// Uses FormData instead of JSON because we're sending a file
export async function uploadImage(incidentId, imageFile) {
  const formData = new FormData()
  formData.append('file', imageFile)
  const token = sessionStorage.getItem('auth_token')
  const headers = token ? { Authorization: `Bearer ${token}` } : {}
  const response = await fetch(
    `${API_BASE_URL}/incidents/${incidentId}/image`,
    { method: 'POST', body: formData, headers }
  )
  if (!response.ok) throw new Error(`Image upload failed: HTTP ${response.status}`)
  return response.json()
}

// ── REPROCESS INCIDENT (Day 52) ──────────────────────────
// Re-runs the full AI pipeline on an existing incident
// Endpoint: POST /incidents/{id}/reprocess
export async function reprocessIncident(id) {
  return apiRequest(`/incidents/${id}/reprocess`, {
    method: 'POST',
  })
}

// ── GET AI STATUS (Day 52) ───────────────────────────────
// Checks the health of all AI models in the pipeline
// Endpoint: GET /ai/status
export async function getAIStatus() {
  return apiRequest('/ai/status')
}

// ── ANALYTICS: SUMMARY (Day 70) ─────────────────────────
// Returns KPI cards + chart-friendly arrays for type and severity
// Endpoint: GET /incidents/analytics/summary
export async function getAnalyticsSummary() {
  return apiRequest('/incidents/analytics/summary')
}

// ── ANALYTICS: TIMESERIES (Day 70) ──────────────────────
// Returns daily incident counts for the last N days, zero-filled
// Endpoint: GET /incidents/analytics/timeseries?days=30
export async function getTimeseries(days = 30) {
  return apiRequest(`/incidents/analytics/timeseries?days=${days}`)
}

// ── ANALYTICS: RISK DISTRIBUTION (Day 70) ───────────────
// Returns histogram data with 5 risk-score buckets
// Endpoint: GET /incidents/analytics/risk-distribution
export async function getRiskDistribution() {
  return apiRequest('/incidents/analytics/risk-distribution')
}

// ── AUTH: LOGIN (Day 72) ─────────────────────────────────
// POST to /auth/login with username + password, returns token + user
// Used by AuthContext — components call ctx.login() not this directly
export async function loginUser(username, password) {
  // Bypass apiRequest here since we have no token yet (this IS the login call)
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.detail || `Login failed: HTTP ${response.status}`)
  }
  return response.json()
}
