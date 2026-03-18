// frontend/src/components/dashboard/IncidentDetail.jsx
// Detail panel component that shows full information for one incident
// Appears as a side panel when user clicks an incident row
// Day 31: Enhanced to show audio file information

// Import React
import React from 'react'

// Import CSS for this component
import './IncidentDetail.css'


// ========================================
// INCIDENT DETAIL COMPONENT
// ========================================

// Component that displays detailed view of one incident
// Props:
//   - incident: The incident object to display (from API/database)
//   - onClose: Function to call when user clicks close button
function IncidentDetail({ incident, onClose }) {
  
  // ========================================
  // HELPER FUNCTION - Format Date
  // ========================================
  
  // Formats ISO date string to readable format
  // Example: "2024-01-15T10:30:00" → "Jan 15, 2024 at 10:30 AM"
  function formatDate(dateString) {
    // If no date provided, return N/A
    if (!dateString) return 'N/A';
    
    // Create Date object from ISO string
    const date = new Date(dateString);
    
    // Format using toLocaleString for readable output
    // This automatically formats based on user's locale/timezone
    return date.toLocaleString('en-US', {
      month: 'short',   // "Jan", "Feb", etc.
      day: 'numeric',   // "15"
      year: 'numeric',  // "2024"
      hour: 'numeric',  // "10"
      minute: '2-digit', // "30"
      hour12: true      // "AM/PM" format
    });
  }
  
  
  // ========================================
  // HELPER FUNCTION - Get Severity Color
  // ========================================
  
  // Returns background color for severity badge
  // Different colors for different severity levels
  function getSeverityColor(severity) {
    // If no severity provided, default to gray
    if (!severity) return '#95a5a6';
    
    // Map of severity level to color
    const colors = {
      'low': '#27ae60',      // Green
      'medium': '#f39c12',   // Orange
      'high': '#e74c3c',     // Red
      'critical': '#c0392b'  // Dark red
    };
    
    // Look up color by severity (convert to lowercase for case-insensitive match)
    // If severity not in map, default to gray
    return colors[severity.toLowerCase()] || '#95a5a6';
  }
  
  
  // ========================================
  // RENDER DETAIL PANEL
  // ========================================
  
  return (
    // Overlay - dark semi-transparent background behind panel
    // Clicking overlay closes the panel
    // onClick={onClose} calls the close function when overlay clicked
    <div className="detail-overlay" onClick={onClose}>
      
      {/* Detail panel - white box that slides in from right */}
      {/* onClick with stopPropagation prevents closing when clicking inside panel */}
      {/* e.stopPropagation() stops click event from bubbling up to overlay */}
      {/* Without this, clicking anywhere in panel would close it */}
      <div className="detail-panel" onClick={(e) => e.stopPropagation()}>
        
        {/* ========================================
            PANEL HEADER
            ======================================== */}
        <div className="detail-header">
          {/* Title with incident ID */}
          {/* {incident.id} embeds the incident ID number */}
          <h2>Incident #{incident.id}</h2>
          
          {/* Close button (X) */}
          {/* onClick calls onClose function passed from parent */}
          {/* aria-label for screen readers (accessibility) */}
          <button 
            className="close-button" 
            onClick={onClose}
            aria-label="Close detail panel"
          >
            ✕
          </button>
        </div>
        
        {/* ========================================
            PANEL CONTENT (Scrollable Area)
            ======================================== */}
        <div className="detail-content">
          
          {/* ========================================
              SEVERITY BADGE - Large and Prominent
              ======================================== */}
          
          <div className="detail-severity">
            {/* Large severity badge at top */}
            {/* style prop sets background color dynamically */}
            {/* getSeverityColor() returns correct color for this severity */}
            <span 
              className="severity-badge-large"
              style={{ backgroundColor: getSeverityColor(incident.severity) }}
            >
              {/* Display severity in uppercase */}
              {/* || 'MEDIUM' provides default if severity is null */}
              {incident.severity ? incident.severity.toUpperCase() : 'MEDIUM'}
            </span>
          </div>
          
          {/* ========================================
              CORE INFORMATION FIELDS
              ======================================== */}
          
          {/* Incident Type */}
          <div className="detail-field">
            <label>Incident Type</label>
            <p className="field-value incident-type-value">
              {/* Show incident type in uppercase, or "OTHER" if null */}
              {incident.incident_type ? incident.incident_type.toUpperCase() : 'OTHER'}
            </p>
          </div>
          
          {/* Source - Who reported this */}
          <div className="detail-field">
            <label>Reported By</label>
            <p className="field-value">
              {/* Capitalize first letter of source */}
              {/* .charAt(0) gets first character */}
              {/* .toUpperCase() makes it capital */}
              {/* .slice(1) gets rest of string */}
              {incident.source.charAt(0).toUpperCase() + incident.source.slice(1)}
            </p>
          </div>
          
          {/* Description - What happened */}
          <div className="detail-field">
            <label>Description</label>
            {/* Full description - not truncated like in table */}
            {/* CSS class .description-full allows wrapping and adds styling */}
            <p className="field-value description-full">
              {incident.description}
            </p>
          </div>
          
          {/* Location - Where it happened */}
          <div className="detail-field">
            <label>Location</label>
            <p className="field-value">
              {/* Pin emoji for visual indicator */}
              📍 {incident.location}
            </p>
          </div>
          
          {/* ========================================
              AI-GENERATED FIELDS SECTION
              ======================================== */}
          
          {/* Section divider with heading */}
          <div className="section-divider">
            <h3>AI Analysis</h3>
          </div>
          
          {/* Risk Score */}
          <div className="detail-field">
            <label>Risk Score</label>
            <p className="field-value risk-score-value">
              {/* Show risk score as percentage */}
              {/* Multiply by 100 to convert 0.85 → 85% */}
              {/* .toFixed(0) rounds to nearest integer */}
              {/* If risk_score is null, show "Not calculated yet" */}
              {incident.risk_score !== null 
                ? `${(incident.risk_score * 100).toFixed(0)}%` 
                : 'Not calculated yet'}
            </p>
          </div>
          
          {/* AI Transcript (from audio) */}
          {/* Only show this field if transcript exists */}
          {/* && means: only render if incident.transcript is truthy */}
          {incident.transcript && (
            <div className="detail-field">
              <label>Audio Transcript</label>
              {/* Display the transcript text */}
              {/* CSS class .transcript-text adds special styling */}
              <p className="field-value transcript-text">
                🎤 {incident.transcript}
              </p>
            </div>
          )}
          
          {/* AI Summary */}
          {/* Only show if summary exists */}
          {incident.summary && (
            <div className="detail-field">
              <label>AI Summary</label>
              <p className="field-value summary-text">
                📝 {incident.summary}
              </p>
            </div>
          )}
          
          {/* ========================================
              ATTACHED MEDIA FILES SECTION
              ======================================== */}
          
          {/* Only show this entire section if audio OR image exists */}
          {/* (condition1 || condition2) means show if EITHER is true */}
          {(incident.audio_path || incident.image_path) && (
            <>
              {/* Section divider */}
              <div className="section-divider">
                <h3>Attached Media</h3>
              </div>
              
              {/* Audio file information */}
              {/* Only show if audio_path exists (file was uploaded) */}
              {incident.audio_path && (
                <div className="detail-field">
                  <label>Audio Recording</label>
                  
                  {/* Show file path */}
                  <p className="field-value">
                    🎧 {incident.audio_path}
                  </p>
                  
                  {/* Helper note about file status */}
                  {/* Explains that file was uploaded and will be processed */}
                  <p className="field-note">
                    Audio file uploaded successfully. 
                    {/* If transcript doesn't exist yet, show processing message */}
                    {!incident.transcript && ' Transcription in progress...'}
                    {/* If transcript exists, show it's complete */}
                    {incident.transcript && ' Transcription complete (see above).'}
                  </p>
                </div>
              )}
              
              {/* Image file information */}
              {/* Only show if image_path exists */}
              {incident.image_path && (
                <div className="detail-field">
                  <label>Photo</label>
                  
                  {/* Show file path */}
                  <p className="field-value">
                    📷 {incident.image_path}
                  </p>
                  
                  {/* Helper note */}
                  <p className="field-note">
                    Image file uploaded successfully. 
                    Analysis will be processed automatically.
                  </p>
                </div>
              )}
            </>
          )}
          
        </div>
        
        {/* ========================================
            PANEL FOOTER (Action Buttons)
            ======================================== */}
        <div className="detail-footer">
          {/* Close button */}
          <button className="btn-secondary" onClick={onClose}>
            Close
          </button>
          
          {/* Edit button (disabled - future feature) */}
          <button className="btn-primary" disabled>
            Edit Incident (Coming Soon)
          </button>
        </div>
        
      </div>
    </div>
  )
}

// ========================================
// EXPORT
// ========================================

// Export as default export
// Allows importing: import IncidentDetail from './IncidentDetail'
export default IncidentDetail