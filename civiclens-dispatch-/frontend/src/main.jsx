// frontend/src/main.jsx
// Application entry point — mounts the React tree into #root.
//
// Day 72: Wrapped App in AuthProvider so every component can call
//          useAuth() to read the current user and token.

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
// AuthProvider holds the JWT token and user object for the entire app tree
import { AuthProvider } from './context/AuthContext.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    {/* AuthProvider must wrap App so useAuth() works in any component */}
    <AuthProvider>
      <App />
    </AuthProvider>
  </StrictMode>,
)
