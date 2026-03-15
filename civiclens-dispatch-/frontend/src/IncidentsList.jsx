// frontend/src/IncidentsList.jsx
// This component fetches incidents from the API and displays them
// Demonstrates: useEffect, API calls, loading states, error handling

// Import React hooks
import { useState, useEffect } from 'react'

// Import API function
import { getIncidents } from './api/client'

// Import IncidentCard component to display each incident
import IncidentCard from './IncidentCard'


// ========================================
// INCIDENTS LIST COMPONENT
// ========================================

function IncidentsList() {
    
    // ========================================
    // STATE
    // ========================================
    
    // State: array of incidents
    // Starts as empty array
    const [incidents, setIncidents] = useState([])
    
    // State: loading indicator
    // Starts as true (we'll fetch immediately)
    const [loading, setLoading] = useState(true)
    
    // State: error message
    // Starts as null (no error yet)
    const [error, setError] = useState(null)
    
    
    // ========================================
    // FETCH INCIDENTS ON MOUNT
    // ========================================
    
    useEffect(() => {
        // Define async function to fetch incidents
        async function fetchIncidents() {
            try {
                console.log('Fetching incidents from API...');
                
                // Call API to get all incidents
                // This makes GET request to http://localhost:8000/incidents
                const data = await getIncidents();
                
                // Log received data
                console.log('Received incidents:', data);
                
                // Update state with received incidents
                // This triggers a re-render with the new data
                setIncidents(data);
                
                // Turn off loading state
                setLoading(false);
                
            } catch (err) {
                // If API call fails, update error state
                console.error('Failed to fetch incidents:', err);
                setError(err.message);
                
                // Turn off loading state
                setLoading(false);
            }
        }
        
        // Call the fetch function
        fetchIncidents();
        
        // Empty dependency array = run once when component mounts
    }, []);
    
    
    // ========================================
    // CONDITIONAL RENDERING
    // ========================================
    
    // If still loading, show loading spinner
    if (loading) {
        return (
            <div className="incidents-list">
                <h2>📋 Recent Incidents</h2>
                <div style={{ 
                    padding: '40px', 
                    textAlign: 'center',
                    backgroundColor: '#f0f0f0',
                    borderRadius: '8px'
                }}>
                    <p style={{ fontSize: '18px', color: '#666' }}>
                        ⏳ Loading incidents...
                    </p>
                </div>
            </div>
        );
    }
    
    // If error occurred, show error message
    if (error) {
        return (
            <div className="incidents-list">
                <h2>📋 Recent Incidents</h2>
                <div style={{ 
                    padding: '20px', 
                    backgroundColor: '#f8d7da',
                    color: '#721c24',
                    borderRadius: '8px',
                    border: '1px solid #f5c6cb'
                }}>
                    <p><strong>❌ Failed to load incidents</strong></p>
                    <p>Error: {error}</p>
                    <p style={{ fontSize: '14px', marginTop: '10px' }}>
                        Make sure backend is running on port 8000
                    </p>
                </div>
            </div>
        );
    }
    
    // If no incidents in database, show empty state
    if (incidents.length === 0) {
        return (
            <div className="incidents-list">
                <h2>📋 Recent Incidents</h2>
                <div style={{ 
                    padding: '40px', 
                    textAlign: 'center',
                    backgroundColor: '#fff',
                    borderRadius: '8px',
                    border: '2px dashed #ddd'
                }}>
                    <p style={{ fontSize: '18px', color: '#999' }}>
                        📭 No incidents found
                    </p>
                    <p style={{ fontSize: '14px', color: '#666', marginTop: '10px' }}>
                        Submit a new incident or run the seed script to add sample data.
                    </p>
                </div>
            </div>
        );
    }
    
    // If data loaded successfully, display incidents
    return (
        <div className="incidents-list">
            {/* Header with count */}
            <h2>📋 Recent Incidents ({incidents.length})</h2>
            
            {/* Info message */}
            <p style={{ 
                marginBottom: '20px', 
                color: '#666',
                fontSize: '14px'
            }}>
                Showing {incidents.length} incidents from database. 
                Data fetched from backend API.
            </p>
            
            {/* Map over incidents array and create IncidentCard for each */}
            {/* .map() is like a for loop that returns new array */}
            {/* Each incident gets passed to IncidentCard as props */}
            {incidents.map((incident) => (
                // IncidentCard component (we already built this!)
                // Pass incident data as props
                // key prop is required when mapping - helps React track which items changed
                // Use incident.id as key (must be unique)
                <IncidentCard 
                    key={incident.id}
                    id={incident.id}
                    source={incident.source}
                    description={incident.description}
                    location={incident.location}
                    severity={incident.severity || 'medium'}  // Default to medium if null
                />
            ))}
        </div>
    )
}

export default IncidentsList