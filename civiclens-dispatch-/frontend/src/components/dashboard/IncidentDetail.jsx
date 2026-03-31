// frontend/src/components/dashboard/IncidentDetail.jsx
// This is the RIGHT SIDE PANEL in the dispatcher dashboard.
// When a dispatcher clicks a row in the incidents table,
// this panel slides open and shows full details of that incident.
//
// Day 35 changes:
//   - Added AIBadge component to mark AI-generated fields
//   - Added a dedicated transcript panel with 3 states:
//       1. No audio uploaded → show nothing
//       2. Audio uploaded but not yet transcribed → show "Processing..."
//       3. Transcript ready → show transcript text in a scrollable card
//   - Added AI badges next to Incident Type, Severity, Risk Score labels

// Import React (required for JSX to work)
import React from 'react'

// Import the CSS file that styles this component
// IncidentDetail.css handles layout, colors, and spacing for this panel
import './IncidentDetail.css'

// ============================================================
// AI BADGE - Small inline component
// ============================================================
// This is a tiny "sub-component" defined inside this file
// because it's only used here and is very simple.
//
// It renders a small pill label that says "🤖 AI" so dispatchers
// can instantly see which fields were filled in by artificial
// intelligence versus typed by a human.
//
// Usage example:
//   <label>Risk Score <AIBadge /></label>
//   Renders as: "Risk Score  🤖 AI"
//
// No props needed — it always looks the same.
const AIBadge = () => (
  // The span gets the class "ai-badge" which is styled in the CSS
  // to look like a small rounded pill with a purple/indigo color
  <span className="ai-badge">🤖 AI</span>
)

// ============================================================
// TRANSCRIPT PANEL - Medium inline component
// ============================================================
// This component handles ALL transcript display logic.
// It receives the full incident object and decides what to show
// based on whether audio and transcript fields exist.
//
// Three possible states:
//   State 1: incident.audio_path is null/empty
//            → Return null (render nothing at all)
//   State 2: incident.audio_path exists BUT incident.transcript is null
//            → Show a "Processing..." spinner message
//   State 3: Both audio_path and transcript exist
//            → Show the transcript text in a styled scrollable card
//
// Why a separate component?
//   The logic has three branches with JSX for each. Keeping it
//   separate makes IncidentDetail's main return statement cleaner
//   and easier to read.
const TranscriptPanel = ({ incident }) => {

  // STATE 1: No audio was uploaded for this incident
  // If there's no audio_path, there's nothing to transcribe.
  // Return null tells React "render nothing here" — no empty box,
  // no placeholder, just nothing at all.
  if (!incident.audio_path) {
    return null
  }

  // STATE 2: Audio exists but transcript hasn't been generated yet.
  // The background job (incident_processor.py) runs after upload.
  // There's a short delay before the transcript appears.
  // We show a friendly "Processing..." message so the dispatcher
  // doesn't think something is broken.
  if (!incident.transcript) {
    return (
      // The outer div gets the "transcript-panel" class for the card styling
      <div className="transcript-panel transcript-panel--processing">

        {/* Header row with icon, title, and AI badge */}
        <div className="transcript-panel__header">
          {/* Microphone icon to signal this is audio-related */}
          <span className="transcript-panel__icon">🎤</span>
          {/* Section title */}
          <h4 className="transcript-panel__title">Audio Transcript</h4>
          {/* AIBadge tells dispatcher this is AI-generated content */}
          <AIBadge />
        </div>

        {/* Processing state body */}
        <div className="transcript-panel__body">
          {/* Spinning clock emoji gives a visual sense of "waiting" */}
          {/* The CSS animation makes this pulse gently */}
          <p className="transcript-processing-text">
            🔄 Transcription in progress...
          </p>
          {/* Helper text so dispatcher knows what to do */}
          <p className="transcript-processing-hint">
            The AI is converting the audio recording to text.
            Refresh in a few seconds to see the result.
          </p>
        </div>

      </div>
    )
  }

  // STATE 3: Transcript is ready — show it!
  // We reach this line only if BOTH audio_path AND transcript exist.
  return (
    // The outer div is the styled card container
    <div className="transcript-panel">

      {/* Header row with icon, title, and AI badge */}
      <div className="transcript-panel__header">
        {/* Microphone icon */}
        <span className="transcript-panel__icon">🎤</span>
        {/* Section title */}
        <h4 className="transcript-panel__title">Audio Transcript</h4>
        {/* Mark this as AI-generated */}
        <AIBadge />
      </div>

      {/* The actual transcript text in a scrollable box */}
      {/* overflow-y: auto in CSS means it scrolls if text is long */}
      <div className="transcript-panel__body">
        {/* blockquote is semantically correct for quoted/transcribed speech */}
        <blockquote className="transcript-text">
          {/* incident.transcript is the text string from the database */}
          {incident.transcript}
        </blockquote>
      </div>

      {/* Footer note clarifying this is AI-generated */}
      <div className="transcript-panel__footer">
        <p className="transcript-footer-note">
          ℹ️ Automatically transcribed from audio recording using AI speech recognition.
          Verify accuracy before taking action.
        </p>
      </div>

    </div>
  )
}

