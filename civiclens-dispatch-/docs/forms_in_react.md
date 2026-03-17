# Forms in React (Day 27)

## Controlled vs Uncontrolled Inputs

### Uncontrolled (DOM manages value)
```javascript
// React doesn't know the value
<input type="text" />
```

### Controlled (React manages value)
```javascript
const [value, setValue] = useState('');

<input 
    value={value}
    onChange={(e) => setValue(e.target.value)}
/>
```

**Always use controlled inputs in React!**

## Form State Pattern
```javascript
// Single state object for all fields
const [formData, setFormData] = useState({
    field1: '',
    field2: '',
    field3: ''
});

// Update specific field
function handleChange(event) {
    const { name, value } = event.target;
    
    setFormData({
        ...formData,      // Copy existing
        [name]: value     // Update one field
    });
}

// Use in inputs
<input 
    name="field1"
    value={formData.field1}
    onChange={handleChange}
/>
```

## Form Submission Pattern
```javascript
async function handleSubmit(event) {
    // 1. Prevent default
    event.preventDefault();
    
    // 2. Validate
    if (!validateForm()) return;
    
    // 3. Set loading state
    setSubmitting(true);
    
    try {
        // 4. Call API
        await createIncident(formData);
        
        // 5. Show success
        setSuccess(true);
        
        // 6. Reset form
        setFormData({ field1: '', field2: '' });
        
    } catch (error) {
        // 7. Show error
        setError(error.message);
    } finally {
        // 8. Turn off loading
        setSubmitting(false);
    }
}
```

## File Uploads
```javascript
const [file, setFile] = useState(null);

function handleFileChange(event) {
    const file = event.target.files[0];
    setFile(file);
}

<input 
    type="file"
    accept="image/*"
    onChange={handleFileChange}
/>

// Show selected file
{file && <p>{file.name} ({file.size} bytes)</p>}
```

## Validation

### HTML5 Validation
```javascript
<input required />                    // Can't be empty
<input type="email" required />       // Must be valid email
<input minLength={10} />             // Minimum length
<input pattern="[0-9]{3}" />         // Must match regex
```

### JavaScript Validation
```javascript
function validateForm() {
    if (description.length < 10) {
        setError("Too short!");
        return false;
    }
    return true;
}

// In handleSubmit
if (!validateForm()) return;
```

## Form State Management

### Three States
1. **Idle** - Form is empty, ready for input
2. **Submitting** - API call in progress
3. **Success/Error** - Show result message
```javascript
const [submitting, setSubmitting] = useState(false);
const [success, setSuccess] = useState(false);
const [error, setError] = useState(null);

// Button shows different text
<button disabled={submitting}>
    {submitting ? 'Submitting...' : 'Submit'}
</button>
```

## Parent-Child Communication

### Child Notifies Parent
```javascript
// Parent
function Parent() {
    function handleSubmit() {
        refreshList();  // Refresh data
    }
    
    return <Form onSubmit={handleSubmit} />;
}

// Child
function Form({ onSubmit }) {
    async function handleSubmit(e) {
        e.preventDefault();
        await createData();
        onSubmit();  // Notify parent
    }
}
```

## Best Practices

✅ Use controlled inputs  
✅ Validate before submission  
✅ Show loading state  
✅ Handle errors gracefully  
✅ Reset form after success  
✅ Disable submit while submitting  
✅ Use semantic HTML (`<form>`, `<label>`, etc.)  

❌ Don't forget `event.preventDefault()`  
❌ Don't mutate state directly  
❌ Don't ignore errors  
❌ Don't forget to clear file inputs  

---

*Day 27 complete!*