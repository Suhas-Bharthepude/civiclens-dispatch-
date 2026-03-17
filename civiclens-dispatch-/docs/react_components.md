# React Components Guide (Day 25)

## Component Architecture
```
App.jsx (Root)
├── HealthCheck.jsx (API status)
└── IncidentsList.jsx (Data fetching)
    └── IncidentTable.jsx (Display)
        └── (maps over) IncidentRow
```

## Components Built

### App.jsx
**Purpose:** Root component, main container

**Responsibilities:**
- Renders header
- Contains all other components
- Will manage global state (filters, selected incident)

**Props:** None (root component)

**State:** None yet (will add filters later)

### HealthCheck.jsx
**Purpose:** Check if backend API is running

**Responsibilities:**
- Fetch /health endpoint
- Show green box if connected
- Show red error if not connected

**Props:** None

**State:**
- `healthData` - Response from API
- `loading` - Loading indicator
- `error` - Error message

### IncidentsList.jsx
**Purpose:** Fetch incidents and pass to table

**Responsibilities:**
- Call getIncidents() API
- Handle loading state
- Handle error state
- Handle empty state
- Pass data to IncidentTable

**Props:** None

**State:**
- `incidents` - Array of incidents from API
- `loading` - Loading indicator  
- `error` - Error message

### IncidentTable.jsx
**Purpose:** Display incidents in table format

**Responsibilities:**
- Render HTML table
- Map over incidents array
- Format data (risk scores, severity)
- Handle row clicks
- Apply styling and hover effects

**Props:**
- `incidents` - Array of incident objects

**State:** None (presentational component)

### LoadingSpinner.jsx
**Purpose:** Reusable loading animation

**Props:**
- `message` - Custom loading text (optional)

**State:** None

## Data Flow

### 1. Component Mount
```javascript
IncidentsList mounts
    ↓
useEffect runs
    ↓
Calls getIncidents()
```

### 2. Loading State
```javascript
loading = true
    ↓
Renders "Loading..." message
```

### 3. Data Arrives
```javascript
API returns data
    ↓
setIncidents(data)
    ↓
loading = false
    ↓
Component re-renders
```

### 4. Display Data
```javascript
IncidentsList receives incidents
    ↓
Passes to IncidentTable as props
    ↓
IncidentTable maps over array
    ↓
Creates table row for each incident
```

## Rendering Patterns

### Mapping Arrays
```javascript
{items.map(item => (
    <Component key={item.id} data={item} />
))}
```

**Key rules:**
- Always provide `key` prop
- Use unique ID (not array index)
- Extract logic to separate component

### Conditional Rendering
```javascript
// Three-state pattern
if (loading) return <Loading />;
if (error) return <Error />;
return <Data />;

// Inline with ternary
{loading ? <Loading /> : <Data />}

// Inline with logical AND
{error && <ErrorMessage />}
```

### Props Passing
```javascript
// Parent
<Child name="Alice" age={25} />

// Child receives
function Child({ name, age }) {
    return <p>{name} is {age}</p>;
}
```

## Styling Patterns

### Component CSS Files
Each component can have its own CSS:
```
IncidentTable.jsx
IncidentTable.css  ← Styles for this component
```

### CSS Modules (Alternative)
```
IncidentTable.module.css
```

### Inline Styles
```javascript
<div style={{ color: 'red', fontSize: '16px' }}>
    Inline styles
</div>
```

**Best practice:** Use CSS files for most styling, inline for dynamic styles.

## Common Patterns

### Loading State Pattern
```javascript
const [data, setData] = useState(null);
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);

useEffect(() => {
    async function fetch() {
        try {
            const result = await api();
            setData(result);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }
    fetch();
}, []);
```

### Table Rendering Pattern
```javascript
<table>
    <thead>
        <tr>
            <th>Column 1</th>
            <th>Column 2</th>
        </tr>
    </thead>
    <tbody>
        {data.map(item => (
            <tr key={item.id}>
                <td>{item.field1}</td>
                <td>{item.field2}</td>
            </tr>
        ))}
    </tbody>
</table>
```

---

*Last updated: Day 25*