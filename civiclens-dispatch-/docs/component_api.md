# Component API Reference

## Dashboard Components

### HealthCheck

**Purpose:** Displays API connection status

**Props:** None

**State:**
- `healthData` - Response from /health endpoint
- `loading` - Loading indicator
- `error` - Error message

**Usage:**
```javascript
<HealthCheck />
```

**Displays:**
- ✅ Green box if API connected
- ❌ Red box if API down

---

### IncidentsList

**Purpose:** Fetches and displays list of incidents

**Props:**
- `onIncidentClick` (function, required): Callback when incident clicked
- `refreshTrigger` (number, required): Increments to trigger refetch

**State:**
- `incidents` - Array of incidents from API
- `loading` - Loading indicator
- `error` - Error message

**Usage:**
```javascript
<IncidentsList 
    onIncidentClick={(incident) => console.log(incident)}
    refreshTrigger={0}
/>
```

**Behavior:**
- Fetches on mount
- Refetches when refreshTrigger changes
- Shows skeleton while loading
- Shows error with retry button if fails
- Passes data to IncidentTable

---

### IncidentTable

**Purpose:** Displays incidents in table format

**Props:**
- `incidents` (array, required): Array of incident objects
- `onIncidentClick` (function, required): Callback when row clicked

**State:** None (presentational component)

**Usage:**
```javascript
<IncidentTable 
    incidents={[
        { id: 1, description: 'Fire', ... },
        { id: 2, description: 'Accident', ... }
    ]}
    onIncidentClick={(incident) => handleClick(incident)}
/>
```

**Features:**
- Sortable columns
- Color-coded severity badges
- Hover effects
- Clickable rows
- Responsive (hides columns on mobile)

---

### IncidentDetail

**Purpose:** Side panel showing full incident details

**Props:**
- `incident` (object, required): Incident object to display
- `onClose` (function, required): Callback when panel closes

**State:** None

**Usage:**
```javascript
{selectedIncident && (
    <IncidentDetail 
        incident={selectedIncident}
        onClose={() => setSelectedIncident(null)}
    />
)}
```

**Features:**
- Slides in from right
- Dark overlay
- Multiple close methods (X, overlay, ESC)
- Shows all incident fields
- Displays AI-generated data

---

## Form Components

### SubmitIncidentForm

**Purpose:** Form for submitting new incidents

**Props:**
- `onIncidentSubmitted` (function, optional): Callback after successful submission

**State:**
- `formData` - Object with form field values
- `audioFile` - Selected audio file
- `imageFile` - Selected image file
- `submitting` - Submission in progress
- `submitSuccess` - Submission succeeded
- `submitError` - Error message

**Usage:**
```javascript
<SubmitIncidentForm 
    onIncidentSubmitted={() => refreshList()}
/>
```

**Features:**
- Controlled inputs
- Client-side validation
- File upload interface
- Success/error messages
- Auto-reset after success
- Retry on error

**Validation Rules:**
- Source: Required
- Description: Required, min 10 characters
- Location: Required

---

## Layout Components

### DashboardLayout

**Purpose:** Two-column flexbox layout

**Props:**
- `leftColumn` (JSX, required): Content for left column
- `rightColumn` (JSX, required): Content for right column
- `leftWidth` (number, optional): Flex ratio for left (default: 1)
- `rightWidth` (number, optional): Flex ratio for right (default: 2)

**State:** None

**Usage:**
```javascript
<DashboardLayout
    leftWidth={1}
    rightWidth={2}
    leftColumn={<FormComponent />}
    rightColumn={<TableComponent />}
/>
```

**Features:**
- Flexible column ratios
- Responsive (stacks on mobile)
- Sticky left column option

---

### SectionDivider

**Purpose:** Visual separator between sections

**Props:**
- `title` (string, optional): Text to display on divider

**Usage:**
```javascript
// With title
<SectionDivider title="AI Analysis" />

// Without title (simple line)
<SectionDivider />
```

---

## Shared Components

### LoadingState

**Purpose:** Loading indicators

**Props:**
- `type` (string, optional): 'spinner', 'skeleton', or 'inline' (default: 'spinner')
- `message` (string, optional): Loading message (default: 'Loading...')
- `rows` (number, optional): Number of skeleton rows (default: 3)

**Usage:**
```javascript
// Spinner
<LoadingState type="spinner" message="Loading incidents..." />

// Skeleton
<LoadingState type="skeleton" rows={5} />

// Inline (for buttons)
<LoadingState type="inline" message="Submitting..." />
```

---

### Toast

**Purpose:** Single toast notification

**Props:**
- `message` (string, required): Text to display
- `type` (string, optional): 'success', 'error', 'warning', 'info' (default: 'info')
- `duration` (number, optional): Auto-dismiss time in ms (default: 5000)
- `onClose` (function, optional): Callback when closed

**Usage:**
```javascript
<Toast 
    message="Incident created!"
    type="success"
    duration={5000}
    onClose={() => console.log('closed')}
/>
```

---

### ToastContainer

**Purpose:** Manages and displays multiple toasts

**Props:**
- `toasts` (array, required): Array of toast objects
- `removeToast` (function, required): Function to remove toast by id

**Usage:**
```javascript
// Typically used with useToast hook
const { toasts, removeToast } = useToast();

<ToastContainer 
    toasts={toasts}
    removeToast={removeToast}
/>
```

---

### IncidentCard

**Purpose:** Card-style incident display (alternative to table row)

**Props:**
- `id` (number, required): Incident ID
- `source` (string, required): Report source
- `description` (string, required): Incident description
- `location` (string, required): Incident location
- `severity` (string, required): Severity level

**Usage:**
```javascript
<IncidentCard 
    id={1}
    source="citizen"
    description="Fire on Main St"
    location="123 Main St"
    severity="high"
/>
```

---

## Custom Hooks

### useToast

**Purpose:** Manage toast notifications

**Returns:**
- `toasts` (array): Current toasts
- `showToast` (function): Display new toast
- `removeToast` (function): Remove toast by ID

**Usage:**
```javascript
import useToast from './hooks/useToast';

function MyComponent() {
    const { showToast } = useToast();
    
    function handleSuccess() {
        showToast('Operation successful!', 'success');
    }
    
    function handleError() {
        showToast('Operation failed', 'error');
    }
}
```

**showToast signature:**
```javascript
showToast(message, type, duration)
// message: string
// type: 'success' | 'error' | 'warning' | 'info'
// duration: number (milliseconds)
```

---

## 🎨 Styling

### CSS Variables

Defined in `index.css`:
```css
--primary-color: #3498db
--secondary-color: #2c3e50
--success-color: #27ae60
--warning-color: #f39c12
--danger-color: #e74c3c
--spacing-md: 16px
--shadow-md: 0 2px 8px rgba(0,0,0,0.1)
```

### Using Variables
```css
.my-component {
    color: var(--primary-color);
    margin: var(--spacing-md);
    box-shadow: var(--shadow-md);
}
```

## 🔌 API Integration

All API calls go through `src/api/client.js`.

### Available Functions
```javascript
// Health check
checkHealth()

// Incidents
getIncidents(filters)
getIncident(id)
createIncident(data)
updateIncident(id, data)
deleteIncident(id)
```

### Adding New API Calls

1. Add function to `api/client.js`
2. Use `apiRequest` helper
3. Export function
4. Import where needed

---

*Frontend documentation complete*