// ============================================================
// MAIN COMPONENT: IncidentDetail
// ============================================================
// Props this component receives:
//   incident  - The full incident object (or null if nothing selected)
//   onClose   - A function to call when dispatcher clicks "Close"
//
// If incident is null (no row selected yet), we show an empty state.
// If incident exists, we show all its fields in organized sections.
const IncidentDetail = ({ incident, onClose }) => {

  // ── EMPTY STATE ───────────────────────────────────────────
  // If no incident has been selected yet, show a placeholder
  // so the panel doesn't just appear blank.
  if (!incident) {
    return (
      // The outer div always has "detail-panel" for consistent sizing/layout
      <div className="detail-panel">
        <div className="detail-empty">
          {/* Arrow icon pointing left toward the table */}
          <p className="empty-icon">👈</p>
          <p className="empty-message">
            Select an incident from the table to view details
          </p>
        </div>
      </div>
    )
  }

  // ── HELPER: Format dates nicely ───────────────────────────
  // The database stores dates as ISO strings like "2025-03-31T14:22:00"
  // We convert them to readable format like "Mar 31, 2025, 2:22 PM"
  const formatDate = (dateString) => {
    // If no date exists, return a fallback string
    if (!dateString) return 'Unknown'
    // JavaScript's built-in Date object parses the ISO string
    // toLocaleString() formats it for the user's locale automatically
    return new Date(dateString).toLocaleString()
  }

  // ── HELPER: Get CSS class for severity color ───────────────
  // Returns a class name based on severity level so we can
  // color-code the badge: red for critical, orange for high, etc.
  const getSeverityClass = (severity) => {
    // Use a lookup object (faster and cleaner than if/else chain)
    const classes = {
      critical: 'severity-badge--critical',  // Red
      high:     'severity-badge--high',       // Orange
      medium:   'severity-badge--medium',     // Yellow
      low:      'severity-badge--low',        // Green
    }
    // Return the matching class, or the medium class as default
    // The ?. (optional chaining) prevents errors if severity is null
    return classes[severity?.toLowerCase()] || 'severity-badge--medium'
  }

  // ── HELPER: Format risk score as percentage ────────────────
  // The database stores risk_score as a decimal (0.0 to 1.0)
  // We convert 0.87 → "87%" for display
  const formatRiskScore = (score) => {
    // If score is null or undefined, show a dash
    if (score === null || score === undefined) return '—'
    // Multiply by 100, round to nearest integer, add % sign
    return `${Math.round(score * 100)}%`
  }

  // ── MAIN RENDER ───────────────────────────────────────────
  // Now we render the full incident detail panel.
  // Sections in order:
  //   1. Panel header (title + close button)
  //   2. Severity badge (prominent at top)
  //   3. Core info (type, source, description, location, dates)
  //   4. AI Analysis section (risk score, incident type, severity)
  //   5. Transcript panel (THE NEW DAY 35 FEATURE)
  //   6. AI Summary (if exists)
  //   7. Attached media (audio/image file paths)
  //   8. Panel footer (close button)
  return (
    // Outer wrapper — "detail-panel" gives the panel its width, height, border
    <div className="detail-panel">

      {/* ── SECTION 1: PANEL HEADER ─────────────────────────── */}
      {/* Shows the incident ID as a title and an X close button */}
      <div className="detail-header">
        <h2 className="detail-title">
          {/* Display incident ID so dispatcher knows which record this is */}
          Incident #{incident.id}
        </h2>
        {/* Close button — calls onClose() which hides the panel */}
        {/* onClose is passed in as a prop from the parent component */}
        <button
          className="detail-close-btn"
          onClick={onClose}
          // Accessible label for screen readers
          aria-label="Close incident detail panel"
        >
          ✕
        </button>
      </div>

      {/* ── SCROLLABLE CONTENT AREA ─────────────────────────── */}
      {/* This div scrolls independently so the header/footer stay fixed */}
      <div className="detail-content">

        {/* ── SECTION 2: SEVERITY BADGE ─────────────────────── */}
        {/* Big colored badge at the top — first thing dispatcher sees */}
        <div className="detail-severity-row">
          <span className={`severity-badge ${getSeverityClass(incident.severity)}`}>
            {/* Show severity in uppercase, default to MEDIUM if missing */}
            {incident.severity ? incident.severity.toUpperCase() : 'MEDIUM'}
          </span>
          {/* Status badge next to severity */}
          <span className={`status-badge status-badge--${incident.status || 'pending'}`}>
            {incident.status ? incident.status.toUpperCase() : 'PENDING'}
          </span>
        </div>

        {/* ── SECTION 3: CORE INFORMATION ──────────────────── */}
        {/* Fields that were entered by the human submitting the report */}

        {/* Description — the free-text summary of the incident */}
        <div className="detail-field">
          {/* Label has NO AI badge because humans write descriptions */}
          <label className="detail-label">Description</label>
          <p className="detail-value description-full">
            {incident.description}
          </p>
        </div>

        {/* Location */}
        <div className="detail-field">
          <label className="detail-label">Location</label>
          <p className="detail-value">
            📍 {incident.location || 'Not specified'}
          </p>
        </div>

        {/* Reported by (source) */}
        <div className="detail-field">
          <label className="detail-label">Reported By</label>
          <p className="detail-value">
            {/* Capitalize first letter: "citizen" → "Citizen" */}
            {incident.source
              ? incident.source.charAt(0).toUpperCase() + incident.source.slice(1)
              : 'Unknown'}
          </p>
        </div>

        {/* Timestamps — when the incident was created and last updated */}
        <div className="detail-field">
          <label className="detail-label">Reported At</label>
          <p className="detail-value">
            🕐 {formatDate(incident.created_at)}
          </p>
        </div>

        {/* ── SECTION 4: AI ANALYSIS ───────────────────────── */}
        {/* Divider heading to visually separate AI fields from human fields */}
        <div className="section-divider">
          <h3 className="section-divider__title">🤖 AI Analysis</h3>
        </div>

        {/* Incident Type — classified by AI */}
        <div className="detail-field">
          {/* Label row has both the text AND the AI badge */}
          <label className="detail-label">
            Incident Type <AIBadge />
          </label>
          <p className="detail-value incident-type-value">
            {/* Show in uppercase, default to OTHER */}
            {incident.incident_type
              ? incident.incident_type.toUpperCase()
              : 'OTHER'}
          </p>
        </div>

        {/* Severity (AI-assessed) */}
        {/* Note: severity also appears as a badge at top, but we
            show it here too with context that it's AI-generated */}
        <div className="detail-field">
          <label className="detail-label">
            Severity <AIBadge />
          </label>
          <p className="detail-value">
            {incident.severity ? incident.severity.toUpperCase() : 'MEDIUM'}
          </p>
        </div>

        {/* Risk Score — a 0-1 probability score from the AI */}
        <div className="detail-field">
          <label className="detail-label">
            Risk Score <AIBadge />
          </label>
          {/* Show as a percentage with a color class */}
          <p className={`detail-value risk-score-value ${
            // Add extra class for high-risk scores so they appear red
            incident.risk_score > 0.7
              ? 'risk-score-value--high'
              : incident.risk_score > 0.4
                ? 'risk-score-value--medium'
                : 'risk-score-value--low'
          }`}>
            {formatRiskScore(incident.risk_score)}
          </p>
        </div>

        {/* AI Summary — a short paragraph the AI wrote about the incident */}
        {/* Only render if a summary exists (it might not for older incidents) */}
        {incident.summary && (
          <div className="detail-field">
            <label className="detail-label">
              AI Summary <AIBadge />
            </label>
            <p className="detail-value summary-text">
              {incident.summary}
            </p>
          </div>
        )}

        {/* ── SECTION 5: TRANSCRIPT PANEL (DAY 35 FEATURE) ─── */}
        {/* This section heading only appears if audio exists */}
        {incident.audio_path && (
          <div className="section-divider">
            <h3 className="section-divider__title">🎤 Audio</h3>
          </div>
        )}

        {/* TranscriptPanel handles all 3 states internally */}
        {/* We just pass the whole incident and it figures out what to show */}
        <TranscriptPanel incident={incident} />

        {/* ── SECTION 6: ATTACHED MEDIA ────────────────────── */}
        {/* Show file paths for any uploaded files */}
        {/* This section only renders if at least one file exists */}
        {(incident.audio_path || incident.image_path) && (
          <>
            {/* Divider for the media section */}
            <div className="section-divider">
              <h3 className="section-divider__title">📎 Attached Files</h3>
            </div>

            {/* Audio file path */}
            {incident.audio_path && (
              <div className="detail-field">
                <label className="detail-label">Audio File</label>
                {/* Show the filename, not the full path */}
                {/* .split('/').pop() extracts just the filename from the path */}
                <p className="detail-value file-path">
                  🎧 {incident.audio_path.split('/').pop()}
                </p>
              </div>
            )}

            {/* Image file path */}
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
      {/* END: detail-content scrollable area */}

      {/* ── SECTION 7: PANEL FOOTER ──────────────────────────── */}
      {/* Fixed at the bottom — contains action buttons */}
      <div className="detail-footer">
        {/* Close button at the bottom (mirrors the X button at the top) */}
        <button
          className="btn btn--secondary"
          onClick={onClose}
        >
          Close
        </button>
        {/* Placeholder for future "Dispatch" or "Acknowledge" buttons */}
        {/* These will be added in later days when we add status management */}
      </div>

    </div>
  )
}

// Export the component so other files can import and use it
// App.jsx imports this and renders it in the right side of the dashboard
export default IncidentDetail