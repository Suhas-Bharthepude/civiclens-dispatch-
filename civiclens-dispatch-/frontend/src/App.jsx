// frontend/src/App.jsx
// This is the main App component - the root of your React application
// Everything in your app will be inside this component

// Import useState hook from React
// Hooks are special functions that let you use React features
// useState lets you add state (data that can change) to a component
import { useState } from 'react'

// Import CSS file for styling
// This CSS applies to this component
import './App.css'


import IncidentCard from './IncidentCard'



// ========================================
// APP COMPONENT
// ========================================

// This is a FUNCTION COMPONENT
// It's a JavaScript function that returns JSX (looks like HTML)
function App() {
  
  // ========================================
  // STATE
  // ========================================
  
  // useState() creates a piece of state
  // const [value, setValue] = useState(initialValue)
  //         ↑       ↑                    ↑
  //      current  function to         starting
  //      value    change it            value
  
  // State: counter that starts at 0
  const [count, setCount] = useState(0)
  
  // When you call setCount(5), React:
  // 1. Updates count to 5
  // 2. Re-renders the component
  // 3. User sees the new value!
  
  
  // ========================================
  // RETURN JSX
  // ========================================
  
  // This component returns JSX (HTML-like syntax)
  // Everything inside return() is what users see
  return (
    // Fragment - wraps multiple elements without adding extra div
    <>
      
      {/* Main container div */}
      <div className="app-container">
        
        {/* HEADER */}
        <header className="app-header">
          <h1>🚨 CivicLens Dispatch</h1>
          <p>Emergency Incident Triage System</p>
        </header>
        
        {/* MAIN CONTENT */}
        <main className="app-main">
          
          {/* Welcome message */}
          <div className="welcome-section">
            <h2>Welcome to React! 🎉</h2>
            <p>This is your first React component.</p>
            <p>You're viewing the App component in <code>src/App.jsx</code></p>
          </div>
          
          {/* Counter example - demonstrates state */}
          <div className="counter-section">
            <h3>Interactive Counter (React State Demo)</h3>
            <p>Current count: <strong>{count}</strong></p>
            
            {/* Button to increment counter */}
            {/* onClick is a prop that takes a function */}
            {/* () => setCount(count + 1) is an arrow function */}
            {/* When clicked, it increases count by 1 */}
            <button onClick={() => setCount(count + 1)}>
              Increment Count
            </button>
            
            {/* Button to reset counter */}
            <button onClick={() => setCount(0)} style={{ marginLeft: '10px' }}>
              Reset
            </button>
          </div>
          
          {/* Information about next steps */}
          <div className="info-section">
            <h3>📋 Next Steps</h3>
            <ul>
              <li>✅ React app is running</li>
              <li>✅ State is working (try the counter!)</li>
              <li>🔄 Tomorrow: Build real components for CivicLens</li>
              <li>🔄 Day 24: Connect to backend API</li>
            </ul>
          </div>

          {/* Demo: Using our custom component */}
          <div className="demo-section">
            <h3>Custom Component Demo</h3>
            {/* Use IncidentCard component */}
            {/* We pass data via props */}
            <IncidentCard 
              id={1}
              source="citizen"
              description="Fire on Main Street"
              location="123 Main St"
              severity="high"
            />
  
            {/* Use it again with different data! */}
            <IncidentCard 
              id={2}
                source="police"
                description="Car accident"
                location="Highway 101"
                severity="medium"
            />
          </div>
                        
          
        </main>
        
      </div>
    </>
  )
}

// ========================================
// EXPORT
// ========================================

// Export the component so other files can import it
// This is required for the component to be used in main.jsx
export default App