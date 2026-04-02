// frontend/src/components/dashboard/IncidentDetail.jsx
// The right-side detail panel in the dispatcher dashboard.
// Shows all fields of the selected incident and lets the
// dispatcher change its status (pending → active → resolved).
//
// Day 37 additions:
//   - Status action buttons in the footer (Mark Active / Resolve / Reopen)
//   - isUpdating state to disable buttons while request is in flight
//   - handleStatusChange: calls PATCH API, then notifies parent via onStatusChange
//   - Optimistic UI: parent updates selectedIncident immediately
//
// Day 51 additions:
//   - Image caption display (from DETR object detection, Day 48)
//   - Reprocess with AI button (calls POST /incidents/{id}/reprocess, Day 50)
//
// Props received from App.jsx:
//   incident       - the currently selected incident object (or null)
//   onClose        - called when dispatcher clicks Close or presses ESC
//   onStatusChange - called after a status update: onStatusChange(id, newStatus)

import React, { useState } from 'react'

// CSS for this panel
import './IncidentDetail.css'

// API function that sends PATCH /incidents/{id} with { status: newStatus }
import { updateIncidentStatus } from '../../api/client'

// ============================================================
// AI BADGE — small inline sub-component
// ============================================================
// Renders a "🤖 AI" pill label next to field names that were
// filled in by AI, so dispatchers know which data to verify.
const AIBadge = () => (
  <span className="ai-badge">🤖 AI</span>
)

// ============================================================
// TRANSCRIPT PANEL — handles 3 states for audio transcripts
// ============================================================
// State 1: No audio uploaded → render nothing
// State 2: Audio exists, transcript not ready → show "Processing..."
// State 3: Both audio and transcript exist → show transcript card
const TranscriptPanel = ({ incident }) => {
  // If no audio was uploaded, there's nothing to show
  if (!incident.audio_path) return null

  // Audio exists but transcript hasn't been generated yet
  if (!incident.transcript) {
    return (
      <div className="transcript-panel transcript-panel--processing">
        <div className="transcript-panel__header">
          <span className="transcript-panel__icon">🎤</span>
          <h4 className="transcript-panel__title">Audio Transcript</h4>
          <AIBadge />
        </div>
        <div className="transcript-panel__body">
          <p className="transcript-processing-text">🔄 Transcription in progress...</p>
          <p className="transcript-processing-hint">
            Refresh in a few seconds to see the result.
          </p>
        </div>
      </div>
    )
  }

  // Both audio and transcript exist — show the transcript text
  return (
    <div className="transcript-panel">
      <div className="transcript-panel__header">
        <span className="transcript-panel__icon">🎤</span>
        <h4 className="transcript-panel__title">Audio Transcript</h4>
        <AIBadge />
      </div>
      <div className="transcript-panel__body">
        <blockquote className="transcript-text">{incident.transcript}</blockquote>
      </div>
      <div className="transcript-panel__footer">
        <p className="transcript-footer-note">
          ℹ️ Auto-transcribed by AI — verify before acting.
        </p>
      </div>
    </div>
  )
}

// ============================================================
// STATUS ACTION BUTTONS — inline sub-component
// ============================================================
// Renders the correct set of action buttons based on current status.
// Rules:
//   pending  → show "Mark Active" + "Mark Resolved"
//   active   → show "Mark Resolved"
//   resolved → show "Reopen" (sets back to pending)
//
// Props:
//   currentStatus - the incident's current status string
//   isUpdating    - true while a PATCH request is in flight (disables buttons)
//   onUpdate      - function(newStatus) called when a button is clicked
const StatusActions = ({ currentStatus, isUpdating, onUpdate }) => {
  return (
    // Wrapper for the action buttons — sits before the Close button in the footer
    <div className="status-actions">

      {/* "Mark Active" button — only shown when status is pending */}
      {currentStatus === 'pending' && (
        <button
          className="btn btn--status btn--active"
          // Disabled while another request is already in flight
          disabled={isUpdating}
          onClick={() => onUpdate('active')}
          // Tooltip on hover
          title="Mark this incident as actively being handled"
        >
          {/* Show spinner emoji while updating, otherwise the label */}
          {isUpdating ? '⏳' : '⚡ Mark Active'}
        </button>
      )}

      {/* "Mark Resolved" button — shown when status is pending or active */}
      {(currentStatus === 'pending' || currentStatus === 'active') && (
        <button
          className="btn btn--status btn--resolve"
          disabled={isUpdating}
          onClick={() => onUpdate('resolved')}
          title="Mark this incident as resolved and closed"
        >
          {isUpdating ? '⏳' : '✅ Resolve'}
        </button>
      )}

      {/* "Reopen" button — only shown when status is resolved */}
      {currentStatus === 'resolved' && (
        <button
          className="btn btn--status btn--reopen"
          disabled={isUpdating}
          onClick={() => onUpdate('pending')}
          title="Reopen this incident and set it back to pending"
        >
          {isUpdating ? '⏳' : '↩ Reopen'}
        </button>
      )}

    </div>
  )
}

