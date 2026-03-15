# CivicLens Dispatch - Learning Notes (Days 1-18)

## Day 1-3: Project Setup
- **Git basics**: Learned version control with commit, push, branching
- **Virtual environments**: Isolated Python dependencies with venv
- **Project structure**: Organized folders for backend, frontend, docs

## Day 4-5: HTTP and REST
- **HTTP requests**: GET, POST, PUT, DELETE methods
- **REST concepts**: Endpoints, routes, status codes, JSON bodies
- **requests library**: Making HTTP calls from Python

## Day 6-7: FastAPI Basics
- **FastAPI app**: Created basic app with uvicorn server
- **Routes**: Defined endpoints with path and query parameters
- **Path parameters**: `/echo/{name}` - extract values from URL
- **Query parameters**: `?severity=high` - filter results

## Day 8: Pydantic Models
- **Data validation**: Automatic validation with Pydantic
- **Type hints**: Enforce data types for request/response
- **Schema separation**: IncidentCreate vs IncidentRead models

## Day 9-10: SQL and PostgreSQL
- **Relational databases**: Tables, rows, columns, relationships
- **SQL basics**: CREATE, INSERT, SELECT, UPDATE, DELETE
- **Primary keys**: Unique identifiers for each row
- **Foreign keys**: Link tables together

## Day 11-12: SQLAlchemy ORM
- **ORM concept**: Object-Relational Mapping - work with DB using Python classes
- **Engine**: Connection to database
- **Metadata**: Registry of table definitions
- **Table definitions**: Define schema with Column objects

## Day 13: Reading Data
- **SELECT queries**: Fetch data from database
- **Filtering**: WHERE clauses to narrow results
- **Pagination**: LIMIT and OFFSET for large datasets
- **Sorting**: ORDER BY for organizing results

## Day 14: Code Organization
- **Routers**: Organize endpoints by feature
- **Modular structure**: Separate concerns (routes, schemas, db, services)
- **Seed scripts**: Populate database with test data

## Day 15-16: Async Processing
- **Background tasks**: Don't block HTTP responses with slow work
- **FastAPI BackgroundTasks**: Built-in way to schedule work after response
- **Use cases**: AI processing, email sending, file processing

## Day 17: File Uploads
- **UploadFile**: FastAPI's file upload handler
- **Multipart forms**: How files are sent over HTTP
- **File storage**: Saving uploaded files to disk with unique names

## Day 18: Storage Strategy
- **Local storage**: Start with disk-based file storage
- **S3-compatible**: Plan for scalable cloud storage later
- **File paths**: Store relative paths in database, actual files on disk

## Day 19: Configuration
- **Environment variables**: Keep secrets out of code
- **.env file**: Store config locally (never commit!)
- **Config module**: Central place for all settings
- **python-dotenv**: Load .env automatically

---

## Key Takeaways So Far

✅ **FastAPI** is async-first and perfect for AI workloads
✅ **Pydantic** makes data validation automatic and type-safe
✅ **SQLAlchemy** + **databases** library = async database access
✅ **Background tasks** keep API responsive while doing heavy work
✅ **Config management** keeps secrets safe and code clean


## Next Steps (Days 19-30)

- Add real AI models (ASR, classification, summarization)
- Build React frontend
- Implement mapping/geocoding
- Add authentication
- Write comprehensive tests

---

*These notes capture my learning journey building CivicLens Dispatch*





