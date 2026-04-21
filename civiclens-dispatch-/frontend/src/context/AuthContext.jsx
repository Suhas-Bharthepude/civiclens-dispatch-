// frontend/src/context/AuthContext.jsx
// React context that holds the authenticated user's state and exposes
// login / logout actions to the entire component tree.
//
// Day 72: Auth with admin and dispatcher roles
//
// Token storage: sessionStorage (NOT localStorage).
//   sessionStorage is cleared when the browser tab closes.
//   localStorage would persist across sessions — a security risk for
//   auth tokens that should expire with the work session.
//
// Usage:
//   import { useAuth } from './context/AuthContext'
//   const { user, token, login, logout } = useAuth()

import { createContext, useContext, useState, useCallback } from 'react'
import { loginUser } from '../api/client'


// Create the context — null default forces every consumer to be inside AuthProvider
const AuthContext = createContext(null)


// ── PROVIDER ──────────────────────────────────────────────
// Wrap the app in this so all components can read auth state
export function AuthProvider({ children }) {

  // Rehydrate from sessionStorage so a page refresh doesn't log the user out
  // JSON.parse(null) returns null, which is the correct "not logged in" value
  const [token, setToken] = useState(
    () => sessionStorage.getItem('auth_token')
  )
  const [user, setUser] = useState(
    () => {
      const stored = sessionStorage.getItem('auth_user')
      // Guard against malformed JSON that might have been left by a bug
      try { return stored ? JSON.parse(stored) : null }
      catch { return null }
    }
  )


  // ── LOGIN ────────────────────────────────────────────────
  // Calls POST /auth/login, stores the token + user, updates state.
  // Throws on bad credentials so the LoginPage can show the error.
  const login = useCallback(async (username, password) => {
    // loginUser is defined in api/client.js — it bypasses the auth header
    // injection since we don't have a token yet at this point
    const data = await loginUser(username, password)

    // Persist to sessionStorage so a tab refresh keeps the user logged in
    sessionStorage.setItem('auth_token', data.access_token)
    sessionStorage.setItem('auth_user', JSON.stringify(data.user))

    // Update React state — triggers re-render in App.jsx (login page → dashboard)
    setToken(data.access_token)
    setUser(data.user)
  }, [])


  // ── LOGOUT ───────────────────────────────────────────────
  // Clears both storage and state — App.jsx will render the login page
  const logout = useCallback(() => {
    sessionStorage.removeItem('auth_token')
    sessionStorage.removeItem('auth_user')
    setToken(null)
    setUser(null)
  }, [])


  return (
    <AuthContext.Provider value={{ token, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}


// ── HOOK ──────────────────────────────────────────────────
// Components call useAuth() instead of useContext(AuthContext) directly.
// The guard ensures a clear error message if someone forgets AuthProvider.
export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be called inside <AuthProvider>')
  return ctx
}
