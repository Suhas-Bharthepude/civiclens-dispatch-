// frontend/src/components/LoadingSpinner.jsx
// Reusable loading spinner component
// Shows animated spinner while data is loading

import React from 'react'
import './LoadingSpinner.css'


// ========================================
// LOADING SPINNER COMPONENT
// ========================================

// Simple loading spinner component
// Props:
//   - message: Optional custom message (default: "Loading...")
function LoadingSpinner({ message = "Loading..." }) {
  return (
    // Container div
    <div className="loading-container">
      {/* Spinning circle animation */}
      {/* This is a CSS-only spinner (no images needed) */}
      <div className="spinner"></div>
      
      {/* Loading message */}
      <p className="loading-message">{message}</p>
    </div>
  )
}

export default LoadingSpinner