civiclens-dispatch/
│
├── .venv/                                    # Virtual environment (do not commit)
│
├── backend/
│   ├── __init__.py
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                          # FastAPI app entry point
│   │   ├── config.py                        # Environment configuration
│   │   │
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── database.py                  # Database connection setup
│   │   │   ├── dependencies.py              # get_db() dependency
│   │   │   └── models.py                    # SQLAlchemy table definitions
│   │   │
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── incidents.py                 # All incident endpoints
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── incident.py                  # Pydantic models
│   │   │
│   │   ├── services/
│   │   │   └── incident_processor.py        # AI pipeline (stub)
│   │   │
│   │   ├── tasks/
│   │   │   └── incident_tasks.py            # Background task helpers
│   │   │
│   │   ├── utils/
│   │   │   └── file_utils.py                # File upload utilities
│   │   │
│   │   ├── media/
│   │   │   └── tmp/
│   │   │       ├── audio/
│   │   │       │   └── .gitkeep             # Keep folder in git
│   │   │       ├── images/
│   │   │       │   └── .gitkeep             # Keep folder in git
│   │   │       └── documents/
│   │   │           └── .gitkeep             # Keep folder in git
│   │   │
│   │   └── uploads/
│   │       └── .gitkeep                     # Alternative upload location
│   │
│   ├── playground/
│   │   ├── http_playground.py               # HTTP/JSON experiments
│   │   └── test_api.py                      # Manual API testing script
│   │
│   ├── scripts/
│   │   └── seed_incidents.py                # Database seeding script
│   │
│   ├── sql/
│   │   └── experiments.sql                  # SQL learning exercises
│   │
│   ├── tests/
│   │   └── test_incidents.py                # API tests (Day 20)
│   │
│   ├── .env                                 # Environment variables (DO NOT COMMIT)
│   ├── requirements.txt                     # Python dependencies
│   ├── test.db                              # SQLite database (dev only)
│   └── venv/                                # Alternative venv location (if used)
│
├── frontend/                                # React app (Days 22-30)
│   └── (empty for now)
│
├── infra/                                   # Docker/deployment (Day 68)
│   └── (empty for now)
│
├── docs/
│   ├── architecture.md                      # **NEW** - System architecture
│   ├── concepts.md                          # REST API concepts
│   ├── database.md                          # **NEW** - Database concepts
│   ├── pipeline.md                          # (Day 40 - future)
│   ├── performance.md                       # (Day 58 - future)
│   ├── demo_script.md                       # (Day 61 - future)
│   ├── resume_bullets.md                    # (Day 64 - future)
│   └── slides/                              # (Day 63 - future)
│
├── notes/
│   └── learning-notes.md                    # Daily learning log
│
├── .gitignore                               # Git ignore rules
├── LICENSE                                  # Project license
├── README.md                                # Project overview
└── roadmap.md                               # 75-day roadmap





## Day 19: Environment Variables & Configuration

- **Environment variables**: Store configuration separately from code
- **.env file**: Local file with KEY=VALUE pairs (never commit!)
- **os.getenv()**: Read environment variables in Python
- **python-dotenv**: Automatically load .env file on startup
- **Configuration class**: Central place for all settings
- **Default values**: Fallback if environment variable not set
- **.env.example**: Template showing what variables are needed
- **SQLite**: File-based database, perfect for development (no server needed)

### Key Takeaways

✅ Secrets belong in .env, not in code  
✅ Each environment (dev/staging/prod) has its own .env  
✅ Always provide sensible defaults for optional settings  
✅ SQLite for dev, PostgreSQL for production  

---

*Day 19 complete!*



## Day 20: Testing with pytest

- **Testing**: Writing code to verify your code works correctly
- **pytest**: Python testing framework
- **Unit tests**: Test small pieces in isolation
- **Integration tests**: Test multiple pieces together
- **API tests**: Test HTTP endpoints
- **Fixtures**: Setup/teardown code that runs before/after tests
- **Assertions**: Checks that verify expected results
- **AAA pattern**: Arrange, Act, Assert
- **Test coverage**: Percentage of code covered by tests

### Key Concepts

**TestClient**: Simulates HTTP requests without starting server  
**Fixtures**: Reusable setup code for tests  
**@pytest.fixture**: Decorator that marks a function as a fixture  
**assert**: Python keyword that checks if something is True  
**pytest.raises()**: Tests that code raises expected errors  

### Test Structure
```python
def test_something():
    # ARRANGE - set up
    data = prepare_data()
    
    # ACT - do the thing
    result = function_to_test(data)
    
    # ASSERT - verify
    assert result == expected
```

### Commands Learned
```bash
pytest                    # Run all tests
pytest -v                 # Verbose output
pytest tests/file.py      # Run specific file
pytest --cov=app          # Show coverage
```

---

*Day 20 complete! Testing fundamentals mastered.* ✅


## Day 21: Buffer/Cleanup & Mini Review

**Purpose:** Consolidate knowledge, clean code, prepare for frontend

### What "Buffer Day" Means
- Review what we've built (20 days of code!)
- Clean up messy code
- Update documentation
- Reflect on lessons learned
- Prepare mentally and technically for new phase

