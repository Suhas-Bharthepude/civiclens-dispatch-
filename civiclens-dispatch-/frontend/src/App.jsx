// frontend/src/App.jsx
// Main App component - displays the dispatcher dashboard
// Now shows real incidents in a professional table format

// Import React hooks (we might use useState later for filters)
import { useState } from 'react'

// Import CSS for styling
import './App.css'

// Import our custom components
import HealthCheck from './HealthCheck'
import IncidentsList from './IncidentsList'


// ========================================
// APP COMPONENT
// ========================================

// Main application component
// This is the root component that contains everything
function App() {
  
  // ========================================
  // STATE (for future features)
  // ========================================
  
  // We'll add filter state here tomorrow (Day 26)
  // For now, just showing all incidents
  
  
  // ========================================
  // RETURN JSX
  // ========================================
  
  return (
    // Fragment - wraps multiple elements without adding div
    <>
      {/* Main app container */}
      <div className="app-container">
        
        {/* ========================================
            HEADER - Top Navigation Bar
            ======================================== */}
        <header className="app-header">
          {/* Application title */}
          <h1>🚨 CivicLens Dispatch</h1>
          
          {/* Subtitle */}
          <p>Emergency Incident Triage System</p>
          
          {/* Version badge (optional) */}
          <span style={{
            display: 'inline-block',
            marginTop: '10px',
            padding: '4px 12px',
            backgroundColor: 'rgba(255, 255, 255, 0.2)',
            borderRadius: '12px',
            fontSize: '0.85rem'
          }}>
            v1.0.0 - Day 25
          </span>
        </header>
        
        {/* ========================================
            MAIN CONTENT AREA
            ======================================== */}
        <main className="app-main">
          
          {/* Health Check Component */}
          {/* Shows green box if backend is connected */}
          {/* Shows red box with error if backend is down */}
          <HealthCheck />
          
          {/* Incidents List Component */}
          {/* Fetches incidents from API */}
          {/* Displays them in a professional table */}
          {/* Handles loading, error, and empty states */}
          <IncidentsList />
          
        </main>
        
        {/* ========================================
            FOOTER (Optional)
            ======================================== */}
        <footer style={{
          textAlign: 'center',
          padding: '20px',
          color: '#999',
          fontSize: '0.85rem'
        }}>
          <p>CivicLens Dispatch © 2024 | Built with React + FastAPI</p>
        </footer>
        
      </div>
    </>
  )
}

// ========================================
// EXPORT
// ========================================

// Export App component as default
// main.jsx imports this and renders it
export default App