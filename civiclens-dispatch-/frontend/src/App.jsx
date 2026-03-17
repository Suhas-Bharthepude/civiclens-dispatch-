// frontend/src/App.jsx
// Main App component - now manages selected incident state
// Shows detail panel when incident is clicked

// Import CSS
import './App.css'

// Import components
import HealthCheck from './HealthCheck'
import IncidentsList from './IncidentsList'
import IncidentDetail from './components/IncidentDetail'

// Import useEffect at top
import { useState, useEffect } from 'react'

import SubmitIncidentForm from './components/SubmitIncidentForm'



// ========================================
// APP COMPONENT
// ========================================

function App() {
  
  // ========================================
  // STATE - Selected Incident
  // ========================================
  
  // State: currently selected incident for detail view
  // Starts as null (no incident selected)
  // When user clicks a row, this becomes the incident object
  const [selectedIncident, setSelectedIncident] = useState(null)
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  
  // selectedIncident will be:
  // - null (no selection) → detail panel hidden
  // - incident object (selected) → detail panel shown

  // ========================================
  // KEYBOARD SHORTCUT - ESC to Close
  // ========================================

  // useEffect to listen for ESC key press
  useEffect(() => {
      // Define function that handles keydown events
      function handleKeyDown(event) {
          // If ESC key (key code 27) and panel is open
          if (event.key === 'Escape' && selectedIncident) {
              // Close the detail panel
              handleCloseDetail();
          }
      }
      
      // Add event listener to document
      // Listens for any keydown event on the page
      document.addEventListener('keydown', handleKeyDown);
      
      // Cleanup function - runs when component unmounts
      // Removes event listener to prevent memory leaks
      return () => {
          document.removeEventListener('keydown', handleKeyDown);
      };
      
      // Dependency: selectedIncident
      // Re-run effect when selectedIncident changes
  }, [selectedIncident]);
    
  
  
  
  
  // ========================================
  // EVENT HANDLERS
  // ========================================
  
  // Called when user clicks an incident row in the table
  // incident parameter is the clicked incident object
  function handleIncidentClick(incident) {
    // Log for debugging
    console.log('Incident clicked:', incident);
    
    // Update state with selected incident
    // This triggers re-render and shows detail panel
    setSelectedIncident(incident);
  }
  
  // Called when user closes the detail panel
  function handleCloseDetail() {
    // Log for debugging
    console.log('Closing detail panel');
    
    // Clear selected incident (set back to null)
    // This triggers re-render and hides detail panel
    setSelectedIncident(null);
  }

  // Add this function after handleCloseDetail
  function handleIncidentSubmitted() {
    console.log('New incident submitted! Refreshing list...');
    
    // Increment refresh trigger
    // This causes IncidentsList to re-fetch
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
            HEADER
            ======================================== */}
        <header className="app-header">
          <h1>🚨 CivicLens Dispatch</h1>
          <p>Emergency Incident Triage System</p>
          
          {/* Version badge */}
          <span style={{
            display: 'inline-block',
            marginTop: '10px',
            padding: '4px 12px',
            backgroundColor: 'rgba(255, 255, 255, 0.2)',
            borderRadius: '12px',
            fontSize: '0.85rem'
          }}>
            v1.0.0 - Day 26
          </span>
        </header>
        
        {/* ========================================
            MAIN CONTENT
            ======================================== */}

        
        <main className="app-main">
          
          {/* API Health Check */}
          <HealthCheck />
          
          {/* Incident Submission Form */}
          <SubmitIncidentForm onIncidentSubmitted={handleIncidentSubmitted} />



          {/* Incidents List with Table */}
          {/* Pass handleIncidentClick as prop */}
          {/* Child will call this when row is clicked */}
          <IncidentsList 
              onIncidentClick={handleIncidentClick}
              refreshTrigger={refreshTrigger}
          />
          
        </main>
        
        {/* ========================================
            FOOTER
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
      
      {/* ========================================
          DETAIL PANEL (Conditional)
          ======================================== */}
      
      {/* Only render detail panel if an incident is selected */}
      {/* && means: if left side is truthy, render right side */}
      {/* If selectedIncident is null, nothing renders */}
      {/* If selectedIncident has data, IncidentDetail renders */}
      {selectedIncident && (
        <IncidentDetail 
          incident={selectedIncident}
          onClose={handleCloseDetail}
        />
      )}
      
    </>
  )
}

export default App