### Activities Completed
1. ✅ Created project status document
2. ✅ Cleaned up code (marked deprecated files)
3. ✅ Updated architecture documentation
4. ✅ Rewrote README for GitHub presentation
5. ✅ Created lessons learned document
6. ✅ Reviewed all docs for accuracy

### Key Realizations

**Technical:**
- Backend is solid and ready for frontend
- Test suite gives confidence to make changes
- Configuration system is flexible and secure
- Code organization makes sense

**Personal:**
- I've learned A LOT in 21 days
- Having good docs makes everything easier
- Tests catch bugs early
- Clean code is easier to work with

### What's Ready for Frontend
- ✅ All API endpoints working
- ✅ CORS configured for frontend requests
- ✅ File uploads ready for form data
- ✅ Error handling returns proper status codes
- ✅ Response models are consistent

### Mental Preparation for React
- HTML/CSS/JavaScript basics (Day 22)
- React components and props (Day 23)
- API calls from frontend (Day 24)
- Form handling (Day 27)
- Building a real UI!

### Confidence Check
- **Backend understanding**: 8/10 ✅
- **Testing practices**: 7/10 ✅  
- **Documentation habits**: 9/10 ✅
- **Ready for frontend**: 6/10 (will improve!)

---

*Day 21 complete! Ready for frontend development!* 🎉


## Day 22: Web Basics - HTML/CSS/JavaScript

**Big shift:** Moving from backend (Python) to frontend (web technologies)

### HTML (Structure)
- **Tags**: Building blocks like `<div>`, `<p>`, `<button>`
- **Attributes**: Extra info like `id`, `class`, `required`
- **Document structure**: `<!DOCTYPE>`, `<html>`, `<head>`, `<body>`
- **Forms**: Collect user input with `<form>`, `<input>`, `<textarea>`
- **Tables**: Display data with `<table>`, `<tr>`, `<td>`

