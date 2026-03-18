// frontend/src/App.jsx
// Main App component with two-column dashboard layout


// Import React hooks
import { useState, useEffect } from 'react'

// Import CSS
import './App.css'

// Import custom hooks
import useToast from './hooks/useToast'

// Import dashboard components
import HealthCheck from './components/dashboard/HealthCheck'
import IncidentsList from './components/dashboard/IncidentsList'
import IncidentDetail from './components/dashboard/IncidentDetail'

// Import form components
import SubmitIncidentForm from './components/forms/SubmitIncidentForm'

// Import layout components
import DashboardLayout from './components/layout/DashboardLayout'

// Import shared components
import ToastContainer from './components/shared/ToastContainer'


function App() {
  
  const [selectedIncident, setSelectedIncident] = useState(null)
  const [refreshTrigger, setRefreshTrigger] = useState(0)
  const { toasts, showToast, removeToast } = useToast()
  
  useEffect(() => {
    function handleKeyDown(event) {
      if (event.key === 'Escape' && selectedIncident) {
        handleCloseDetail();
      }
    }
    
    document.addEventListener('keydown', handleKeyDown);
    
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [selectedIncident]);
  
  function handleIncidentClick(incident) {
    console.log('Incident clicked:', incident);
    setSelectedIncident(incident);
  }
  
  function handleCloseDetail() {
    console.log('Closing detail panel');
    setSelectedIncident(null);
  }
  
  function handleIncidentSubmitted() {
    console.log('New incident submitted! Refreshing list...');
    showToast('Incident submitted successfully! Dispatchers notified.', 'success');
    setRefreshTrigger(prev => prev + 1);
  }
  
  return (
    <>
      <div className="app-container">
        
        <header className="app-header">
          <h1>🚨 CivicLens Dispatch</h1>
          <p>Emergency Incident Triage System</p>
          <span className="version-badge">v1.0.0 - Day 29</span>
        </header>
        
        <main className="app-main">
          
          <HealthCheck />
          
          <DashboardLayout
            leftWidth={1}
            rightWidth={2}
            
            leftColumn={
              <>
                <div className="column-header">
                  <h3>📝 Report Incident</h3>
                  <p className="column-description">
                    Submit a new incident report
                  </p>
                </div>
                
                <SubmitIncidentForm onIncidentSubmitted={handleIncidentSubmitted} />
              </>
            }
            
            rightColumn={
              <>
                <IncidentsList 
                  onIncidentClick={handleIncidentClick}
                  refreshTrigger={refreshTrigger}
                />
              </>
            }
          />
          
        </main>
        
        <footer className="app-footer">
          <p>CivicLens Dispatch © 2024 | Built with React + FastAPI</p>
          <p className="footer-note">
            🚨 For true emergencies, always call 911. This system is for incident triage and non-emergency reporting.
          </p>
        </footer>
        
      </div>
      
      {selectedIncident && (
        <IncidentDetail 
          incident={selectedIncident}
          onClose={handleCloseDetail}
        />
      )}
      
      <ToastContainer 
        toasts={toasts}
        removeToast={removeToast}
      />
      
    </>
  )
}

export default App