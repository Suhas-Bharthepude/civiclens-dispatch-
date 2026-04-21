// frontend/src/App.jsx
// Root component — owns top-level state and layout.
//
// Day 70: Added "Live Feed / Analytics" toggle in the header.
//          Conditionally renders DashboardLayout or AnalyticsView.
// Day 71: Added useIncidentStream for WebSocket live updates.
//          Passes wsUpdate + wsConnected down to IncidentsList.
//          Shows "● Live" indicator when WebSocket is connected.
// Day 72: Reads auth from AuthContext; shows login page when not
//          authenticated; logout button in header; passes user role.

import { useState, useEffect } from 'react'
import './App.css'
import useToast           from './hooks/useToast'
import useIncidentStream  from './hooks/useIncidentStream'
import HealthCheck        from './components/dashboard/HealthCheck'
import IncidentsList      from './components/dashboard/IncidentsList'
import IncidentDetail     from './components/dashboard/IncidentDetail'
import SubmitIncidentForm from './components/forms/SubmitIncidentForm'
import DashboardLayout    from './components/layout/DashboardLayout'
import ToastContainer     from './components/shared/ToastContainer'
import StatsBar           from './components/dashboard/StatsBar'
import AIStatusIndicator  from './components/dashboard/AIStatusIndicator'
import AnalyticsView      from './components/analytics/AnalyticsView'
import { useAuth }        from './context/AuthContext'
import LoginPage          from './pages/LoginPage'


function App() {
  const [selectedIncident, setSelectedIncident] = useState(null)
  const [refreshTrigger,   setRefreshTrigger]   = useState(0)
  // activeView: 'live' shows the dashboard, 'analytics' shows charts (Day 70)
  const [activeView,       setActiveView]       = useState('live')
  // wsUpdate: the latest WebSocket event object — passed to IncidentsList (Day 71)
  const [wsUpdate,         setWsUpdate]         = useState(null)

  const { toasts, showToast: addToast } = useToast()
  // Read auth state from context (Day 72)
  const { user, logout } = useAuth()

  // ── WEBSOCKET STREAM (Day 71) ──────────────────────────
  // Opens ws://localhost:8000/ws/incidents on mount.
  // Each message is forwarded to IncidentsList via wsUpdate state.
  const { connected: wsConnected } = useIncidentStream((event) => {
    // Forward the parsed event to IncidentsList — it handles prepend/replace
    setWsUpdate(event)
  })

  // ── KEYBOARD SHORTCUT ─────────────────────────────────
  // ESC closes the detail panel without reaching for the mouse
  useEffect(() => {
    const onKey = (e) => {
      if (e.key === 'Escape' && selectedIncident) setSelectedIncident(null)
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [selectedIncident])

  const handleSelect    = (inc) => setSelectedIncident(inc)
  const handleClose     = ()    => setSelectedIncident(null)

  // Called by IncidentDetail when dispatcher clicks a status button.
  // 1. Optimistic update: detail panel reflects the new status immediately
  // 2. refreshTrigger: re-fetches the table row so its badge updates too
  const handleStatusChange = (id, newStatus) => {
    setSelectedIncident(prev =>
      prev && prev.id === id
        ? { ...prev, status: newStatus }
        : prev
    )
    setRefreshTrigger(n => n + 1)
  }

  // Called after an incident is deleted (Day 72)
  // Closes the detail panel and triggers a table refresh
  const handleDeleted = () => {
    setSelectedIncident(null)
    setRefreshTrigger(n => n + 1)
  }

  const handleSubmitted = () => {
    setRefreshTrigger(n => n + 1)
    addToast('Incident submitted successfully!', 'success')
  }

  // ── AUTH GATE (Day 72) ────────────────────────────────
  // If no user is logged in, show login page instead of the dashboard
  if (!user) {
    return <LoginPage />
  }

  return (
    <div className="app-shell">

      {/* HEADER */}
      <header className="app-header">
        <div className="app-header-left">
          <span style={{ fontSize: 26 }}>🚨</span>
          <div>
            <div className="app-title">CivicLens Dispatch</div>
            <div className="app-subtitle">AI-Powered Incident Management</div>
          </div>
        </div>

        {/* ── VIEW TOGGLE (Day 70) ─────────────────────── */}
        {/* Swaps between the live dashboard and the analytics view */}
        <div className="view-toggle">
          <button
            className={`view-toggle__btn ${activeView === 'live' ? 'view-toggle__btn--active' : ''}`}
            onClick={() => setActiveView('live')}
          >
            🗂 Live Feed
          </button>
          <button
            className={`view-toggle__btn ${activeView === 'analytics' ? 'view-toggle__btn--active' : ''}`}
            onClick={() => setActiveView('analytics')}
          >
            📊 Analytics
          </button>
        </div>

        <div className="app-header-right">
          {/* ── LIVE INDICATOR (Day 71) ──────────────────
              Shows ● Live when WebSocket is connected,
              ○ Polling when falling back to 30-s poll */}
          <div className={`ws-indicator ${wsConnected ? 'ws-indicator--live' : 'ws-indicator--polling'}`}>
            <span className="ws-indicator__dot" />
            <span className="ws-indicator__label">
              {wsConnected ? 'Live' : 'Polling'}
            </span>
          </div>

          <AIStatusIndicator />
          <HealthCheck />

          {/* ── USER INFO + LOGOUT (Day 72) ──────────────── */}
          <div className="user-badge">
            <span className="user-badge__name">
              {user.username}
            </span>
            <span className={`user-badge__role user-badge__role--${user.role}`}>
              {user.role}
            </span>
            <button className="user-badge__logout" onClick={logout} title="Sign out">
              Sign out
            </button>
          </div>
        </div>
      </header>

      {/* BODY — conditionally renders live feed or analytics */}
      {activeView === 'analytics' ? (

        /* ── ANALYTICS VIEW (Day 70) ────────────────────── */
        <div className="app-body app-body--analytics">
          <AnalyticsView />
        </div>

      ) : (

        /* ── LIVE FEED (original dashboard layout) ──────── */
        <div className="app-body">

          {/* LEFT: incidents table + detail panel */}
          <div className="app-dashboard">
            {/* StatsBar re-fetches when refreshTrigger increments */}
            <StatsBar refreshTrigger={refreshTrigger} />
            <DashboardLayout>
              <IncidentsList
                onSelectIncident={handleSelect}
                selectedIncidentId={selectedIncident?.id}
                refreshTrigger={refreshTrigger}
                wsUpdate={wsUpdate}          // Latest WebSocket event (Day 71)
                wsConnected={wsConnected}    // Disables polling when WS is live
              />
              <IncidentDetail
                incident={selectedIncident}
                onClose={handleClose}
                onStatusChange={handleStatusChange}
                onDeleted={handleDeleted}    // Day 72: admin delete
                userRole={user.role}         // Day 72: hide delete for non-admin
              />
            </DashboardLayout>
          </div>

          {/* RIGHT: new incident form */}
          <div className="app-form-panel">
            <div className="app-form-panel-header">
              <div className="app-form-panel-title">📝 New Incident Report</div>
              <div className="app-form-panel-subtitle">Submit a new incident for dispatch</div>
            </div>
            <SubmitIncidentForm onSubmitted={handleSubmitted} />
          </div>

        </div>
      )}

      {/* FOOTER */}
      <footer className="app-footer">
        <p>CivicLens Dispatch — For life-threatening emergencies always call 911</p>
      </footer>

      <ToastContainer toasts={toasts} />
    </div>
  )
}

export default App
