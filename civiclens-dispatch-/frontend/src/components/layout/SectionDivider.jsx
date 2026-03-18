// frontend/src/components/SectionDivider.jsx
// Simple divider component for separating content sections
// Improves visual hierarchy and readability

import React from 'react'
import './SectionDivider.css'


// ========================================
// SECTION DIVIDER COMPONENT
// ========================================

// Component that renders a horizontal divider with optional title
// Props:
//   - title: Optional text to display on the divider
function SectionDivider({ title }) {
  
  // If title provided, show divider with title
  if (title) {
    return (
      <div className="section-divider">
        {/* Line on left */}
        <div className="divider-line"></div>
        
        {/* Title text */}
        <span className="divider-title">{title}</span>
        
        {/* Line on right */}
        <div className="divider-line"></div>
      </div>
    )
  }
  
  // If no title, show simple line
  return <hr className="simple-divider" />
}

export default SectionDivider