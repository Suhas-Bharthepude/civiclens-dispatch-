// frontend/src/components/dashboard/IncidentsList.jsx
// Container component that fetches incidents and displays them in a table
// Handles: API calls, loading states, error states, retry logic
// Day 29: Enhanced with skeleton loading and retry button
// Day 30: Moved to organized components/dashboard/ folder

// Import React hooks
// useState - for managing component state (data, loading, error)
// useEffect - for side effects (fetching data from API)
import { useState, useEffect } from 'react'

// Import API function to fetch incidents from backend
// ../../ goes up two folders from components/dashboard/ to src/
// Then into api/ folder to find client.js
import { getIncidents } from '../../api/client'

// Import IncidentTable component to display the data in table format
// ./ means same folder (components/dashboard/)
import IncidentTable from './IncidentTable'

// Import LoadingState component for skeleton loading screens
// ../shared/ means go up one folder, then into shared/
import LoadingState from '../shared/LoadingState'


// ========================================
// INCIDENTS LIST COMPONENT
// ========================================

// Component that fetches and displays list of incidents
// This is a "smart" component (handles data fetching and state)
// Props:
//   - onIncidentClick: Callback function when user clicks an incident row
//   - refreshTrigger: Number that increments to trigger data re-fetch
function IncidentsList({ onIncidentClick, refreshTrigger }) {
  
  // ========================================
  // STATE MANAGEMENT
  // ========================================
  
  // State: array of incidents fetched from API
  // Starts as empty array []
  // Will be populated with incident objects after fetch completes
  const [incidents, setIncidents] = useState([])
  
  // State: loading indicator (true while fetching data)
  // Starts as true because we fetch immediately when component mounts
  // Set to false after fetch completes (success or error)
  const [loading, setLoading] = useState(true)
  
  // State: error message (null if no error occurred)
  // Stores error message string if API call fails
  // Used to display error message to user with retry button
  const [error, setError] = useState(null)
  
  
  // ========================================
  // FETCH DATA ON COMPONENT MOUNT OR REFRESH
  // ========================================
  
  // useEffect runs after component renders
  // We use it to fetch data from API (side effect)
  // Cannot fetch directly in component body (would cause infinite loop)
  useEffect(() => {
    // Define async function inside useEffect
    // useEffect callback itself cannot be async, so we define async function inside
    async function fetchIncidents() {
      try {
        // Log that we're starting the fetch (helpful for debugging)
        console.log('Fetching incidents from API...');
        
        // Set loading state to true
        // This shows skeleton screen to user while data loads
        setLoading(true);
        
        // Clear any previous errors
        // If user clicked retry after error, clear the old error message
        setError(null);
        
        // Call API to get all incidents
        // This makes GET request to http://localhost:8000/incidents
        // await pauses execution here until response comes back
        // Response is parsed to JSON and stored in data variable
        const data = await getIncidents();
        
        // Log received data for debugging
        // Shows array of incident objects in browser console
        console.log('Received incidents:', data);
        
        // Update state with received data
        // This triggers a re-render with the new incidents
        // Component will re-run and render the table with data
        setIncidents(data);
        
        // Turn off loading state (we're done fetching)
        // Component will re-render and show table instead of skeleton
        setLoading(false);
        
      } catch (err) {
        // If API call fails (network error, server down, etc.), catch the error
        // err is the error object thrown by fetch or getIncidents
        console.error('Failed to fetch incidents:', err);
        
        // Update error state with error message
        // err.message is the human-readable error description
        setError(err.message);
        
        // Turn off loading state (we're done trying to fetch)
        // Component will re-render and show error message instead of skeleton
        setLoading(false);
      }
    }
    
    // Call the async function we just defined
    // This actually executes the fetch
    fetchIncidents();
    
    // Dependency array: re-run this effect when these values change
    // [refreshTrigger, loading] means:
    // - Re-fetch when refreshTrigger changes (new incident submitted)
    // - Re-fetch when loading changes to true (user clicked retry button)
    // Empty array [] would mean run only once on mount
  }, [refreshTrigger, loading]);
  
  
  // ========================================
  // CONDITIONAL RENDERING - LOADING STATE
  // ========================================
  
  // While loading is true, show skeleton screen
  // This runs before data arrives from API
  if (loading) {
    return (
      // Container div for this section
      <div className="incidents-section">
        {/* Section header - shows even while loading */}
        <h2>📋 Recent Incidents</h2>
        
        {/* Skeleton loading state - shows placeholder boxes */}
        {/* type="skeleton" shows animated gray boxes */}
        {/* rows={5} shows 5 skeleton rows (simulates 5 incidents loading) */}
        {/* This feels faster than a spinner (shows layout structure) */}
        {/* Skeleton boxes have shimmer animation (defined in LoadingState.css) */}
        <LoadingState type="skeleton" rows={5} />
      </div>
    );
  }
  
  
  // ========================================
  // CONDITIONAL RENDERING - ERROR STATE
  // ========================================
  
  // If error occurred, show error message with retry button
  // This runs if API call failed
  if (error) {
    return (
      // Container div for this section
      <div className="incidents-section">
        {/* Section header */}
        <h2>📋 Recent Incidents</h2>
        
        {/* Error state box - shown if API call fails */}
        {/* Red background and border for visual alert */}
        <div style={{ 
          padding: '20px',                    // Space inside error box
          backgroundColor: '#f8d7da',         // Light red background
          color: '#721c24',                   // Dark red text
          borderRadius: '8px',                // Rounded corners
          border: '1px solid #f5c6cb'         // Red border
        }}>
          {/* Error icon and bold heading */}
          <p><strong>❌ Failed to Load Incidents</strong></p>
          
          {/* Display the actual error message */}
          {/* {error} embeds the error message from state */}
          <p>Error: {error}</p>
          
          {/* Help text for debugging */}
          {/* Tells user what might be wrong */}
          <p style={{ fontSize: '14px', marginTop: '10px' }}>
            Make sure the backend is running on port 8000.
          </p>
          
          {/* Show command to run backend */}
          {/* <code> tag styled differently via global CSS */}
          <p style={{ fontSize: '14px' }}>
            Try: <code>uvicorn app.main:app --reload</code>
          </p>
          
          {/* Retry button - lets user try loading again */}
          {/* onClick handler resets error and triggers re-fetch */}
          <button 
            onClick={() => {
              // Clear error state (remove error message)
              setError(null);
              
              // Set loading to true
              // This triggers useEffect to re-run (because loading is in dependency array)
              // useEffect will call fetchIncidents() again
              setLoading(true);
              
              // Log retry attempt for debugging
              console.log('Retrying to fetch incidents...');
            }}
            style={{
              marginTop: '15px',              // Space above button
              padding: '10px 20px',           // Space inside button
              backgroundColor: '#e74c3c',     // Red background matches error theme
              color: 'white',                 // White text
              border: 'none',                 // No border
              borderRadius: '4px',            // Rounded corners
              cursor: 'pointer',              // Pointer cursor on hover
              fontWeight: '600',              // Bold text
              fontSize: '0.95rem'             // Slightly smaller font
            }}
          >
            {/* Button text with retry icon */}
            🔄 Retry Loading
          </button>
        </div>
      </div>
    );
  }
  
  
  // ========================================
  // CONDITIONAL RENDERING - EMPTY STATE
  // ========================================
  
  // If no incidents in database, show empty state
  // This runs if fetch succeeded but returned empty array
  if (incidents.length === 0) {
    return (
      // Container div for this section
      <div className="incidents-section">
        {/* Section header */}
        <h2>📋 Recent Incidents</h2>
        
        {/* Empty state box - shown when database has no incidents */}
        {/* Dashed border indicates "empty" visually */}
        <div style={{ 
          padding: '40px',                    // Space inside
          textAlign: 'center',                // Center all text
          backgroundColor: '#fff',            // White background
          borderRadius: '8px',                // Rounded corners
          border: '2px dashed #ddd'           // Dashed gray border
        }}>
          {/* Empty mailbox icon and message */}
          <p style={{ fontSize: '18px', color: '#999' }}>
            📭 No Incidents Found
          </p>
          
          {/* Helper text explaining what to do */}
          <p style={{ fontSize: '14px', color: '#666', marginTop: '10px' }}>
            The database is empty. Run the seed script to add sample data:
          </p>
          
          {/* Show command to run seed script */}
          {/* Styled as code block for visual distinction */}
          <code style={{ 
            display: 'block',                 // Take full width
            marginTop: '10px',                // Space above
            padding: '10px',                  // Space inside
            backgroundColor: '#f0f0f0',       // Light gray background
            borderRadius: '4px'               // Rounded corners
          }}>
            python -m scripts.seed_incidents
          </code>
        </div>
      </div>
    );
  }
  
  
  // ========================================
  // SUCCESS STATE - RENDER TABLE
  // ========================================
  
  // If we reach here, data loaded successfully and has incidents
  // Show the table with incidents
  return (
    // Container div for this section
    <div className="incidents-section">
      {/* Section header with count */}
      {/* {incidents.length} shows number of incidents dynamically */}
      <h2>📋 Recent Incidents ({incidents.length})</h2>
      
      {/* Info text for user */}
      {/* Explains what clicking does and that data is live */}
      <p style={{ 
        marginBottom: '20px',               // Space below text
        color: '#666',                      // Gray text color
        fontSize: '14px'                    // Smaller font size
      }}>
        Click any row to view details. Data updates in real-time from backend API.
      </p>
      
      {/* Render the table component */}
      {/* Pass incidents array as prop (data to display) */}
      {/* Pass onIncidentClick as prop (callback when row clicked) */}
      {/* IncidentTable is a "dumb" component (just displays data, no fetching) */}
      <IncidentTable 
        incidents={incidents}
        onIncidentClick={onIncidentClick}
      />
    </div>
  )
}

// ========================================
// EXPORT
// ========================================

// Export component as default export
// Allows other files to import: import IncidentsList from './IncidentsList'
export default IncidentsList