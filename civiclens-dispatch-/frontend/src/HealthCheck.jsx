// frontend/src/HealthCheck.jsx
// This component checks if the backend API is running
// Makes a real API call using fetch()

// Import hooks from React
import { useState, useEffect } from 'react'

// Import API client function
import { checkHealth } from './api/client'


// ========================================
// HEALTH CHECK COMPONENT
// ========================================

function HealthCheck() {
    
    // ========================================
    // STATE
    // ========================================
    
    // State: API status data
    // Starts as null (no data yet)
    const [healthData, setHealthData] = useState(null)
    
    // State: loading indicator
    // Starts as true (we're fetching data)
    const [loading, setLoading] = useState(true)
    
    // State: error message
    // Starts as null (no error yet)
    const [error, setError] = useState(null)
    
    
    // ========================================
    // FETCH HEALTH DATA ON MOUNT
    // ========================================
    
    // useEffect runs after component renders
    useEffect(() => {
        // Define async function inside useEffect
        // (can't make useEffect callback itself async)
        async function fetchHealth() {
            try {
                // Call the API
                // await pauses until the promise resolves
                const data = await checkHealth();
                
                // Update state with received data
                setHealthData(data);
                
                // Turn off loading
                setLoading(false);
                
            } catch (err) {
                // If fetch fails, update error state
                // err.message contains the error description
                setError(err.message);
                
                // Turn off loading
                setLoading(false);
            }
        }
        
        // Call the async function
        fetchHealth();
        
        // Empty dependency array = run once on mount
    }, []);
    
    
    // ========================================
    // RENDER DIFFERENT UI BASED ON STATE
    // ========================================
    
    // If still loading, show loading message
    if (loading) {
        return (
            <div style={{ padding: '20px', backgroundColor: '#fff3cd', borderRadius: '8px' }}>
                <p>⏳ Checking API connection...</p>
            </div>
        );
    }
    
    // If error occurred, show error message
    if (error) {
        return (
            <div style={{ 
                padding: '20px', 
                backgroundColor: '#f8d7da', 
                color: '#721c24',
                borderRadius: '8px',
                border: '1px solid #f5c6cb'
            }}>
                <p><strong>❌ API Connection Failed</strong></p>
                <p>Error: {error}</p>
                <p style={{ fontSize: '14px', marginTop: '10px' }}>
                    Make sure backend is running: <code>uvicorn app.main:app --reload</code>
                </p>
            </div>
        );
    }
    
    // If data loaded successfully, show success message
    return (
        <div style={{ 
            padding: '20px', 
            backgroundColor: '#d4edda',
            color: '#155724',
            borderRadius: '8px',
            border: '1px solid #c3e6cb'
        }}>
            <p><strong>✅ API Connected!</strong></p>
            <p>Service: {healthData.service}</p>
            <p>Version: {healthData.version}</p>
            <p>Status: {healthData.status}</p>
        </div>
    );
}

export default HealthCheck