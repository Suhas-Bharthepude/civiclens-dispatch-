// frontend/src/api/client.js
// This file contains all API calls to the FastAPI backend
// Components import functions from here instead of calling fetch directly
//
// Benefits:
// 1. Centralized API logic (one place to update URLs)
// 2. Consistent error handling
// 3. Reusable across components
// 4. Easy to test

// ========================================
// CONFIGURATION
// ========================================

// Base URL for API
// In development: localhost:8000
// In production: would be your deployed API URL
const API_BASE_URL = 'http://localhost:8000';


// ========================================
// HELPER FUNCTION - Make API Request
// ========================================

// Generic function to make API requests
// This handles common logic like error checking
// Other functions will use this internally
async function apiRequest(endpoint, options = {}) {
    /*
    Makes an HTTP request to the API
    
    Args:
        endpoint: The API path (e.g., '/incidents')
        options: Fetch options (method, body, headers, etc.)
    
    Returns:
        Promise that resolves to response data (JSON)
    
    Throws:
        Error if request fails or returns non-2xx status code
    */
    
    // Build full URL by combining base URL and endpoint
    // Example: 'http://localhost:8000' + '/incidents'
    const url = `${API_BASE_URL}${endpoint}`;
    
    // Log request for debugging
    console.log(`[API] ${options.method || 'GET'} ${url}`);
    
    try {
        // Make the HTTP request
        // fetch() returns a Promise
        // await waits for the Promise to resolve
        const response = await fetch(url, options);
        
        // Check if request succeeded (status code 200-299)
        if (!response.ok) {
            // Request failed (404, 500, etc.)
            // Throw error with status code
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // Parse JSON from response body
        // response.json() also returns a Promise
        const data = await response.json();
        
        // Log success
        console.log(`[API] Success:`, data);
        
        // Return the parsed data
        return data;
        
    } catch (error) {
        // Log error for debugging
        console.error(`[API] Error:`, error);
        
        // Re-throw error so calling code can handle it
        throw error;
    }
}


// ========================================
// HEALTH CHECK
// ========================================

// Check if API is running
export async function checkHealth() {
    /*
    Calls GET /health endpoint
    
    Returns:
        Object like { status: "ok", service: "...", version: "..." }
    
    Example usage:
        const health = await checkHealth();
        console.log(health.status);  // "ok"
    */
    return apiRequest('/health');
}


// ========================================
// INCIDENT OPERATIONS
// ========================================

// Get all incidents (with optional filters)
export async function getIncidents(filters = {}) {
    /*
    Calls GET /incidents endpoint
    
    Args:
        filters: Optional object with query parameters
            Example: { severity: 'high', limit: 10 }
    
    Returns:
        Array of incident objects
    
    Example usage:
        const incidents = await getIncidents();
        const highSeverity = await getIncidents({ severity: 'high' });
    */
    
    // Build query string from filters object
    // Example: { severity: 'high', limit: 10 }
    // Becomes: '?severity=high&limit=10'
    const queryParams = new URLSearchParams(filters).toString();
    
    // Add query string to endpoint if it exists
    const endpoint = queryParams ? `/incidents?${queryParams}` : '/incidents';
    
    return apiRequest(endpoint);
}


// Get a single incident by ID
export async function getIncident(id) {
    /*
    Calls GET /incidents/{id} endpoint
    
    Args:
        id: Incident ID number
    
    Returns:
        Single incident object
    
    Example usage:
        const incident = await getIncident(5);
        console.log(incident.description);
    */
    return apiRequest(`/incidents/${id}`);
}


// Create a new incident
export async function createIncident(incidentData) {
    /*
    Calls POST /incidents endpoint
    
    Args:
        incidentData: Object with incident fields
            Example: {
                source: "citizen",
                description: "Fire on Main St",
                location: "123 Main St"
            }
    
    Returns:
        Created incident object (includes auto-generated ID)
    
    Example usage:
        const newIncident = await createIncident({
            source: "citizen",
            description: "Emergency",
            location: "123 St"
        });
        console.log(newIncident.id);  // Auto-generated ID
    */
    return apiRequest('/incidents', {
        method: 'POST',  // HTTP POST method
        headers: {
            'Content-Type': 'application/json',  // Tell server we're sending JSON
        },
        body: JSON.stringify(incidentData),  // Convert object to JSON string
    });
}


// Update an existing incident
export async function updateIncident(id, updateData) {
    /*
    Calls PATCH /incidents/{id} endpoint
    
    Args:
        id: Incident ID to update
        updateData: Object with fields to update
    
    Returns:
        Updated incident object
    
    Example usage:
        const updated = await updateIncident(5, { severity: 'high' });
    */
    return apiRequest(`/incidents/${id}`, {
        method: 'PATCH',  // HTTP PATCH method (partial update)
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData),
    });
}


// Delete an incident
export async function deleteIncident(id) {
    /*
    Calls DELETE /incidents/{id} endpoint
    
    Args:
        id: Incident ID to delete
    
    Returns:
        Success message object
    
    Example usage:
        await deleteIncident(5);
    */
    return apiRequest(`/incidents/${id}`, {
        method: 'DELETE',  // HTTP DELETE method
    });
}


// ========================================
// EXPORT ALL FUNCTIONS
// ========================================

// All functions are already exported individually above with 'export'
// This allows importing like:
// import { getIncidents, createIncident } from './api/client'