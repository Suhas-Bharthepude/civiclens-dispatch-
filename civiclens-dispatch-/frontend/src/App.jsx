// frontend/src/App.jsx
// Main App component - now fetches real data from backend!

// Import useState hook (we'll use this later for filters)
import { useState } from 'react'

// Import CSS
import './App.css'

// Import our custom components
import HealthCheck from './HealthCheck'
import IncidentsList from './IncidentsList'


// ========================================
// APP COMPONENT
// ========================================

function App() {
  
  // ========================================
  // RETURN JSX
  // ========================================
  
  return (
    <>
      <div className="app-container">
        
        {/* Header */}
        <header className="app-header">
          <h1>🚨 CivicLens Dispatch</h1>
          <p>Emergency Incident Triage System</p>
        </header>
        
        {/* Main content */}
        <main className="app-main">
          
          {/* API health check */}
          <HealthCheck />
          
          {/* Real incidents from database */}
          <IncidentsList />
          
        </main>
        
      </div>
    </>
  )
}

export default App