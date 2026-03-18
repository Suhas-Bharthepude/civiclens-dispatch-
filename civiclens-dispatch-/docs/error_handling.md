# Error Handling Guide (Day 29)

## Philosophy

**Every operation that can fail, should handle failure gracefully.**

Users should:
1. Know what happened
2. Understand why it happened
3. Know how to fix it or try again

## Error Handling Patterns

### Pattern 1: Try-Catch with State
```javascript
const [error, setError] = useState(null);

async function fetchData() {
    try {
        const data = await api();
        setData(data);
    } catch (err) {
        setError(err.message);
    }
}
```

### Pattern 2: Three-State Pattern
```javascript
const [data, setData] = useState(null);
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);

// Render based on state
if (loading) return <Loading />;
if (error) return <Error error={error} onRetry={fetchData} />;
return <Data data={data} />;
```

### Pattern 3: Error Boundaries (React)
```javascript
class ErrorBoundary extends React.Component {
    state = { hasError: false };
    
    static getDerivedStateFromError(error) {
        return { hasError: true };
    }
    
    render() {
        if (this.state.hasError) {
            return <h1>Something went wrong.</h1>;
        }
        return this.props.children;
    }
}
```

## Loading States

### Spinner (Default)
**When to use:** General purpose, unknown duration
```javascript
<LoadingState type="spinner" message="Loading..." />
```

### Skeleton (Better UX)
**When to use:** Loading tables, lists, cards (known structure)
```javascript
<LoadingState type="skeleton" rows={5} />
```

**Why better:**
- Shows layout immediately
- Feels faster
- Reduces perceived wait time

### Inline (Buttons)
**When to use:** Button actions (submit, save, etc.)
```javascript
<button disabled={loading}>
    {loading ? <LoadingState type="inline" /> : 'Submit'}
</button>
```

## Toast Notifications

### Usage
```javascript
// In component
const { showToast } = useToast();

// Show success
showToast('Data saved!', 'success');

// Show error
showToast('Failed to save', 'error');

// Show warning
showToast('Connection unstable', 'warning');

// Show info
showToast('Processing...', 'info', 10000);  // 10 seconds
```

### Toast Types

| Type | Color | Icon | Usage |
|------|-------|------|-------|
| success | Green | ✅ | Successful operations |
| error | Red | ❌ | Failed operations |
| warning | Orange | ⚠️ | Warnings, cautions |
| info | Blue | ℹ️ | Information, status |

### Auto-Dismiss

Toasts automatically dismiss after duration:
- Default: 5000ms (5 seconds)
- Success: 5000ms
- Error: 7000ms (longer so user can read)
- Warning: 6000ms

User can also manually close with X button.

## Retry Logic

### When to Provide Retry

✅ Network errors (server down, timeout)  
✅ Temporary failures (rate limit, server busy)  
✅ User actions (form submission failed)  

❌ Don't retry on validation errors (user input wrong)  
❌ Don't retry on 404 (resource doesn't exist)  

### Implementation
```javascript
const [retryCount, setRetryCount] = useState(0);

async function fetchData() {
    try {
        const data = await api();
        setData(data);
        setError(null);
    } catch (err) {
        setError(err.message);
    }
}

// Retry button
<button onClick={() => {
    setRetryCount(prev => prev + 1);
    setError(null);
    setLoading(true);
}}>
    Retry {retryCount > 0 && `(Attempt ${retryCount + 1})`}
</button>
```

## Error Messages

### Good Error Messages

✅ **Specific**: "Failed to connect to database" (not "Error")  
✅ **Actionable**: "Check backend is running on port 8000"  
✅ **Friendly**: "Something went wrong" (not "ERROR 500")  
✅ **Helpful**: Include retry button or troubleshooting steps  

### Bad Error Messages

❌ "Error" (what error?)  
❌ "null is not an object" (technical, unhelpful)  
❌ "500" (what does that mean to user?)  
❌ Silent failures (no message at all)  

## Network Error Handling

### Common Errors

**Network request failed**
- Cause: Backend not running, wrong URL, firewall
- Message: "Unable to connect to server. Please check backend is running."
- Action: Retry button

**Timeout**
- Cause: Server too slow, network slow
- Message: "Request timed out. Server may be busy."
- Action: Retry button

**404 Not Found**
- Cause: Wrong endpoint, resource deleted
- Message: "Requested resource not found."
- Action: Go back or refresh

**500 Server Error**
- Cause: Backend code error
- Message: "Server encountered an error. Please try again later."
- Action: Retry button, contact support

## Form Validation

### Client-Side Validation
```javascript
function validateForm() {
    if (field.length < 10) {
        setError("Too short");
        return false;
    }
    return true;
}

if (!validateForm()) return;  // Stop submission
```

### Server-Side Validation
```javascript
try {
    await submitForm(data);
} catch (error) {
    // Backend returned validation error
    if (error.status === 422) {
        setError("Invalid data format");
    }
}
```

**Always validate on both sides:**
- Client: Better UX (instant feedback)
- Server: Security (never trust client)

## Loading UX Best Practices

✅ Show loading immediately (< 100ms delay)  
✅ Use skeleton screens for known layouts  
✅ Disable buttons during submission  
✅ Show progress for long operations  
✅ Provide cancel option for long operations  

❌ Don't show blank screen while loading  
❌ Don't use spinners for everything  
❌ Don't let users double-click submit  

---

*Error handling complete: Day 29*