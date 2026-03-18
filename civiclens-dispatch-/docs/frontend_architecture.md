# Frontend Architecture (Days 22-30)

## Component Tree
```
App.jsx (Root)
│
├─ HealthCheck.jsx
│  └─ Shows: API status
│
├─ DashboardLayout.jsx
│  │
│  ├─ Left Column (1/3 width)
│  │  │
│  │  └─ SubmitIncidentForm.jsx
│  │     ├─ Text inputs (source, description, location)
│  │     ├─ File inputs (audio, image)
│  │     └─ Calls: POST /incidents
│  │
│  └─ Right Column (2/3 width)
│     │
│     └─ IncidentsList.jsx
│        ├─ Calls: GET /incidents
│        ├─ State: incidents[], loading, error
│        │
│        └─ IncidentTable.jsx
│           ├─ Maps: incidents → table rows
│           └─ Events: onClick → parent
│
├─ IncidentDetail.jsx (Conditional)
│  ├─ Shows: when selectedIncident !== null
│  ├─ Displays: Full incident details
│  └─ Events: onClose → sets selectedIncident = null
│
└─ ToastContainer.jsx
   └─ Maps: toasts → Toast.jsx components
```

## Data Flow

### State Location
```
App.jsx
├─ selectedIncident (which incident detail to show)
├─ refreshTrigger (when to refetch incidents)
└─ toasts (array of notifications)

IncidentsList.jsx
├─ incidents (fetched from API)
├─ loading (fetch in progress)
└─ error (fetch failed)

SubmitIncidentForm.jsx
├─ formData (form field values)
├─ audioFile / imageFile (uploaded files)
├─ submitting (submit in progress)
├─ submitSuccess (submit succeeded)
└─ submitError (submit failed)
```

### Props Flow (Down)
```
App
  ↓ onIncidentClick, refreshTrigger
IncidentsList
  ↓ incidents, onIncidentClick
IncidentTable
  ↓ id, description, severity, etc.
Table Row
```

### Events Flow (Up)
```
Table Row (clicked)
  ↑ calls onIncidentClick(incident)
IncidentTable
  ↑ passes event up
IncidentsList
  ↑ passes event up
App (handles click, sets selectedIncident)
```

## Routing Strategy

**Current:** No routing (single-page app)

**Future options:**
- React Router (URL-based navigation)
- Keep as single-page (current approach)

**Decision:** Single-page is simpler for now, can add routing later if needed.

## State Management

**Current:** Component state + props

**Libraries available (not using yet):**
- Redux - Global state management
- Zustand - Lightweight state
- Context API - Built-in React

**Decision:** Component state is sufficient for current app size.

## API Communication

### Pattern
```
Component
  ↓ imports function from api/client.js
api/client.js
  ↓ makes fetch() request
Backend API (localhost:8000)
  ↓ returns JSON
api/client.js
  ↓ parses and returns
Component
  ↓ updates state
  ↓ re-renders
```

### Error Handling Flow
```
API call fails
  ↓ catch block
Set error state
  ↓ component re-renders
Show error UI
  ↓ user clicks retry
Clear error state
  ↓ try API call again
```

## File Organization
```
src/
├── App.jsx              # Root component
├── main.jsx             # React entry point
├── index.css            # Global styles
│
├── api/
│   └── client.js        # All API calls
│
├── components/
│   ├── dashboard/       # Dashboard views
│   ├── forms/           # Form components
│   ├── layout/          # Layout components
│   └── shared/          # Reusable components
│
├── hooks/
│   └── useToast.js      # Custom hooks
│
└── utils/               # Utility functions
```

## Key Design Decisions

### Why No Redux?
- App is small enough for component state
- Props drilling is minimal
- Adds complexity without benefit
- Can add later if needed

### Why No TypeScript?
- Learning focus: React first, types later
- JavaScript is simpler for beginners
- Can migrate to TypeScript later

### Why Vite over Create React App?
- Faster build times
- Modern tooling
- Smaller bundle sizes
- Better developer experience

### Why CSS files vs CSS-in-JS?
- Familiar to beginners
- Easy to modify
- Good performance
- Can switch to styled-components later

---

*Architecture documented: Day 30*