// ============================================================
// MAIN COMPONENT: IncidentDetail
// ============================================================
const IncidentDetail = ({ incident, onClose, onStatusChange }) => {

  // isUpdating: true while the PATCH request is in flight
  // Used to disable all status buttons to prevent double-clicking
  const [isUpdating, setIsUpdating] = useState(false)

  // updateError: stores an error message if the PATCH request fails
  // Displayed as a small error banner in the footer area
  const [updateError, setUpdateError] = useState(null)

  // ── STATUS CHANGE HANDLER ──────────────────────────────
  // Called when dispatcher clicks one of the status action buttons.
  // newStatus: 'pending' | 'active' | 'resolved'
  const handleStatusChange = async (newStatus) => {
    // Clear any previous error message
    setUpdateError(null)

    // Disable buttons immediately — prevents double-click
    setIsUpdating(true)

    // Remember the old status in case we need to revert
    const previousStatus = incident.status

    // OPTIMISTIC UPDATE:
    // Tell the parent (App.jsx) about the new status right away,
    // before waiting for the server to confirm.
    // This makes the UI feel instant.
    // If the server rejects it, we'll revert below.
    onStatusChange(incident.id, newStatus)

    try {
      // Send PATCH /incidents/{id} with { status: newStatus }
      // This is the actual server call — takes ~100-500ms
      await updateIncidentStatus(incident.id, newStatus)

      // Success! The optimistic update was correct.
      // No additional UI changes needed — the parent already updated.

    } catch (err) {
      // The server rejected the update (e.g., network error, server down).
      // We need to REVERT the optimistic update.

      // Tell the parent to put the old status back
      onStatusChange(incident.id, previousStatus)

      // Show an error message to the dispatcher
      setUpdateError(`Failed to update status: ${err.message}`)

    } finally {
      // Always re-enable buttons, whether request succeeded or failed
      // 'finally' runs even if the try or catch threw an error
      setIsUpdating(false)
    }
  }

  // ── REPROCESS HANDLER (Day 51) ─────────────────────────
  // Called when dispatcher clicks the "Reprocess with AI" button.
  // Sends POST /incidents/{id}/reprocess to re-run the full AI pipeline.
  const handleReprocess = async () => {
    try {
      // Call the reprocess endpoint added on Day 50
      await fetch(`http://localhost:8000/incidents/${incident.id}/reprocess`, {
        method: 'POST'
      })
      // Show confirmation to the dispatcher
      alert(`Reprocessing queued for incident #${incident.id}. Refresh in a moment to see updated AI results.`)
    } catch (err) {
      alert(`Failed to reprocess: ${err.message}`)
    }
  }

  // ── HELPERS ───────────────────────────────────────────
  // Format ISO date string to readable format
  const formatDate = (str) => {
    if (!str) return 'Unknown'
    return new Date(str).toLocaleString()
  }

  // Returns a CSS class for the severity badge color
  const getSeverityClass = (severity) => {
    const map = {
      critical: 'severity-badge--critical',
      high:     'severity-badge--high',
      medium:   'severity-badge--medium',
      low:      'severity-badge--low',
    }
    return map[severity?.toLowerCase()] || 'severity-badge--medium'
  }

  // Converts 0.87 → "87%" and null → "—"
  const formatRiskScore = (score) => {
    if (score === null || score === undefined) return '—'
    return `${Math.round(score * 100)}%`
  }

  // ── EMPTY STATE ────────────────────────────────────────
  // No incident selected yet — show a placeholder
  if (!incident) {
    return (
      <div className="detail-panel">
        <div className="detail-empty">
          <p className="empty-icon">👈</p>
          <p className="empty-message">Select an incident from the table to view details</p>
        </div>
      </div>
    )
  }

  // ── MAIN RENDER ────────────────────────────────────────
  return (
    <div className="detail-panel">

      {/* ── HEADER ─────────────────────────────────────── */}
      <div className="detail-header">
        <h2 className="detail-title">Incident #{incident.id}</h2>
        <button
          className="detail-close-btn"
          onClick={onClose}
          aria-label="Close detail panel"
        >
          ✕
        </button>
      </div>

      {/* ── SCROLLABLE CONTENT ─────────────────────────── */}
      <div className="detail-content">

        {/* Severity + Status badges at the top */}
        <div className="detail-severity-row">
          <span className={`severity-badge ${getSeverityClass(incident.severity)}`}>
            {incident.severity ? incident.severity.toUpperCase() : 'MEDIUM'}
          </span>
          {/* Status badge — class changes based on current status */}
          <span className={`status-badge status-badge--${incident.status || 'pending'}`}>
            {incident.status ? incident.status.toUpperCase() : 'PENDING'}
          </span>
        </div>

        {/* ── CORE INFORMATION ───────────────────────── */}

        <div className="detail-field">
          {/* No AI badge — humans write descriptions */}
          <label className="detail-label">Description</label>
          <p className="detail-value description-full">{incident.description}</p>
        </div>

        <div className="detail-field">
          <label className="detail-label">Location</label>
          <p className="detail-value">📍 {incident.location || 'Not specified'}</p>
        </div>

        <div className="detail-field">
          <label className="detail-label">Reported By</label>
          <p className="detail-value">
            {incident.source
              ? incident.source.charAt(0).toUpperCase() + incident.source.slice(1)
              : 'Unknown'}
          </p>
        </div>

        <div className="detail-field">
          <label className="detail-label">Reported At</label>
          <p className="detail-value">🕐 {formatDate(incident.created_at)}</p>
        </div>

        {/* ── AI ANALYSIS ────────────────────────────── */}
        <div className="section-divider">
          <h3 className="section-divider__title">🤖 AI Analysis</h3>
        </div>

        <div className="detail-field">
          <label className="detail-label">Incident Type <AIBadge /></label>
          <p className="detail-value incident-type-value">
            {incident.incident_type ? incident.incident_type.toUpperCase() : 'OTHER'}
          </p>
        </div>

        <div className="detail-field">
          <label className="detail-label">Severity <AIBadge /></label>
          <p className="detail-value">
            {incident.severity ? incident.severity.toUpperCase() : 'MEDIUM'}
          </p>
        </div>

        <div className="detail-field">
          <label className="detail-label">Risk Score <AIBadge /></label>
          <p className={`detail-value risk-score-value ${
            incident.risk_score > 0.7  ? 'risk-score-value--high'   :
            incident.risk_score > 0.4  ? 'risk-score-value--medium' :
                                         'risk-score-value--low'
          }`}>
            {formatRiskScore(incident.risk_score)}
          </p>
        </div>

        {/* AI Summary — only if one exists */}
        {incident.summary && (
          <div className="detail-field">
            <label className="detail-label">AI Summary <AIBadge /></label>
            <p className="detail-value summary-text">{incident.summary}</p>
          </div>
        )}

        {/* ── IMAGE CAPTION (Day 51) ─────────────────── */}
        {/* Only show if image_caption exists and isn't an error message */}
        {incident.image_caption && !incident.image_caption.startsWith('[') && (
          <div className="detail-field">
            <label className="detail-label">Image Analysis <AIBadge /></label>
            <p className="detail-value summary-text">🖼️ {incident.image_caption}</p>
          </div>
        )}

        {/* ── AUDIO SECTION ──────────────────────────── */}
        {/* Section heading only appears if audio was uploaded */}
        {incident.audio_path && (
          <div className="section-divider">
            <h3 className="section-divider__title">🎤 Audio</h3>
          </div>
        )}

        {/* TranscriptPanel handles its own 3-state logic internally */}
        <TranscriptPanel incident={incident} />

        {/* ── ATTACHED FILES ──────────────────────────── */}
        {(incident.audio_path || incident.image_path) && (
          <>
            <div className="section-divider">
              <h3 className="section-divider__title">📎 Attached Files</h3>
            </div>

            {incident.audio_path && (
              <div className="detail-field">
                <label className="detail-label">Audio File</label>
                {/* Show just the filename, not the full server path */}
                <p className="detail-value file-path">
                  🎧 {incident.audio_path.split('/').pop()}
                </p>
              </div>
            )}

            {incident.image_path && (
              <div className="detail-field">
                <label className="detail-label">Photo</label>
                <p className="detail-value file-path">
                  📷 {incident.image_path.split('/').pop()}
                </p>
              </div>
            )}
          </>
        )}

      </div>
      {/* END scrollable content */}

      {/* ── FOOTER ─────────────────────────────────────── */}
      {/* Contains status action buttons + reprocess + error message + close button */}
      <div className="detail-footer">

        {/* Error message banner — only visible when an update fails */}
        {updateError && (
          <div className="update-error">
            {/* ⚠️ icon makes the error easy to spot */}
            ⚠️ {updateError}
            {/* X button clears the error message */}
            <button
              className="update-error__dismiss"
              onClick={() => setUpdateError(null)}
            >
              ✕
            </button>
          </div>
        )}

        {/* Row with status buttons on left, Close button on right */}
        <div className="detail-footer__actions">

          {/* StatusActions renders the correct button(s) for the current status */}
          <StatusActions
            currentStatus={incident.status || 'pending'}
            isUpdating={isUpdating}
            onUpdate={handleStatusChange}
          />

          {/* Reprocess button (Day 51) — re-runs the full AI pipeline */}
          <button
            className="btn btn--status btn--reprocess"
            onClick={handleReprocess}
            title="Re-run all AI models on this incident"
          >
            🔄 Reprocess
          </button>

          {/* Close button — always present on the right */}
          <button className="btn btn--secondary" onClick={onClose}>
            Close
          </button>

        </div>
      </div>

    </div>
  )
}

export default IncidentDetail