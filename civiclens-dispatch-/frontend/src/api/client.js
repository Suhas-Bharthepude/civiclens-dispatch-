// frontend/src/api/client.js
// Central API module — ALL fetch() calls live here.
// Components import named functions from this file.
// They never call fetch() directly.
//
// Day 41 addition: getStats()

// Base URL of the backend API
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// ── SHARED REQUEST HELPER ────────────────────────────────
// All API functions call this helper.
// It handles URL construction, error checking, and JSON parsing.
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`
  console.log(`[API] ${options.method || 'GET'} ${url}`)

  const response = await fetch(url, options)

  // response.ok is true for 2xx status codes
  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}`
    try {
      const errorData = await response.json()
      errorMessage = errorData.detail || errorMessage
    } catch { /* body wasn't JSON — use status code */ }
    throw new Error(errorMessage)
  }

  // 204 No Content has no body
  if (response.status === 204) return null

  return response.json()
}

// ── CHECK HEALTH ─────────────────────────────────────────
// Called by HealthCheck.jsx to verify the backend is reachable
export async function checkHealth() {
  return apiRequest('/health')
}

// ── GET INCIDENTS ─────────────────────────────────────────
// Fetches all incidents, optionally filtered by query params
export async function getIncidents(filters = {}) {
  const params = Object.keys(filters)
    .filter(key => filters[key] !== '' && filters[key] != null)
    .map(key => `${key}=${encodeURIComponent(filters[key])}`)
    .join('&')
  const endpoint = params ? `/incidents?${params}` : '/incidents'
  return apiRequest(endpoint)
}

// ── GET STATS ─────────────────────────────────────────────  ← NEW DAY 41
// Fetches aggregate statistics about all incidents.
// Returns an object with total, by_severity, by_status, by_type, etc.
// Used by the StatsBar component to show dashboard KPIs.
//
// Example response:
// {
//   total: 10,
//   by_severity: { critical: 1, high: 3, medium: 5, low: 1 },
//   by_status:   { pending: 6, active: 2, resolved: 2 },
//   by_type:     { fire: 3, medical: 2, crime: 2, ... },
//   high_risk_count: 4,
//   with_audio_count: 3
// }
export async function getStats() {
  // Calls GET /incidents/stats on the backend
  return apiRequest('/incidents/stats')
}

// ── GET SINGLE INCIDENT ───────────────────────────────────
export async function getIncident(id) {
  return apiRequest(`/incidents/${id}`)
}

// ── CREATE INCIDENT ───────────────────────────────────────
export async function createIncident(incidentData) {
  return apiRequest('/incidents', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(incidentData),
  })
}

// ── UPDATE INCIDENT STATUS ────────────────────────────────
// Sends PATCH /incidents/{id} with { status: newStatus }
export async function updateIncidentStatus(id, newStatus) {
  return apiRequest(`/incidents/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status: newStatus }),
  })
}

// ── UPLOAD AUDIO ──────────────────────────────────────────
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