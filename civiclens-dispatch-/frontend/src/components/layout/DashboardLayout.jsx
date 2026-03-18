// frontend/src/components/DashboardLayout.jsx
// Reusable layout component for two-column dashboard design
// Left column: Forms, filters, controls
// Right column: Data, tables, results

// Import React
import React from 'react'

// Import CSS
import './DashboardLayout.css'


// ========================================
// DASHBOARD LAYOUT COMPONENT
// ========================================

// Flexible two-column layout component
// Props:
//   - leftColumn: JSX to display in left column
//   - rightColumn: JSX to display in right column
//   - leftWidth: Optional width ratio for left column (default: 1)
//   - rightWidth: Optional width ratio for right column (default: 2)
function DashboardLayout({ leftColumn, rightColumn, leftWidth = 1, rightWidth = 2 }) {
  
  // ========================================
  // RETURN JSX
  // ========================================
  
  return (
    // Main container for the layout
    // CSS class handles flexbox layout
    <div className="dashboard-layout">
      
      {/* ========================================
          LEFT COLUMN
          ======================================== */}
      
      {/* Left column for forms, filters, controls */}
      {/* style prop sets flex ratio dynamically */}
      {/* flex: leftWidth means this column gets 'leftWidth' portions of space */}
      {/* Example: if leftWidth=1 and rightWidth=2, left gets 1/3, right gets 2/3 */}
      <div className="dashboard-left" style={{ flex: leftWidth }}>
        {/* Render whatever was passed as leftColumn prop */}
        {leftColumn}
      </div>
      
      {/* ========================================
          RIGHT COLUMN
          ======================================== */}
      
      {/* Right column for data display, tables, results */}
      {/* Gets 'rightWidth' portions of available space */}
      <div className="dashboard-right" style={{ flex: rightWidth }}>
        {/* Render whatever was passed as rightColumn prop */}
        {rightColumn}
      </div>
      
    </div>
  )
}

export default DashboardLayout