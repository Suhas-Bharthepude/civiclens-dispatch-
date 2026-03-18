// frontend/src/components/HealthCheck.jsx
// Component that checks if the backend API is running and responding
// Makes a health check API call and displays connection status

// Import React hooks
// useState - for managing component state
// useEffect - for making API call after component renders
import { useState, useEffect } from 'react'

// Import API function to check backend health
// checkHealth() makes GET request to http://localhost:8000/health

import { checkHealth } from '../../api/client'


// ========================================
// HEALTH CHECK COMPONENT
// ========================================

// Component that displays API connection status
// No props needed - self-contained
function HealthCheck() {
  
  // ========================================
  // STATE
  // ========================================
  
  // State: health data from API response
  // Will contain: { status: "ok", service: "...", version: "..." }
  // Starts as null (no data yet)
  const [healthData, setHealthData] = useState(null)
  
  // State: loading indicator
  // Starts as true (we fetch immediately)
  const [loading, setLoading] = useState(true)
  
  // State: error message
  // Starts as null (no error yet)
  const [error, setError] = useState(null)
  
  
  // ========================================
  // FETCH HEALTH DATA ON MOUNT
  // ========================================
  
  // useEffect runs after component renders
  useEffect(() => {
    // Define async function to fetch health status
    async function fetchHealth() {
      try {
        // Call API health check endpoint
        // await pauses until response comes back
        const data = await checkHealth();
        
        // Update state with response data
        setHealthData(data);
        
        // Turn off loading
        setLoading(false);
        
      } catch (err) {
        // If API call fails, update error state
        setError(err.message);
        
        // Turn off loading
        setLoading(false);
      }
    }
    
    // Execute the async function
    fetchHealth();
    
    // Empty dependency array = run once on mount
  }, []);
  
  
  // ========================================
  // CONDITIONAL RENDERING - LOADING
  // ========================================
  
  // While loading, show yellow waiting message
  if (loading) {
    return (
      <div style={{ 
        padding: '20px',                    // Space inside
        backgroundColor: '#fff3cd',         // Light yellow background
        borderRadius: '8px',                // Rounded corners
        marginBottom: '20px'                // Space below
      }}>
        <p>⏳ Checking API connection...</p>
      </div>
    );
  }
  
  
  // ========================================
  // CONDITIONAL RENDERING - ERROR
  // ========================================
  
  // If error occurred, show red error box
  if (error) {
    return (
      <div style={{ 
        padding: '20px',                    // Space inside
        backgroundColor: '#f8d7da',         // Light red background
        color: '#721c24',                   // Dark red text
        borderRadius: '8px',                // Rounded corners
        border: '1px solid #f5c6cb',        // Red border
        marginBottom: '20px'                // Space below
      }}>
        {/* Error heading */}
        <p><strong>❌ API Connection Failed</strong></p>
        
        {/* Error message */}
        <p>Error: {error}</p>
        
        {/* Help text */}
        <p style={{ fontSize: '14px', marginTop: '10px' }}>
          Make sure backend is running: <code>uvicorn app.main:app --reload</code>
        </p>
      </div>
    );
  }
  
  
  // ========================================
  // SUCCESS STATE
  // ========================================
  
  // If data loaded successfully, show green success box
  return (
    <div style={{ 
      padding: '20px',                      // Space inside
      backgroundColor: '#d4edda',           // Light green background
      color: '#155724',                     // Dark green text
      borderRadius: '8px',                  // Rounded corners
      border: '1px solid #c3e6cb',          // Green border
      marginBottom: '20px'                  // Space below
    }}>
      {/* Success heading */}
      <p><strong>✅ API Connected!</strong></p>
      
      {/* Display service name from API response */}
      <p>Service: {healthData.service}</p>
      
      {/* Display version from API response */}
      <p>Version: {healthData.version}</p>
      
      {/* Display status from API response */}
      <p>Status: {healthData.status}</p>
    </div>
  );
}

// Export component as default export
// Allows importing: import HealthCheck from './components/HealthCheck'
export default HealthCheck