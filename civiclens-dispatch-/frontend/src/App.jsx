import { useState, useEffect } from 'react'
import { Activity, BarChart3, Plus, LogOut, User, Siren } from 'lucide-react'

import useToast          from './hooks/useToast'
import useIncidentStream from './hooks/useIncidentStream'

import HealthCheck        from './components/dashboard/HealthCheck'
import IncidentsList      from './components/dashboard/IncidentsList'
import IncidentDetail     from './components/dashboard/IncidentDetail'
import SubmitIncidentForm from './components/forms/SubmitIncidentForm'
import ToastContainer     from './components/shared/ToastContainer'
import StatsBar           from './components/dashboard/StatsBar'
import AIStatusIndicator  from './components/dashboard/AIStatusIndicator'
import AnalyticsView      from './components/analytics/AnalyticsView'
import { Tabs }           from './components/ui/Tabs'
import { SlideOver }      from './components/ui/SlideOver'
import { Button }         from './components/ui/Button'
import { StatusDot }      from './components/ui/StatusDot'
import { useAuth }        from './context/AuthContext'
import LoginPage          from './pages/LoginPage'


const VIEW_TABS = [
  { id: 'live',      label: 'Live Feed',  icon: Activity  },
  { id: 'analytics', label: 'Analytics',  icon: BarChart3 },
]

function App() {
  const [selectedIncident, setSelectedIncident] = useState(null)
  const [refreshTrigger,   setRefreshTrigger]   = useState(0)
  const [activeView,       setActiveView]       = useState('live')
  const [wsUpdate,         setWsUpdate]         = useState(null)
  const [formOpen,         setFormOpen]         = useState(false)

  const { toasts, showToast: addToast, removeToast } = useToast()
  const { user, logout } = useAuth()

  const { connected: wsConnected } = useIncidentStream((event) => {
    setWsUpdate(event)
  })

  useEffect(() => {
    const onKey = (e) => {
      if (e.key === 'Escape' && selectedIncident) setSelectedIncident(null)
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [selectedIncident])

  useEffect(() => {
    document.title = activeView === 'analytics'
      ? 'Analytics — CivicLens Dispatch'
      : 'Live Feed — CivicLens Dispatch'
  }, [activeView])

  const handleSelect      = (inc) => setSelectedIncident(inc)
  const handleClose       = ()    => setSelectedIncident(null)

  const handleStatusChange = (id, newStatus) => {
    setSelectedIncident(prev =>
      prev && prev.id === id ? { ...prev, status: newStatus } : prev
    )
    setRefreshTrigger(n => n + 1)
  }

  const handleDeleted = () => {
    setSelectedIncident(null)
    setRefreshTrigger(n => n + 1)
  }

  const handleSubmitted = () => {
    setFormOpen(false)
    setRefreshTrigger(n => n + 1)
    addToast('Incident submitted successfully!', 'success')
  }

  if (!user) return <LoginPage />

  return (
    <div className="flex flex-col h-screen bg-background overflow-hidden">

      {/* ── HEADER ─────────────────────────────────────────── */}
      <header className="flex items-center gap-4 px-6 py-3 border-b border-border bg-surface flex-shrink-0">

        {/* Brand */}
        <div className="flex items-center gap-3 min-w-0">
          <div className="w-8 h-8 rounded-lg bg-accent flex items-center justify-center flex-shrink-0">
            <Siren size={16} className="text-accent-fg" />
          </div>
          <div className="min-w-0">
            <div className="text-heading text-text-primary leading-none">CivicLens Dispatch</div>
            <div className="text-caption text-text-muted mt-0.5">AI-Powered Incident Management</div>
          </div>
        </div>

        {/* View tabs — centered */}
        <div className="flex-1 flex justify-center">
          <Tabs tabs={VIEW_TABS} active={activeView} onChange={setActiveView} />
        </div>

        {/* System status + user */}
        <div className="flex items-center gap-3 flex-shrink-0">

          {/* WS / Polling indicator */}
          <div className="flex items-center gap-1.5">
            <StatusDot variant={wsConnected ? 'live' : 'idle'} />
            <span className="text-caption text-text-muted">
              {wsConnected ? 'Live' : 'Polling'}
            </span>
          </div>

          <div className="w-px h-4 bg-border" />

          <AIStatusIndicator />
          <HealthCheck />

          <div className="w-px h-4 bg-border" />

          {/* User badge */}
          <div className="flex items-center gap-2">
            <User size={14} className="text-text-muted" />
            <span className="text-body text-text-secondary">{user.username}</span>
            <span className="text-label text-text-muted uppercase tracking-widest">{user.role}</span>
          </div>

          <button
            onClick={logout}
            className="flex items-center gap-1.5 px-2 py-1.5 rounded-lg text-caption text-text-muted hover:text-text-primary hover:bg-surface-2 transition-colors"
            title="Sign out"
          >
            <LogOut size={13} />
            Sign out
          </button>
        </div>
      </header>

      {/* ── BODY ───────────────────────────────────────────── */}
      {activeView === 'analytics' ? (

        <div className="flex-1 overflow-auto p-6">
          <AnalyticsView />
        </div>

      ) : (

        <div className="flex-1 flex flex-col overflow-hidden p-6 gap-4">

          {/* Stats row */}
          <StatsBar refreshTrigger={refreshTrigger} />

          {/* Main split: 7 cols incidents / 5 cols detail */}
          <div className="flex-1 grid grid-cols-12 gap-4 overflow-hidden min-h-0">

            {/* Incidents column */}
            <div className="col-span-7 flex flex-col overflow-hidden min-h-0">
              <div className="flex items-center justify-between mb-3 flex-shrink-0">
                <h2 className="text-heading text-text-primary">Incidents</h2>
                <Button
                  variant="primary"
                  size="sm"
                  icon={Plus}
                  onClick={() => setFormOpen(true)}
                >
                  New Incident
                </Button>
              </div>
              <div className="flex-1 overflow-hidden min-h-0">
                <IncidentsList
                  onSelectIncident={handleSelect}
                  selectedIncidentId={selectedIncident?.id}
                  refreshTrigger={refreshTrigger}
                  wsUpdate={wsUpdate}
                  wsConnected={wsConnected}
                />
              </div>
            </div>

            {/* Detail panel column */}
            <div className="col-span-5 overflow-hidden min-h-0">
              <IncidentDetail
                incident={selectedIncident}
                onClose={handleClose}
                onStatusChange={handleStatusChange}
                onDeleted={handleDeleted}
                userRole={user.role}
                showToast={addToast}
              />
            </div>

          </div>
        </div>
      )}

      {/* ── NEW INCIDENT SLIDE-OVER ────────────────────────── */}
      <SlideOver
        open={formOpen}
        onClose={() => setFormOpen(false)}
        title="New Incident Report"
      >
        <SubmitIncidentForm onSubmitted={handleSubmitted} />
      </SlideOver>

      <ToastContainer toasts={toasts} removeToast={removeToast} />
    </div>
  )
}

export default App
