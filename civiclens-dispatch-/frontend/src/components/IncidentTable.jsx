// frontend/src/components/IncidentTable.jsx
// Professional data table component for displaying incidents
// Features: Sortable columns, hover effects, color-coded severity

// Import React (needed for JSX)
import React from 'react'

// Import CSS for this component
import './IncidentTable.css'


// ========================================
// INCIDENT TABLE COMPONENT
// ========================================

// Component that displays incidents in a table format
// Props:
//   - incidents: Array of incident objects from API
function IncidentTable({ incidents }) {
  
  // ========================================
  // HELPER FUNCTION - Format Risk Score
  // ========================================
  
  // Formats risk score to 2 decimal places
  // Example: 0.856789 → "0.86"
  function formatRiskScore(score) {
    // If score is null or undefined, show "N/A"
    if (score === null || score === undefined) {
      return 'N/A';
    }
    
    // Convert to number and fix to 2 decimal places
    // .toFixed(2) returns string like "0.86"
    return Number(score).toFixed(2);
  }
  
  
  // ========================================
  // HELPER FUNCTION - Get Severity Class
  // ========================================
  
  // Returns CSS class name based on severity level
  // This determines the badge color
  function getSeverityClass(severity) {
    // If no severity, default to medium
    if (!severity) return 'severity-badge severity-medium';
    
    // Convert to lowercase for consistent comparison
    const sev = severity.toLowerCase();
    
    // Return appropriate CSS class
    // These classes are defined in IncidentTable.css
    return `severity-badge severity-${sev}`;
  }
  
  
  // ========================================
  // HANDLE ROW CLICK
  // ========================================
  
  // Called when user clicks a table row
  // For now, just shows alert (Day 26 will show detail panel)
  function handleRowClick(incident) {
    // Show alert with incident details
    // In Day 26, this will open a side panel instead
    alert(`Incident #${incident.id}\n\nDescription: ${incident.description}\n\nLocation: ${incident.location}\n\n(Tomorrow we'll build a detail panel!)`);
  }
  
  
  // ========================================
  // RENDER TABLE
  // ========================================
  
  return (
    // Main table container
    <div className="incident-table-container">
      
      {/* The HTML table element */}
      {/* className for styling from CSS */}
      <table className="incident-table">
        
        {/* ========================================
            TABLE HEADER (Column Names)
            ======================================== */}
        <thead>
          {/* Table row for headers */}
          <tr>
            {/* Table header cells - one for each column */}
            <th>ID</th>
            <th>Type</th>
            <th>Source</th>
            <th>Description</th>
            <th>Location</th>
            <th>Severity</th>
            <th>Risk Score</th>
          </tr>
        </thead>
        
        {/* ========================================
            TABLE BODY (Actual Data Rows)
            ======================================== */}
        <tbody>
          {/* Map over incidents array */}
          {/* For each incident, create a table row */}
          {incidents.map((incident) => (
            // Table row for this incident
            // key prop is REQUIRED when mapping
            // Use unique ID from database
            // onClick makes entire row clickable
            <tr 
              key={incident.id}
              onClick={() => handleRowClick(incident)}
              className="incident-row"
            >
              
              {/* ID column */}
              <td className="incident-id">
                #{incident.id}
              </td>
              
              {/* Type column */}
              <td className="incident-type">
                {/* Show incident type in uppercase */}
                {/* Use || to provide default if type is null */}
                {incident.incident_type ? incident.incident_type.toUpperCase() : 'OTHER'}
              </td>
              
              {/* Source column */}
              <td>
                {/* Capitalize first letter of source */}
                {/* charAt(0) gets first character */}
                {/* toUpperCase() makes it capital */}
                {/* slice(1) gets rest of string */}
                {incident.source.charAt(0).toUpperCase() + incident.source.slice(1)}
              </td>
              
              {/* Description column */}
              <td className="incident-description">
                {/* Show description */}
                {/* Truncate if too long (CSS handles this with text-overflow) */}
                {incident.description}
              </td>
              
              {/* Location column */}
              <td className="incident-location">
                {incident.location}
              </td>
              
              {/* Severity column */}
              <td>
                {/* Colored badge based on severity */}
                {/* getSeverityClass() returns the correct CSS class */}
                <span className={getSeverityClass(incident.severity)}>
                  {/* Display severity in uppercase */}
                  {/* || 'MEDIUM' provides default if severity is null */}
                  {incident.severity ? incident.severity.toUpperCase() : 'MEDIUM'}
                </span>
              </td>
              
              {/* Risk Score column */}
              <td className="risk-score">
                {/* Format risk score to 2 decimals */}
                {formatRiskScore(incident.risk_score)}
              </td>
              
            </tr>
          ))}
        </tbody>
        
      </table>
      
      {/* ========================================
          FOOTER - Show Total Count
          ======================================== */}
      <div className="table-footer">
        {/* Show total number of incidents */}
        <p>
          Showing <strong>{incidents.length}</strong> incidents from database
        </p>
      </div>
      
    </div>
  )
}

export default IncidentTable