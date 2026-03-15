# API Integration Guide (Day 24)

## Overview

The React frontend (port 5174) communicates with the FastAPI backend (port 8000) using HTTP requests.

## Architecture
```
React Component
    ↓ calls
API Client (src/api/client.js)
    ↓ makes HTTP request
FastAPI Backend (localhost:8000)
    ↓ queries
SQLite Database
    ↓ returns data
FastAPI Backend
    ↓ sends JSON response
API Client
    ↓ returns data
React Component
    ↓ updates state
UI Re-renders
```

## The Flow

### 1. Component Mounts
```javascript
function IncidentsList() {
    useEffect(() => {
        fetchData();  // Runs when component first appears
    }, []);
}
```

### 2. API Call Made
```javascript
const data = await getIncidents();  // HTTP GET request
```

### 3. Backend Processes
```python
@app.get("/incidents")
async def list_incidents(db: Database = Depends(get_db)):
    query = incidents.select()
    return await db.fetch_all(query)
```

### 4. Data Returns
```javascript
// Receives array of incidents
[
    { id: 1, description: "Fire", ... },
    { id: 2, description: "Accident", ... }
]
```

### 5. State Updates
```javascript
setIncidents(data);  // Triggers re-render
```

### 6. UI Updates
```javascript
incidents.map(incident => <IncidentCard {...incident} />)
```

## API Client Functions

### Health Check
```javascript
import { checkHealth } from './api/client';

const health = await checkHealth();
// Returns: { status: "ok", service: "...", version: "..." }
```

### Get All Incidents
```javascript
import { getIncidents } from './api/client';

const incidents = await getIncidents();
// Returns: [{id: 1, ...}, {id: 2, ...}, ...]
```

### Get Single Incident
```javascript
import { getIncident } from './api/client';

const incident = await getIncident(5);
// Returns: {id: 5, description: "...", ...}
```

### Create Incident
```javascript
import { createIncident } from './api/client';

const newIncident = await createIncident({
    source: "citizen",
    description: "Fire on Main St",
    location: "123 Main St"
});
// Returns: {id: 11, source: "citizen", ...}
```

## Error Handling Pattern

### Three-State Pattern

Always track three states when fetching data:
```javascript
const [data, setData] = useState(null);      // The data
const [loading, setLoading] = useState(true); // Loading indicator
const [error, setError] = useState(null);    // Error message

useEffect(() => {
    async function fetchData() {
        try {
            const result = await apiCall();
            setData(result);
            setLoading(false);
        } catch (err) {
            setError(err.message);
            setLoading(false);
        }
    }
    fetchData();
}, []);

// Render based on state
if (loading) return <Loading />;
if (error) return <Error message={error} />;
return <DisplayData data={data} />;
```

## CORS Configuration

Backend must allow frontend to make requests.

**In backend/app/main.py:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (dev only!)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Production:** Replace `["*"]` with specific origin like `["https://yourapp.com"]`

## Debugging API Calls

### Browser Network Tab

1. Open DevTools (Cmd+Option+I)
2. Go to Network tab
3. Reload page
4. See all HTTP requests
5. Click on request to see:
   - Request headers
   - Request body
   - Response data
   - Status code

### Console Logging

API client logs every request:
```
[API] GET http://localhost:8000/incidents
[API] Success: [...data...]
```

### Common Errors

**"Failed to fetch"**
- Backend not running
- Wrong URL
- CORS issue

**"404 Not Found"**
- Wrong endpoint path
- Check backend routes

**"500 Internal Server Error"**
- Backend code error
- Check backend console logs

## Best Practices

✅ **Centralize API calls** - Use api/client.js, not fetch in components  
✅ **Handle all three states** - loading, error, success  
✅ **Log requests** - Helps debugging  
✅ **Use async/await** - Cleaner than .then() chains  
✅ **Validate data** - Check response before using  

❌ **Don't hardcode URLs** - Use constants  
❌ **Don't ignore errors** - Always catch and display  
❌ **Don't mutate state directly** - Use setter functions  

---

*Last updated: Day 24*