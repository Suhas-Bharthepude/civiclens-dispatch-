// frontend/src/components/IncidentDetail.jsx
// Detail panel component that shows full information for one incident
// Appears as a side panel when user clicks an incident row

// Import React
import React from 'react'

// Import CSS for this component
import './IncidentDetail.css'


// ========================================
// INCIDENT DETAIL COMPONENT
// ========================================

// Component that displays detailed view of one incident
// Props:
//   - incident: The incident object to display (from API)
//   - onClose: Function to call when user clicks close button
function IncidentDetail({ incident, onClose }) {
  
  // ========================================
  // HELPER FUNCTION - Format Date
  // ========================================
  
  // Formats ISO date string to readable format
  // Example: "2024-01-15T10:30:00" → "Jan 15, 2024 at 10:30 AM"
  function formatDate(dateString) {
    // If no date, return N/A
    if (!dateString) return 'N/A';
    
    // Create Date object from string
    const date = new Date(dateString);
    
    // Format using toLocaleString
    // This automatically formats based on user's locale
    return date.toLocaleString('en-US', {
      month: 'short',  // "Jan"
      day: 'numeric',  // "15"
      year: 'numeric', // "2024"
      hour: 'numeric', // "10"
      minute: '2-digit', // "30"
      hour12: true     // "AM/PM"
    });
  }
  
  
  // ========================================
  // HELPER FUNCTION - Get Severity Color
  // ========================================
  
  // Returns color for severity badge
  function getSeverityColor(severity) {
    // If no severity, default to gray
    if (!severity) return '#95a5a6';
    
    // Map severity levels to colors
    const colors = {
      'low': '#27ae60',      // Green
      'medium': '#f39c12',   // Orange
      'high': '#e74c3c',     // Red
      'critical': '#c0392b'  // Dark red
    };
    
    // Return color for this severity (default to gray)
    return colors[severity.toLowerCase()] || '#95a5a6';
  }
  
  
  // ========================================
  // RENDER DETAIL PANEL
  // ========================================
  
  return (
    // Overlay - dark background behind panel
    // Clicking overlay closes the panel
    <div className="detail-overlay" onClick={onClose}>
      
      {/* Detail panel - slides in from right */}
      {/* onClick with stopPropagation prevents closing when clicking inside panel */}
      {/* stopPropagation() stops the click event from bubbling up to overlay */}
      <div className="detail-panel" onClick={(e) => e.stopPropagation()}>
        
        {/* ========================================
            PANEL HEADER
            ======================================== */}
        <div className="detail-header">
          {/* Title with incident ID */}
          <h2>Incident #{incident.id}</h2>
          
          {/* Close button */}
          {/* onClick calls onClose function passed from parent */}
          <button className="close-button" onClick={onClose}>
            ✕
          </button>
        </div>
        
        {/* ========================================
            PANEL CONTENT (Scrollable)
            ======================================== */}
        <div className="detail-content">
          
          {/* Severity Badge - Prominent */}
          <div className="detail-severity">
            <span 
              className="severity-badge-large"
              style={{ backgroundColor: getSeverityColor(incident.severity) }}
            >
              {incident.severity ? incident.severity.toUpperCase() : 'MEDIUM'}
            </span>
          </div>
          
          {/* ========================================
              CORE INFORMATION
              ======================================== */}
          
          {/* Incident Type */}
          <div className="detail-field">
            <label>Incident Type</label>
            <p className="field-value incident-type-value">
              {incident.incident_type ? incident.incident_type.toUpperCase() : 'OTHER'}
            </p>
          </div>
          
          {/* Source */}
          <div className="detail-field">
            <label>Reported By</label>
            <p className="field-value">
              {/* Capitalize first letter */}
              {incident.source.charAt(0).toUpperCase() + incident.source.slice(1)}
            </p>
          </div>
          
          {/* Description */}
          <div className="detail-field">
            <label>Description</label>
            {/* Full description - not truncated like in table */}
            <p className="field-value description-full">
              {incident.description}
            </p>
          </div>
          
          {/* Location */}
          <div className="detail-field">
            <label>Location</label>
            <p className="field-value">
              📍 {incident.location}
            </p>
          </div>
          
          {/* ========================================
              AI-GENERATED FIELDS
              ======================================== */}
          
          <div className="section-divider">
            <h3>AI Analysis</h3>
          </div>
          
          {/* Risk Score */}
          <div className="detail-field">
            <label>Risk Score</label>
            <p className="field-value risk-score-value">
              {/* Show risk score as percentage or N/A */}
              {incident.risk_score !== null 
                ? `${(incident.risk_score * 100).toFixed(0)}%` 
                : 'Not calculated yet'}
            </p>
          </div>
          
          {/* AI Transcript */}
          {/* Only show if transcript exists */}
          {incident.transcript && (
            <div className="detail-field">
              <label>Audio Transcript</label>
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
              MEDIA FILES
              ======================================== */}
          
          {/* Only show this section if audio or image exists */}
          {(incident.audio_path || incident.image_path) && (
            <>
              <div className="section-divider">
                <h3>Attached Media</h3>
              </div>
              
              {/* Audio file indicator */}
              {incident.audio_path && (
                <div className="detail-field">
                  <label>Audio Recording</label>
                  <p className="field-value">
                    🎧 {incident.audio_path}
                  </p>
                  <p className="field-note">
                    (Audio playback will be added in future update)
                  </p>
                </div>
              )}
              
              {/* Image file indicator */}
              {incident.image_path && (
                <div className="detail-field">
                  <label>Photo</label>
                  <p className="field-value">
                    📷 {incident.image_path}
                  </p>
                  <p className="field-note">
                    (Image viewer will be added in future update)
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
          {/* Close button (alternative to X button) */}
          <button className="btn-secondary" onClick={onClose}>
            Close
          </button>
          
          {/* Future action buttons */}
          <button className="btn-primary" disabled>
            Edit Incident (Coming Soon)
          </button>
        </div>
        
      </div>
    </div>
  )
}

export default IncidentDetail