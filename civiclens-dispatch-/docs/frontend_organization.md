# Frontend Organization Guide

## Where to Put New Files

### New Component

**Question:** Where does this component go?

**Decision tree:**

1. **Is it specific to dashboard view?**
   → `components/dashboard/`
   
2. **Is it a form or form-related?**
   → `components/forms/`
   
3. **Is it layout/structure?**
   → `components/layout/`
   
4. **Is it reusable across app?**
   → `components/shared/`

### New Hook

**All custom hooks go in:**
→ `hooks/`

**Naming:** `useFeatureName.js`

Examples:
- `useToast.js`
- `useAuth.js` (future)
- `useLocalStorage.js` (future)

### New Utility Function

**Helper functions go in:**
→ `utils/`

Examples:
- `formatDate.js`
- `validateEmail.js`
- `calculations.js`

### New Page/View

**Major views go in:**
→ `pages/` (create this folder when needed)

Examples:
- `DashboardPage.jsx`
- `LoginPage.jsx`
- `SettingsPage.jsx`

## Naming Conventions

### Components
- **Format:** PascalCase
- **Examples:** `IncidentTable.jsx`, `SubmitForm.jsx`
- **CSS:** Match component name (`IncidentTable.css`)

### Hooks
- **Format:** camelCase with 'use' prefix
- **Examples:** `useToast.js`, `useAuth.js`

### Utilities
- **Format:** camelCase
- **Examples:** `formatDate.js`, `apiClient.js`

### CSS Files
- **Format:** Match corresponding .jsx file
- **Examples:** `App.css` for `App.jsx`

## Import Patterns

### Relative Imports
```javascript
// Same folder
import Component from './Component'

// Parent folder
import Component from '../Component'

// Grandparent folder
import Component from '../../Component'
```

### Absolute Imports (Future)

Configure in `vite.config.js`:
```javascript
resolve: {
    alias: {
        '@': '/src',
        '@components': '/src/components',
    }
}
```

Then:
```javascript
import Component from '@components/shared/Component'
```

## Component File Structure

### Standard Component File
```javascript
// 1. Imports
import { useState } from 'react'
import './Component.css'

// 2. Component function
function Component({ prop1, prop2 }) {
    // State
    const [state, setState] = useState()
    
    // Event handlers
    function handleEvent() {
        // Logic
    }
    
    // Return JSX
    return (
        <div>
            {/* Content */}
        </div>
    )
}

// 3. Export
export default Component
```

## CSS File Structure
```css
/* Component name and description */

/* Main container */
.component-container {
    /* Styles */
}

/* Sub-elements */
.component-header {
    /* Styles */
}

.component-body {
    /* Styles */
}

/* State variants */
.component-loading {
    /* Styles */
}

.component-error {
    /* Styles */
}

/* Responsive */
@media (max-width: 768px) {
    .component-container {
        /* Mobile styles */
    }
}
```

## When to Create New Component

**Create new component if:**
- ✅ Used in multiple places
- ✅ Complex logic (> 100 lines)
- ✅ Conceptually separate piece
- ✅ Needs independent state

**Keep in parent if:**
- ❌ Only used once
- ❌ Very simple (< 20 lines)
- ❌ Tightly coupled to parent
- ❌ No independent logic

## Refactoring Checklist

Before refactoring:
- [ ] All tests passing (or write tests first)
- [ ] Commit current code (easy to revert)
- [ ] One refactoring at a time

During refactoring:
- [ ] Keep existing behavior
- [ ] Update imports
- [ ] Test after each change
- [ ] Update documentation

After refactoring:
- [ ] All features still work
- [ ] No console errors
- [ ] Code is clearer
- [ ] Commit changes

---

*Organization guide: Day 30*