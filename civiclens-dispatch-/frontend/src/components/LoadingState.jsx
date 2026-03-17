// frontend/src/components/LoadingState.jsx
// Enhanced loading component with multiple styles
// Supports: spinner, skeleton screen, inline loading

// Import React
import React from 'react'

// Import CSS
import './LoadingState.css'


// ========================================
// LOADING STATE COMPONENT
// ========================================

// Flexible loading component that adapts to different use cases
// Props:
//   - type: 'spinner' (default), 'skeleton', or 'inline'
//   - message: Optional loading message
//   - rows: Number of skeleton rows (for skeleton type)
function LoadingState({ type = 'spinner', message = 'Loading...', rows = 3 }) {
  
  // ========================================
  // SPINNER TYPE (Circular Spinner)
  // ========================================
  
  if (type === 'spinner') {
    return (
      // Centered container
      <div className="loading-spinner-container">
        {/* Animated spinning circle */}
        {/* Pure CSS animation - no images needed */}
        <div className="loading-spinner"></div>
        
        {/* Loading message below spinner */}
        <p className="loading-message">{message}</p>
      </div>
    )
  }
  
  
  // ========================================
  // SKELETON TYPE (Placeholder Boxes)
  // ========================================
  
  if (type === 'skeleton') {
    return (
      // Container for skeleton rows
      <div className="loading-skeleton">
        {/* Create array of specified length and map to skeleton rows */}
        {/* Array(rows) creates array with 'rows' empty slots */}
        {/* .fill(0) fills slots with 0 */}
        {/* .map() transforms each item to JSX */}
        {Array(rows).fill(0).map((_, index) => (
          // Skeleton row - animated gray box
          // key is required for mapped elements
          <div key={index} className="skeleton-row">
            {/* Multiple skeleton items in each row */}
            <div className="skeleton-item skeleton-small"></div>
            <div className="skeleton-item skeleton-large"></div>
            <div className="skeleton-item skeleton-medium"></div>
          </div>
        ))}
      </div>
    )
  }
  
  
  // ========================================
  // INLINE TYPE (Small Spinner for Buttons)
  // ========================================
  
  if (type === 'inline') {
    return (
      // Inline container (doesn't take full width)
      <span className="loading-inline">
        {/* Small spinner */}
        <span className="loading-spinner-small"></span>
        {/* Message next to spinner */}
        <span>{message}</span>
      </span>
    )
  }
  
  
  // Default fallback (shouldn't reach here)
  return <div>{message}</div>
}

export default LoadingState