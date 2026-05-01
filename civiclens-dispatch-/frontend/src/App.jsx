import { useState, useEffect } from 'react'
import { Activity, BarChart3, Plus, LogOut, Siren } from 'lucide-react'

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
    addToast('Incident submitted — dispatchers notified', 'success')
  }

  if (!user) return <LoginPage />

  return (
    <div className="flex flex-col h-screen bg-background overflow-hidden">

      {/* ── HEADER ── */}
      <header className="flex items-center h-14 px-6 border-b border-border bg-surface flex-shrink-0 gap-4">

        {/* Brand */}
        <div className="flex items-center gap-2.5 flex-shrink-0 min-w-0">
          <div className="w-7 h-7 rounded-lg bg-accent flex items-center justify-center flex-shrink-0">
            <Siren size={14} className="text-accent-fg" />
          </div>
          <span className="text-body font-semibold text-text-primary whitespace-nowrap">CivicLens Dispatch</span>
        </div>

        {/* View tabs — centered */}
        <div className="flex-1 flex justify-center">
          <Tabs tabs={VIEW_TABS} active={activeView} onChange={setActiveView} />
        </div>

        {/* Right: system status + user */}
        <div className="flex items-center gap-3 flex-shrink-0">

          {/* Status row — all items share the same dot+text style */}
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1.5">
              <StatusDot variant={wsConnected ? 'live' : 'idle'} size="sm" />
              <span className="text-caption text-text-muted">{wsConnected ? 'Live' : 'Polling'}</span>
            </span>
            <span className="w-px h-3 bg-border" />
            <AIStatusIndicator />
            <span className="w-px h-3 bg-border" />
            <HealthCheck />
          </div>

          <span className="w-px h-4 bg-border" />

          {/* User */}
          <span className="text-caption text-text-muted">{user.username}</span>

          <button
            onClick={logout}
            title="Sign out"
            className="p-1.5 rounded-lg text-text-muted hover:text-text-primary hover:bg-surface-2 transition-colors focus:outline-none"
          >
            <LogOut size={14} />
          </button>
        </div>
      </header>

      {/* ── BODY ── */}
      {activeView === 'analytics' ? (

        <div className="flex-1 overflow-auto p-6">
          <AnalyticsView />
        </div>

      ) : (

        <div className="flex-1 flex flex-col overflow-hidden p-6 gap-4">

          <StatsBar refreshTrigger={refreshTrigger} />

          <div className="flex-1 grid grid-cols-12 gap-4 overflow-hidden min-h-0">

            {/* Incidents list */}
            <div className="col-span-7 flex flex-col overflow-hidden min-h-0">
              <div className="flex items-center justify-between mb-3 flex-shrink-0">
                <h2 className="text-heading text-text-primary">Incidents</h2>
                <Button variant="primary" size="sm" icon={Plus} onClick={() => setFormOpen(true)}>
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

            {/* Detail panel */}
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

      {/* Slide-over form */}
      <SlideOver open={formOpen} onClose={() => setFormOpen(false)} title="New Incident Report">
        <SubmitIncidentForm onSubmitted={handleSubmitted} />
      </SlideOver>

      <ToastContainer toasts={toasts} removeToast={removeToast} />
    </div>
  )
}

export default App
