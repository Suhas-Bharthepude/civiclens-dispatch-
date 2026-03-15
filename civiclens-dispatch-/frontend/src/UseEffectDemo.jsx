// frontend/src/UseEffectDemo.jsx
// This component demonstrates how useEffect works
// It's a learning example before we use it for real API calls

// Import useState and useEffect hooks from React
import { useState, useEffect } from 'react'


// ========================================
// USE EFFECT DEMO COMPONENT
// ========================================

function UseEffectDemo() {
    
    // ========================================
    // STATE
    // ========================================
    
    // State: counter starts at 0
    const [count, setCount] = useState(0)
    
    // State: message from API
    const [apiMessage, setApiMessage] = useState('')
    
    
    // ========================================
    // EFFECT 1: Runs once when component mounts
    // ========================================
    
    // useEffect takes two arguments:
    // 1. A function to run (the effect)
    // 2. A dependency array (when to run)
    useEffect(() => {
        // This code runs AFTER the component renders
        console.log('Component mounted! This runs ONCE.');
        
        // Set a message
        setApiMessage('Component loaded successfully!');
        
        // Empty dependency array [] means:
        // "Run this effect only once when component first appears"
        // Like componentDidMount in class components
    }, []);
    
    
    // ========================================
    // EFFECT 2: Runs when count changes
    // ========================================
    
    useEffect(() => {
        // This runs:
        // 1. Once when component mounts
        // 2. Every time 'count' changes
        console.log(`Count changed to: ${count}`);
        
        // Dependency array [count] means:
        // "Run this effect whenever count changes"
    }, [count]);
    
    
    // ========================================
    // RETURN JSX
    // ========================================
    
    return (
        <div style={{ padding: '20px', backgroundColor: '#f0f0f0', borderRadius: '8px' }}>
            <h3>useEffect Demo</h3>
            
            <p><strong>Count:</strong> {count}</p>
            
            <button onClick={() => setCount(count + 1)}>
                Increment (triggers Effect 2)
            </button>
            
            <p style={{ marginTop: '20px' }}>
                <strong>API Message:</strong> {apiMessage}
            </p>
            
            <div style={{ marginTop: '20px', fontSize: '14px', color: '#666' }}>
                <p><strong>What's happening:</strong></p>
                <ul>
                    <li>Effect 1 ran once when component mounted</li>
                    <li>Effect 2 runs every time you click increment</li>
                    <li>Check browser console to see logs!</li>
                </ul>
            </div>
        </div>
    )
}

export default UseEffectDemo