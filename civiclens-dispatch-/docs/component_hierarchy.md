# Component Hierarchy (Day 26)

## Visual Component Tree
```
App.jsx (selectedIncident state)
│
├─ Header (static)
│
├─ Main
│  │
│  ├─ HealthCheck.jsx
│  │  ├─ State: healthData, loading, error
│  │  └─ Makes: GET /health
│  │
│  └─ IncidentsList.jsx
│     ├─ State: incidents, loading, error
│     ├─ Makes: GET /incidents
│     └─ Renders: IncidentTable
│        │
│        ├─ Props: incidents[], onIncidentClick
│        └─ Maps: incidents → table rows
│
├─ Footer (static)
│
└─ IncidentDetail.jsx (conditional)
   ├─ Props: incident, onClose
   ├─ Shows: when selectedIncident !== null
   └─ Renders: full incident details
```

## Data Flow

### Opening Detail Panel
```
1. User clicks row in IncidentTable
   ↓
2. IncidentTable calls onIncidentClick(incident)
   ↓
3. Function goes up to IncidentsList (passes through)
   ↓
4. Function reaches App.jsx
   ↓
5. App calls handleIncidentClick(incident)
   ↓
6. setSelectedIncident(incident) updates state
   ↓
7. App re-renders
   ↓
8. selectedIncident is truthy
   ↓
9. IncidentDetail renders with incident data
   ↓
10. Panel slides in! ✨
```

### Closing Detail Panel
```
User clicks:
  - X button
  - Overlay
  - ESC key
   ↓
onClose() called
   ↓
App.handleCloseDetail()
   ↓
setSelectedIncident(null)
   ↓
App re-renders
   ↓
selectedIncident is null
   ↓
IncidentDetail doesn't render
   ↓
Panel disappears! ✨
```

## State Management

### Local State (Component-specific)

**HealthCheck:**
- `healthData` - API response
- `loading` - Fetch in progress
- `error` - Error message

**IncidentsList:**
- `incidents` - Array of incidents
- `loading` - Fetch in progress
- `error` - Error message

### Lifted State (Shared between components)

**App (parent):**
- `selectedIncident` - Which incident to show in detail

**Why lifted:**
- Both IncidentTable and IncidentDetail need it
- IncidentTable needs to SET it (when row clicked)
- IncidentDetail needs to READ it (to display)
- Solution: Put state in common parent (App)

## Props Flow

### Down the Tree (Data)
```
App
  ↓ incidents, onIncidentClick
IncidentsList
  ↓ incidents, onIncidentClick
IncidentTable
  ↓ individual incident
Table Row
```

### Up the Tree (Events)
```
Table Row (clicked)
  ↑ calls onIncidentClick(incident)
IncidentTable
  ↑ passes event up
IncidentsList
  ↑ passes event up
App (handles event, updates state)
```

## Conditional Rendering Patterns

### Pattern 1: Logical AND
```javascript
{condition && <Component />}
```
Renders Component only if condition is true.

### Pattern 2: Ternary
```javascript
{condition ? <ComponentA /> : <ComponentB />}
```
Renders ComponentA if true, ComponentB if false.

### Pattern 3: Early Return
```javascript
if (loading) return <Loading />;
if (error) return <Error />;
return <Data />;
```
Returns different JSX based on state.

## Event Handling

### Click Events
```javascript
// In parent
function handleClick(data) {
    console.log(data);
}

// Pass to child
<Child onClick={handleClick} />

// Child calls it
<div onClick={() => props.onClick(someData)}>
```

### Keyboard Events
```javascript
useEffect(() => {
    function handleKey(event) {
        if (event.key === 'Escape') {
            closePanel();
        }
    }
    
    document.addEventListener('keydown', handleKey);
    
    return () => {
        document.removeEventListener('keydown', handleKey);
    };
}, []);
```

## CSS Animations

### Fade In
```css
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.element {
    animation: fadeIn 0.3s ease;
}
```

### Slide In
```css
@keyframes slideIn {
    from { transform: translateX(100%); }
    to { transform: translateX(0); }
}
```

---

*Component architecture complete!* 🏗️