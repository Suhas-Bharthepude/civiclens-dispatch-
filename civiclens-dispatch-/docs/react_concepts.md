# React Concepts (Day 23)

## What is React?

React is a **JavaScript library** for building user interfaces.

**Key philosophy:** Build complex UIs from small, reusable pieces (components).

## Core Concepts

### 1. Components

A component is a JavaScript function that returns JSX (HTML-like syntax).

**Simple component:**
```javascript
function Welcome() {
    return <h1>Hello!</h1>;
}
```

**Using a component:**
```javascript
<Welcome />  // Renders: <h1>Hello!</h1>
```

**Why components?**
- ✅ Reusable
- ✅ Testable
- ✅ Maintainable
- ✅ Composable (combine to make bigger components)

### 2. Props (Properties)

Props are arguments passed to components.

**Parent passes props:**
```javascript
<Greeting name="Alice" age={25} />
```

**Child receives props:**
```javascript
function Greeting(props) {
    return <h1>Hello {props.name}, you are {props.age}</h1>;
}
```

**Props are:**
- ✅ Read-only (can't be modified by child)
- ✅ Passed from parent to child (one-way data flow)
- ✅ Can be any type (string, number, object, function, etc.)

**Destructuring props (cleaner syntax):**
```javascript
function Greeting({ name, age }) {
    return <h1>Hello {name}, you are {age}</h1>;
}
```

### 3. State

State is data that can change over time.

**Creating state:**
```javascript
import { useState } from 'react';

function Counter() {
    // Declare state variable
    const [count, setCount] = useState(0);
    //      ↑       ↑              ↑
    //   current  setter      initial value
    
    return (
        <>
            <p>Count: {count}</p>
            <button onClick={() => setCount(count + 1)}>
                Increment
            </button>
        </>
    );
}
```

**When state changes:**
1. Component re-renders automatically
2. UI updates to show new value
3. React only updates what changed (efficient!)

**State rules:**
- ✅ Never modify state directly: `count = 5` ❌
- ✅ Always use setter function: `setCount(5)` ✅
- ✅ State updates trigger re-render
- ✅ Each component has its own state

### 4. JSX (JavaScript XML)

JSX looks like HTML but it's JavaScript.

**JSX syntax:**
```javascript
const element = <h1>Hello World</h1>;
```

**Embedding expressions:**
```javascript
const name = "Alice";
const element = <h1>Hello {name}</h1>;  // Hello Alice
```

**JSX rules:**
- Use `className` not `class`
- All tags must close: `<img />` not `<img>`
- Use camelCase for attributes: `onClick` not `onclick`
- Return one parent element

**Wrong:**
```javascript
return (
    <h1>Title</h1>
    <p>Text</p>
);
```

**Right:**
```javascript
return (
    <>
        <h1>Title</h1>
        <p>Text</p>
    </>
);
```

### 5. Events

Handle user interactions with event handlers.

**Syntax:**
```javascript
<button onClick={handleClick}>Click</button>
```

**Common events:**
- `onClick` - Click
- `onChange` - Input changed
- `onSubmit` - Form submitted
- `onMouseEnter` - Mouse over
- `onFocus` - Element focused

**Event handler function:**
```javascript
function handleClick(event) {
    event.preventDefault();  // Prevent default behavior
    console.log('Button clicked!');
}

<button onClick={handleClick}>Click</button>
```

**Inline arrow function:**
```javascript
<button onClick={() => console.log('Clicked!')}>
    Click
</button>
```

## Component Patterns

### Functional Component (Modern)
```javascript
function MyComponent(props) {
    return <div>{props.text}</div>;
}
```

### With Props Destructuring
```javascript
function MyComponent({ text, count }) {
    return <div>{text}: {count}</div>;
}
```

### With State
```javascript
import { useState } from 'react';

function MyComponent() {
    const [value, setValue] = useState(0);
    
    return (
        <div>
            <p>{value}</p>
            <button onClick={() => setValue(value + 1)}>
                Increment
            </button>
        </div>
    );
}
```

## Data Flow in React
```
Parent Component (has data)
    ↓ (passes data via props)
Child Component (displays data)
```

**Example:**
```javascript
// Parent
function App() {
    const incidents = [
        { id: 1, desc: "Fire" },
        { id: 2, desc: "Accident" }
    ];
    
    return (
        <div>
            {incidents.map(incident => (
                <IncidentCard 
                    key={incident.id}
                    description={incident.desc}
                />
            ))}
        </div>
    );
}

// Child
function IncidentCard({ description }) {
    return <div>{description}</div>;
}
```

## React vs Vanilla JavaScript

### Vanilla JavaScript (Yesterday)
```javascript
// Create element
const div = document.createElement('div');
div.className = 'card';
div.innerHTML = `<h3>${title}</h3><p>${text}</p>`;
document.body.appendChild(div);
```

### React (Today)
```javascript
// Component
function Card({ title, text }) {
    return (
        <div className="card">
            <h3>{title}</h3>
            <p>{text}</p>
        </div>
    );
}

// Use it
<Card title="Hello" text="World" />
```

**React is:**
- ✅ Cleaner
- ✅ Less error-prone
- ✅ Easier to reason about
- ✅ Automatically updates when data changes

## How React Works (Simplified)

1. **You write components** (JavaScript functions returning JSX)
2. **React builds a virtual DOM** (JavaScript representation of UI)
3. **React compares** old vs new virtual DOM
4. **React updates only what changed** in real DOM (efficient!)

**You don't touch the real DOM** - React handles it!

## Common Patterns

### Conditional Rendering
```javascript
// Show element only if condition is true
{isLoggedIn && <p>Welcome!</p>}

// Show different elements based on condition
{isLoggedIn ? <Dashboard /> : <Login />}
```

### Mapping Arrays to Components
```javascript
const items = ['apple', 'banana', 'orange'];

return (
    <ul>
        {items.map((item, index) => (
            <li key={index}>{item}</li>
        ))}
    </ul>
);
```

**Always provide a `key` prop** when mapping!

---

## CivicLens Application to React

### What We'll Build (Days 24-30)

**Components we'll create:**
- `App.jsx` - Main container
- `IncidentList.jsx` - Table of incidents
- `IncidentCard.jsx` - Single incident display
- `IncidentForm.jsx` - Submission form
- `Header.jsx` - Top navigation
- `IncidentDetail.jsx` - Detailed view

**Data flow:**
```
App (fetches incidents from API)
  ↓ props: incidents array
IncidentList (maps over incidents)
  ↓ props: single incident data
IncidentCard (displays one incident)
```

### Today's Learning Applied

1. **Components** → Each UI piece becomes a component
2. **Props** → Pass incident data down
3. **State** → Track selected incident, form inputs
4. **Events** → Handle form submission, row clicks
5. **JSX** → Write HTML-like code in JavaScript

---

## Debugging React

### Browser Console

**See component tree:**
- Install React DevTools extension
- Inspect components
- View props and state

**Console logging:**
```javascript
function MyComponent(props) {
    console.log('Props:', props);
    console.log('Rendering MyComponent');
    
    return <div>{props.text}</div>;
}
```

### Common Errors

**"Cannot read property of undefined"**
- Props might be undefined
- Add default values or conditional rendering

**"Each child in a list should have a unique key"**
- Add `key` prop when mapping arrays
- Use unique value (like ID)

**"Hooks can only be called inside function components"**
- `useState` must be at top level of component
- Can't be in if statements or loops

---

*Day 23 complete! React fundamentals learned!* ⚛️