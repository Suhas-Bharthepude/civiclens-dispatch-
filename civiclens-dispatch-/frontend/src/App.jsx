// frontend/src/App.jsx
import { useState, useEffect } from 'react'
import './App.css'
import useToast           from './hooks/useToast'
import HealthCheck        from './components/dashboard/HealthCheck'
import IncidentsList      from './components/dashboard/IncidentsList'
import IncidentDetail     from './components/dashboard/IncidentDetail'
import SubmitIncidentForm from './components/forms/SubmitIncidentForm'
import DashboardLayout    from './components/layout/DashboardLayout'
import ToastContainer     from './components/shared/ToastContainer'

function App() {
  const [selectedIncident, setSelectedIncident] = useState(null)
  const [refreshTrigger,   setRefreshTrigger]   = useState(0)
  const { toasts, addToast } = useToast()

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
  // id: the incident's database ID
  // newStatus: 'pending' | 'active' | 'resolved'
  // We do two things:
  //   1. Update selectedIncident in memory so the detail panel reflects
  //      the new status badge immediately (optimistic update)
  //   2. Increment refreshTrigger so IncidentsList re-fetches the table,
  //      updating the status badge in the table row too
  const handleStatusChange = (id, newStatus) => {
    // Update the selected incident's status in local state
    // so the detail panel re-renders with the new status badge instantly
    setSelectedIncident(prev =>
      prev && prev.id === id
        ? { ...prev, status: newStatus }  // spread copies all fields, overrides status
        : prev                            // different incident, no change
    )
    // Trigger a table refresh so the row's status badge updates too
    setRefreshTrigger(n => n + 1)
  }

  const handleSubmitted = ()    => {
    setRefreshTrigger(n => n + 1)
    addToast('Incident submitted successfully!', 'success')
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
        <div className="app-header-right">
          <HealthCheck />
        </div>
      </header>

      {/* BODY */}
      <div className="app-body">

        {/* LEFT: incidents table + detail panel */}
        <div className="app-dashboard">
          <DashboardLayout>
            <IncidentsList
              onSelectIncident={handleSelect}
              selectedIncidentId={selectedIncident?.id}
              refreshTrigger={refreshTrigger}
            />
            <IncidentDetail
              incident={selectedIncident}
              onClose={handleClose}
              onStatusChange={handleStatusChange}
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

      {/* FOOTER */}
      <footer className="app-footer">
        <p>CivicLens Dispatch — For life-threatening emergencies always call 911</p>
      </footer>

      <ToastContainer toasts={toasts} />
    </div>
  )
}

export default App