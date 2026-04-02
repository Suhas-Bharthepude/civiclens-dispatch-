// frontend/src/api/client.js
// Central API module — ALL fetch() calls live here.
// Components import named functions from this file.
// They never call fetch() directly.
//
// Day 41 addition: getStats()
// Day 52 additions: reprocessIncident(), getAIStatus()

// Base URL of the backend API
// Uses environment variable if set, otherwise defaults to localhost:8000
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// ── SHARED REQUEST HELPER ────────────────────────────────
// All API functions call this helper.
// It handles URL construction, error checking, and JSON parsing.
async function apiRequest(endpoint, options = {}) {
  // Build the full URL from base + endpoint
  const url = `${API_BASE_URL}${endpoint}`
  // Log every API call for debugging in the browser console
  console.log(`[API] ${options.method || 'GET'} ${url}`)

  // Make the actual HTTP request using the browser's fetch() API
  const response = await fetch(url, options)

  // response.ok is true for 2xx status codes (200, 201, 204, etc.)
  // If not ok, throw an error with details from the response body
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

// ── UPLOAD AUDIO ──────────────────────────────────────────
// Uploads an audio file for an existing incident
// Endpoint: POST /incidents/{id}/audio
// Uses FormData instead of JSON because we're sending a file
export async function uploadAudio(incidentId, audioFile) {
  const formData = new FormData()
  formData.append('file', audioFile)
  const response = await fetch(
    `${API_BASE_URL}/incidents/${incidentId}/audio`,
    { method: 'POST', body: formData }
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
  const response = await fetch(
    `${API_BASE_URL}/incidents/${incidentId}/image`,
    { method: 'POST', body: formData }
  )
  if (!response.ok) throw new Error(`Image upload failed: HTTP ${response.status}`)
  return response.json()
}

// ── REPROCESS INCIDENT (Day 52) ──────────────────────────
// Re-runs the full AI pipeline on an existing incident
// Use when AI processing failed or you want fresh results
// Endpoint: POST /incidents/{id}/reprocess
// Returns immediately — pipeline runs in the background
export async function reprocessIncident(id) {
  return apiRequest(`/incidents/${id}/reprocess`, {
    method: 'POST',
  })
}

// ── GET AI STATUS (Day 52) ───────────────────────────────
// Checks the health of all AI models in the pipeline
// Returns pipeline_status ("healthy"/"degraded"/"down") and per-model details
// Endpoint: GET /ai/status
export async function getAIStatus() {
  return apiRequest('/ai/status')
}