### CSS (Style)
- **Selectors**: Target elements (tag, .class, #id)
- **Properties**: Define appearance (color, font-size, padding)
- **Box model**: margin → border → padding → content
- **Layout**: Positioning and spacing elements
- **Colors**: Hex codes (#3498db), RGB, named colors

### JavaScript (Behavior)
- **Variables**: `let`, `const` for storing data
- **Functions**: Reusable blocks of code
- **DOM manipulation**: `document.getElementById()`, `.addEventListener()`
- **Events**: Respond to clicks, form submissions, etc.
- **FormData**: Extract form field values
- **Template literals**: `${variable}` for dynamic strings

### The DOM (Document Object Model)
- JavaScript's representation of HTML
- Tree structure of elements
- Can be modified in real-time
- Changes instantly update the page

### What I Built
- ✅ Complete prototype dispatcher dashboard
- ✅ Working incident submission form
- ✅ Interactive incident table
- ✅ Dynamic row addition
- ✅ Click handlers and alerts
- ✅ Success message display

### Key Realizations
- **HTML is simple but verbose** - Lots of tags!
- **CSS is powerful** - A few lines transform appearance
- **JavaScript makes pages come alive** - No page reload needed!
- **Browser DevTools are essential** - Console shows everything
- **This is what React simplifies** - Same result, cleaner code

### Connections to Backend
- Form fields match backend API schema (source, description, location)
- Table displays same data structure as database
- JavaScript will call backend API (Day 24)
- File inputs ready for audio/image uploads

### Preparation for React
- Understanding HTML/CSS/JS makes React easier
- React components are just JavaScript that returns HTML
- React handles DOM manipulation automatically
- Same concepts, better developer experience

---

*Day 22 complete! Ready for React!* 🌐


## Day 23: React Concepts

**Paradigm shift:** From imperative (vanilla JS) to declarative (React)

### React Core Concepts

1. **Components**: Reusable UI pieces (JavaScript functions returning JSX)
2. **Props**: Data passed from parent to child (read-only)
3. **State**: Data that can change (`useState` hook)
4. **JSX**: HTML-like syntax in JavaScript
5. **Events**: Handle user interactions (`onClick`, `onChange`)

### useState Hook
```javascript
const [value, setValue] = useState(initialValue);
//      ↑       ↑                    ↑
//   current  updater            starting value
```

**Key insight:** When you call `setValue()`, React re-renders the component!

### JSX vs HTML Differences

| HTML | JSX | Why |
|------|-----|-----|
| `class` | `className` | `class` is JavaScript keyword |
| `onclick` | `onClick` | CamelCase for all events |
| `<img>` | `<img />` | All tags must close |
| `for` | `htmlFor` | `for` is JavaScript keyword |

### Component Composition
```javascript
<App>
  <Header />
  <Main>
    <IncidentList>
      <IncidentCard />
      <IncidentCard />
    </IncidentList>
  </Main>
</App>
```

Components inside components - like LEGO blocks!

### What I Built

- ✅ React app with Vite
- ✅ Custom App component
- ✅ IncidentCard component (reusable!)
- ✅ Interactive counter (state demo)
- ✅ Props passing between components
- ✅ Modern styling with CSS

### Key Realizations

**Imperative vs Declarative:**
- **Imperative (vanilla JS)**: "Create element, set attributes, append to parent"
- **Declarative (React)**: "Here's what I want, React makes it happen"

**State is magical:**
- Change state → UI updates automatically
- No manual DOM manipulation needed
- React handles all the updates

**Components are powerful:**
- Write once, use everywhere
- Pass different props for different data
- Each instance is independent

### Mental Model Shift

**Before React:**
```
Think: "How do I modify the DOM?"
Code: Manual createElement, appendChild, etc.
```

**With React:**
```
Think: "What should the UI look like?"
Code: Return JSX describing the UI
```

### Preparation for Tomorrow (Day 24)

- Learn `useEffect` for side effects (like API calls)
- Fetch data from backend API
- Display real incidents from database
- Handle loading and error states

---

*Day 23 complete! React fundamentals mastered!* ⚛️


## Day 24: Fetching from Backend in React

**The connection!** Frontend now talks to backend!

### Core Concepts

1. **fetch()**: Built-in JavaScript function for HTTP requests
2. **useEffect**: React hook for side effects (runs after render)
3. **Promises**: Represent future values (API responses)
4. **async/await**: Clean syntax for working with promises
5. **Three-state pattern**: loading, error, success

### useEffect Deep Dive
```javascript
useEffect(() => {
    // This function runs AFTER component renders
    fetchData();
}, []);  // Dependencies array
```

**Dependency array controls when effect runs:**
- `[]` - Run once on mount
- `[count]` - Run when count changes
- No array - Run on every render (usually wrong!)

### API Call Pattern
```javascript
// 1. Start with loading=true
const [loading, setLoading] = useState(true);

// 2. Fetch in useEffect
useEffect(() => {
    async function fetch() {
        try {
            const data = await getIncidents();
            setIncidents(data);
            setLoading(false);
        } catch (err) {
            setError(err.message);
            setLoading(false);
        }
    }
    fetch();
}, []);

// 3. Render based on state
if (loading) return <Loading />;
if (error) return <Error />;
return <Data />;
```

### What I Built

- ✅ API client module (centralized API calls)
- ✅ HealthCheck component (tests API connection)
- ✅ IncidentsList component (fetches and displays real data)
- ✅ Loading states (shows "Loading..." while fetching)
- ✅ Error handling (shows errors if API fails)
- ✅ Real-time data from database!

### Key Realizations

**Data flow:**
1. Component mounts
2. useEffect runs
3. Fetch data from API
4. Update state with data
5. Component re-renders with new data
6. User sees real data!

**Why useEffect:**
- Can't fetch in component body (would cause infinite loop!)
- Can't make component function async
- useEffect is the "official" way to do side effects

**CORS is important:**
- Without CORS, browser blocks requests
- Backend must explicitly allow frontend origin
- Already configured in our FastAPI app!

### Debugging Tools Used

- Browser Console - See API logs
- Network tab - See HTTP requests/responses
- React DevTools - Inspect component state
- Backend logs - See server-side processing

### Connections Made

**Frontend ↔ Backend:**
- React on port 5174
- FastAPI on port 8000
- HTTP requests between them
- JSON data format
- Real-time updates!

**Components working together:**
- App.jsx (parent container)
- HealthCheck.jsx (API status)
- IncidentsList.jsx (fetches data)
- IncidentCard.jsx (displays one incident)

### Mental Model

**Before today:**
```
React: Hardcoded data in components
Backend: Has data but no one uses it
```

**After today:**
```
React: "Give me incidents!" → API call
Backend: "Here's the data!" → JSON response
React: Updates state → UI shows data
```

---

*Day 24 complete! Frontend and backend connected!* 🔗