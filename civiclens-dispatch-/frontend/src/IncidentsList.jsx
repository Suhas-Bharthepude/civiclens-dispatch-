// frontend/src/IncidentsList.jsx
// Container component that fetches incidents and displays them in a table
// Handles: API calls, loading states, error states

// Import React hooks
import { useState, useEffect } from 'react'

// Import API function to fetch incidents
import { getIncidents } from './api/client'

// Import IncidentTable component to display the data
import IncidentTable from './components/IncidentTable'


// ========================================
// INCIDENTS LIST COMPONENT
// ========================================

function IncidentsList() {
  
  // ========================================
  // STATE MANAGEMENT
  // ========================================
  
  // State: array of incidents fetched from API
  // Starts as empty array []
  const [incidents, setIncidents] = useState([])
  
  // State: loading indicator (true while fetching)
  // Starts as true because we fetch immediately
  const [loading, setLoading] = useState(true)
  
  // State: error message (null if no error)
  const [error, setError] = useState(null)
  
  
  // ========================================
  // FETCH DATA ON COMPONENT MOUNT
  // ========================================
  
  // useEffect runs after component renders
  // We use it to fetch data from API
  useEffect(() => {
    // Define async function inside useEffect
    // (useEffect callback itself can't be async)
    async function fetchIncidents() {
      try {
        // Log that we're starting the fetch
        console.log('Fetching incidents from API...');
        
        // Call API to get all incidents
        // This makes GET request to http://localhost:8000/incidents
        // await pauses here until response comes back
        const data = await getIncidents();
        
        // Log received data for debugging
        console.log('Received incidents:', data);
        
        // Update state with received data
        // This triggers a re-render with the new incidents
        setIncidents(data);
        
        // Turn off loading state (we're done fetching)
        setLoading(false);
        
      } catch (err) {
        // If API call fails, catch the error
        console.error('Failed to fetch incidents:', err);
        
        // Update error state with error message
        setError(err.message);
        
        // Turn off loading state
        setLoading(false);
      }
    }
    
    // Call the async function we just defined
    fetchIncidents();
    
    // Empty dependency array [] means:
    // "Run this effect only once when component mounts"
    // Like componentDidMount in class components
  }, []);
  
  
  // ========================================
  // CONDITIONAL RENDERING
  // ========================================
  
  // While loading, show loading message
  if (loading) {
    return (
      <div className="incidents-section">
        <h2>📋 Recent Incidents</h2>
        
        {/* Loading state - shown while fetching data */}
        <div style={{ 
          padding: '40px', 
          textAlign: 'center',
          backgroundColor: '#fff3cd',
          borderRadius: '8px',
          border: '1px solid #ffeaa7'
        }}>
          {/* Loading spinner emoji and text */}
          <p style={{ fontSize: '18px', color: '#856404' }}>
            ⏳ Loading incidents from database...
          </p>
        </div>
      </div>
    );
  }
  
  // If error occurred, show error message
  if (error) {
    return (
      <div className="incidents-section">
        <h2>📋 Recent Incidents</h2>
        
        {/* Error state - shown if API call fails */}
        <div style={{ 
          padding: '20px', 
          backgroundColor: '#f8d7da',
          color: '#721c24',
          borderRadius: '8px',
          border: '1px solid #f5c6cb'
        }}>
          {/* Error icon and message */}
          <p><strong>❌ Failed to Load Incidents</strong></p>
          <p>Error: {error}</p>
          
          {/* Help text for debugging */}
          <p style={{ fontSize: '14px', marginTop: '10px' }}>
            Make sure the backend is running on port 8000.
          </p>
          <p style={{ fontSize: '14px' }}>
            Try: <code>uvicorn app.main:app --reload</code>
          </p>
        </div>
      </div>
    );
  }
  
  // If no incidents in database, show empty state
  if (incidents.length === 0) {
    return (
      <div className="incidents-section">
        <h2>📋 Recent Incidents</h2>
        
        {/* Empty state - shown when database has no incidents */}
        <div style={{ 
          padding: '40px', 
          textAlign: 'center',
          backgroundColor: '#fff',
          borderRadius: '8px',
          border: '2px dashed #ddd'
        }}>
          {/* Empty mailbox icon and message */}
          <p style={{ fontSize: '18px', color: '#999' }}>
            📭 No Incidents Found
          </p>
          <p style={{ fontSize: '14px', color: '#666', marginTop: '10px' }}>
            The database is empty. Run the seed script to add sample data:
          </p>
          <code style={{ 
            display: 'block', 
            marginTop: '10px',
            padding: '10px',
            backgroundColor: '#f0f0f0',
            borderRadius: '4px'
          }}>
            python -m scripts.seed_incidents
          </code>
        </div>
      </div>
    );
  }
  
  // Success state - data loaded successfully
  // Show the table with incidents
  return (
    <div className="incidents-section">
      {/* Section header with count */}
      <h2>📋 Recent Incidents ({incidents.length})</h2>
      
      {/* Info text */}
      <p style={{ 
        marginBottom: '20px', 
        color: '#666',
        fontSize: '14px'
      }}>
        Click any row to view details. Data updates in real-time from backend API.
      </p>
      
      {/* Render the table component */}
      {/* Pass incidents array as prop */}
      <IncidentTable incidents={incidents} />
    </div>
  )
}

export default IncidentsList