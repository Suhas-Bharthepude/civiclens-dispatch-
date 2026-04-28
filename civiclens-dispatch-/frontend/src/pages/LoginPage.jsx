// frontend/src/pages/LoginPage.jsx
// Full-page login form shown when no auth token is present.
//
// Day 72: Auth with admin and dispatcher roles
//
// Submits username + password to POST /auth/login via AuthContext.login().
// On success, AuthContext updates state → App.jsx re-renders the dashboard.
// On failure, the error detail from the API is shown inline.

import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import './LoginPage.css'


const LoginPage = () => {

  const [username, setUsername] = useState('dispatcher')
  const [password, setPassword] = useState('dispatch123')
  // error: API error message shown below the form
  const [error,    setError]    = useState(null)
  // loading: true while the login request is in flight
  const [loading,  setLoading]  = useState(false)

  const { login } = useAuth()


  // ── SUBMIT HANDLER ────────────────────────────────────
  const handleSubmit = async (e) => {
    // Prevent the default browser form submission (page reload)
    e.preventDefault()

    // Client-side guard — avoids an API call for obviously empty fields
    if (!username.trim() || !password.trim()) {
      setError('Username and password are required')
      return
    }

    setLoading(true)
    setError(null)

    try {
      // AuthContext.login() calls POST /auth/login and stores the token.
      // On success it updates state → App.jsx removes this page from the tree.
      await login(username.trim(), password)
    } catch (err) {
      // The API returns a human-readable error in err.message
      setError(err.message || 'Login failed — check your credentials')
    } finally {
      setLoading(false)
    }
  }


  return (
    <div className="login-page">
      <div className="login-card">

        {/* ── BRANDING ─────────────────────────────────── */}
        <div className="login-header">
          <span className="login-icon">🚨</span>
          <h1 className="login-title">CivicLens Dispatch</h1>
          <p className="login-subtitle">AI-Powered Incident Management</p>
        </div>

        {/* ── FORM ─────────────────────────────────────── */}
        <form className="login-form" onSubmit={handleSubmit}>

          {/* Inline error banner — only visible after a failed attempt */}
          {error && (
            <div className="login-error" role="alert">
              ⚠️ {error}
            </div>
          )}

          <div className="login-field">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={e => setUsername(e.target.value)}
              placeholder="Enter your username"
              autoComplete="username"
              autoFocus
              disabled={loading}
            />
          </div>

          <div className="login-field">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="Enter your password"
              autoComplete="current-password"
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            className="login-btn"
            disabled={loading}
          >
            {loading ? 'Signing in…' : 'Sign In'}
          </button>

        </form>

        {/* ── FOOTER NOTE ──────────────────────────────── */}
        <p className="login-footer-note">
          For life-threatening emergencies always call 911
        </p>

      </div>
    </div>
  )
}

export default LoginPage
