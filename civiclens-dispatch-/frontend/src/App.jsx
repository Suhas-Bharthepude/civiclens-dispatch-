// frontend/src/App.jsx
// Main App component with two-column dashboard layout
// Left column: Submission form and filters
// Right column: Incidents table

// ========================================
// REACT IMPORTS (Always first)
// ========================================

// Import React hooks
import { useState, useEffect } from 'react'


// ========================================
// STYLE IMPORTS
// ========================================

// Import CSS
import './App.css'


// ========================================
// CUSTOM HOOKS
// ========================================

import useToast from './hooks/useToast'


// ========================================
// COMPONENTS
// ========================================

import HealthCheck from './HealthCheck'
import IncidentsList from './IncidentsList'
import IncidentDetail from './components/IncidentDetail'
import SubmitIncidentForm from './components/SubmitIncidentForm'
import DashboardLayout from './components/DashboardLayout'
import ToastContainer from './components/ToastContainer'


// ========================================
// APP COMPONENT
// ========================================

function App() {
  
  // ========================================
  // STATE MANAGEMENT
  // ========================================
  
  // State: currently selected incident for detail view
  // null = no selection, object = incident selected
  const [selectedIncident, setSelectedIncident] = useState(null)
  
  // State: refresh trigger for incidents list
  // Increments when new incident is submitted
  // Causes IncidentsList to re-fetch data
  const [refreshTrigger, setRefreshTrigger] = useState(0)
  
  const { toasts, showToast, removeToast } = useToast()
  
  // ========================================
  // KEYBOARD SHORTCUT - ESC to Close Detail
  // ========================================
  
  // Listen for ESC key to close detail panel
  useEffect(() => {
    // Define keyboard event handler
    function handleKeyDown(event) {
      // If ESC key pressed and panel is open
      if (event.key === 'Escape' && selectedIncident) {
        // Close the detail panel
        handleCloseDetail();
      }
    }
    
    // Add event listener to document
    document.addEventListener('keydown', handleKeyDown);
    
    // Cleanup function - removes listener when component unmounts
    // This prevents memory leaks
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
    
    // Re-run effect when selectedIncident changes
  }, [selectedIncident]);
  
  
  // ========================================
  // EVENT HANDLERS
  // ========================================
  
  // Called when user clicks an incident row in table
  function handleIncidentClick(incident) {
    console.log('Incident clicked:', incident);
    // Set selected incident (opens detail panel)
    setSelectedIncident(incident);
  }
  
  // Called when user closes detail panel
  function handleCloseDetail() {
    console.log('Closing detail panel');
    // Clear selected incident (hides detail panel)
    setSelectedIncident(null);
  }
  
  // Called when new incident is submitted via form
  function handleIncidentSubmitted() {
    console.log('New incident submitted! Refreshing list...');
    
    // Show success toast
    showToast('Incident submitted successfully! Dispatchers notified.', 'success');
    
    // Refresh the incidents list
    setRefreshTrigger(prev => prev + 1);
  }
  
  
  // ========================================
  // RETURN JSX
  // ========================================
  
  return (
    <>
      {/* Main app container */}
      <div className="app-container">
        
        {/* ========================================
            HEADER - Full Width
            ======================================== */}
        <header className="app-header">
          {/* Main title */}
          <h1>🚨 CivicLens Dispatch</h1>
          
          {/* Subtitle */}
          <p>Emergency Incident Triage System</p>
          
          {/* Version badge */}
          <span className="version-badge">
            v1.0.0 - Day 28
          </span>
        </header>
        
        {/* ========================================
            MAIN CONTENT AREA
            ======================================== */}
        <main className="app-main">
          
          {/* API Health Check - Full Width */}
          <HealthCheck />
          
          {/* ========================================
              TWO-COLUMN LAYOUT
              ======================================== */}
          
          {/* Use DashboardLayout component */}
          {/* leftColumn prop receives JSX for left side */}
          {/* rightColumn prop receives JSX for right side */}
          {/* leftWidth={1} and rightWidth={2} means 1:2 ratio (left gets 1/3, right gets 2/3) */}
          <DashboardLayout
            leftWidth={1}
            rightWidth={2}
            
            leftColumn={
              // Left column: Submission form
              <>
                {/* Section title for left column */}
                <div className="column-header">
                  <h3>📝 Report Incident</h3>
                  <p className="column-description">
                    Submit a new incident report
                  </p>
                </div>
                
                {/* Submission form component */}
                <SubmitIncidentForm onIncidentSubmitted={handleIncidentSubmitted} />
              </>
            }
            
            rightColumn={
              // Right column: Incidents table
              <>
                {/* Incidents list with table */}
                {/* Pass click handler and refresh trigger */}
                <IncidentsList 
                  onIncidentClick={handleIncidentClick}
                  refreshTrigger={refreshTrigger}
                />

            
              </>
            }
          />
          
        </main>
        
        {/* ========================================
            FOOTER - Full Width
            ======================================== */}
        <footer className="app-footer">
          <p>CivicLens Dispatch © 2024 | Built with React + FastAPI</p>
          <p className="footer-note">
            🚨 For true emergencies, always call 911. This system is for incident triage and non-emergency reporting.
          </p>
        </footer>
        
      </div>
      
      {/* ========================================
          DETAIL PANEL (Conditional Render)
          ======================================== */}
      
      {/* Only render detail panel if incident is selected */}
      {selectedIncident && (
        <IncidentDetail 
          incident={selectedIncident}
          onClose={handleCloseDetail}
        />
      )}

      
      {/* Toast notification container */}
        <ToastContainer 
          toasts={toasts}
          removeToast={removeToast}
        />
      
    </>
  )
}

export default App