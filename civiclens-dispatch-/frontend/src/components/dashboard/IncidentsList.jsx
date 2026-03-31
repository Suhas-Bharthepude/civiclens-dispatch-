// frontend/src/components/dashboard/IncidentsList.jsx
//
// The "smart" container component for the incidents table.
// Fetches incidents from the backend, owns sort/filter state,
// and now auto-refreshes every 30 seconds using useAutoRefresh.
//
// Day 38 changes:
//   - Integrated useAutoRefresh hook for 30-second polling
//   - Split loading into 'loading' (first load) and 'isRefreshing' (background)
//   - Added "last updated" timestamp display in the filter bar
//   - Added "Refresh Now" button for manual immediate refresh
//   - Added live status indicator (green dot when healthy, red when error)
//   - refreshTrigger from App.jsx still works alongside the interval

import { useState, useEffect, useMemo, useCallback } from 'react'

// getIncidents fetches all incidents from the backend API
import { getIncidents } from '../../api/client'

// IncidentTable renders the HTML table rows
import IncidentTable from './IncidentTable'

// LoadingState shows a spinner on first load
import LoadingState from '../shared/LoadingState'

// Our new custom hook that handles polling and last-updated tracking
import useAutoRefresh from '../../hooks/useAutoRefresh'

// CSS for the filter bar, empty state, and refresh indicator
import './IncidentsList.css'

// ============================================================
// HELPER: formatTimeAgo
// ============================================================
// Converts a Date object into a human-readable "X ago" string.
// Used to display "Last updated 14 seconds ago" in the filter bar.
//
// Examples:
//   formatTimeAgo(new Date())           → "just now"
//   formatTimeAgo(dateFrom14SecsAgo)    → "14 seconds ago"
//   formatTimeAgo(dateFrom3MinsAgo)     → "3 minutes ago"
function formatTimeAgo(date) {
  // If no date provided, return a placeholder
  if (!date) return 'never'

  // Calculate the difference in seconds between now and the given date
  const secondsAgo = Math.floor((Date.now() - date.getTime()) / 1000)

  // "just now" for very recent updates (within 5 seconds)
  if (secondsAgo < 5) return 'just now'

  // "X seconds ago" for updates within the last minute
  if (secondsAgo < 60) return `${secondsAgo}s ago`

  // "X minutes ago" for updates within the last hour
  const minutesAgo = Math.floor(secondsAgo / 60)
  if (minutesAgo < 60) return `${minutesAgo}m ago`

  // "X hours ago" for very stale data
  const hoursAgo = Math.floor(minutesAgo / 60)
  return `${hoursAgo}h ago`
}

// ============================================================
// COMPONENT
// ============================================================
// Props from App.jsx:
//   onSelectIncident(incident) - tells App.jsx which row was clicked
//   selectedIncidentId         - ID of currently open incident (for row highlight)
//   refreshTrigger             - number that App.jsx increments to force a refresh
//                                (used after form submit or status change)
const IncidentsList = ({ onSelectIncident, selectedIncidentId, refreshTrigger }) => {

  // ── DATA STATE ───────────────────────────────────────
  // The raw array of incidents from the API — never sorted/filtered in place
  const [incidents, setIncidents] = useState([])

  // loading: true only during the FIRST fetch (shows full spinner)
  // After the first load, background refreshes use isRefreshing instead
  const [loading, setLoading] = useState(true)

  // error: null normally, set to an error message if the FIRST fetch fails
  const [error, setError] = useState(null)

  // ── SORT STATE ───────────────────────────────────────
  // Which field to sort by and in which direction
  const [sortField,     setSortField]     = useState('created_at')
  const [sortDirection, setSortDirection] = useState('desc')

  // ── FILTER STATE ─────────────────────────────────────
  // Which incident type to show ('all' = no filter)
  const [filterType, setFilterType] = useState('all')

  // ── DISPLAY TIMER STATE ──────────────────────────────
  // This counter increments every second to make the "14 seconds ago"
  // text update live. It doesn't hold any real data — just triggers re-renders.
  const [, setSecondsTick] = useState(0)

  // ── FETCH FUNCTION ───────────────────────────────────
  // We wrap fetchIncidents in useCallback so it has a stable identity.
  // This is important because we pass it to useAutoRefresh — if the function
  // was recreated on every render, the hook would restart the interval constantly.
  //
  // isFirstLoad: if true, show the full spinner; if false, it's a background poll
  const fetchIncidents = useCallback(async (isFirstLoad = false) => {
    try {
      // On first load, show the full loading spinner
      if (isFirstLoad) {
        setLoading(true)
        setError(null)
      }

      // Fetch all incidents from the backend API
      const data = await getIncidents()

      // Update the incidents array in state
      setIncidents(data)

      // Clear any first-load error (we got data successfully)
      setError(null)

    } catch (err) {
      // Only show the big error UI on first load failures
      // Background refresh failures are handled by useAutoRefresh's refreshError
      if (isFirstLoad) {
        setError(err.message || 'Failed to fetch incidents')
      }
      // Re-throw so useAutoRefresh can catch it and set refreshError
      throw err

    } finally {
      // Always clear the full loading spinner
      setLoading(false)
    }
  }, []) // No dependencies — this function doesn't use any component state

  // ── FIRST LOAD ────────────────────────────────────────
  // Run once when the component mounts to do the initial data fetch
  useEffect(() => {
    fetchIncidents(true) // true = first load = show full spinner
  }, [fetchIncidents])

  // ── REFRESH TRIGGER ───────────────────────────────────
  // When App.jsx increments refreshTrigger (after form submit or status change),
  // re-fetch the data. Skip the very first render (refreshTrigger starts at 0).
  useEffect(() => {
    // refreshTrigger === 0 is the initial value — don't fetch on mount
    // (the first load useEffect above handles that)
    if (refreshTrigger > 0) {
      fetchIncidents(false) // false = not first load = no full spinner
    }
  }, [refreshTrigger, fetchIncidents])

  // ── AUTO REFRESH ──────────────────────────────────────
  // Connect our fetchIncidents function to the polling hook.
  // The hook will call fetchIncidents every 30 seconds automatically.
  // It also gives us isRefreshing, lastUpdated, and triggerRefresh.
  const {
    isRefreshing,    // true while a background poll is in progress
    lastUpdated,     // Date of last successful refresh
    refreshError,    // error message if last background refresh failed
    triggerRefresh,  // function to call for immediate manual refresh
  } = useAutoRefresh(
    fetchIncidents,  // the function to call on each poll
    30000,           // poll every 30 seconds (30,000 milliseconds)
    !loading         // only start polling AFTER the first load is complete
    // This prevents the interval from firing while we're still on the loading screen
  )

  // ── LIVE TIMESTAMP UPDATER ────────────────────────────
  // This effect sets up a 1-second interval that just increments a counter.
  // The counter itself isn't used for anything — incrementing it just causes
  // a re-render, which recalculates formatTimeAgo(lastUpdated) with the
  // current time, making the "14 seconds ago" text count up live.
  useEffect(() => {
    const tickId = setInterval(() => {
      // Increment the counter — this triggers a re-render
      setSecondsTick(n => n + 1)
    }, 1000) // every 1 second

    // Clean up this interval too when the component unmounts
    return () => clearInterval(tickId)
  }, []) // Empty array = set up once on mount

  // ── SORT HANDLER ─────────────────────────────────────
  // Called by IncidentTable when a column header is clicked
  const handleSort = (field) => {
    if (sortField === field) {
      // Same column — flip direction
      setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc')
    } else {
      // New column — sort descending by default
      setSortField(field)
      setSortDirection('desc')
    }
  }

  // ── COMPUTED: SORTED + FILTERED LIST ─────────────────
  // useMemo caches this result and only recalculates when its
  // dependencies change (not on every render)
  const displayedIncidents = useMemo(() => {

    // Step 1: Filter by incident type
    let result = incidents.filter(incident => {
      if (filterType === 'all') return true
      return incident.incident_type?.toLowerCase() === filterType
    })

    // Step 2: Sort a copy (never mutate state directly)
    result = [...result].sort((a, b) => {
      let valA = a[sortField]
      let valB = b[sortField]

      // Push null values to the bottom regardless of sort direction
      if (valA == null) return 1
      if (valB == null) return -1

      // String comparison uses localeCompare for correct alphabetical order
      if (typeof valA === 'string') {
        const cmp = valA.localeCompare(valB)
        return sortDirection === 'asc' ? cmp : -cmp
      }

      // Number/date comparison
      const cmp = valA > valB ? 1 : valA < valB ? -1 : 0
      return sortDirection === 'asc' ? cmp : -cmp
    })

    return result

  }, [incidents, sortField, sortDirection, filterType])

  // ── RENDER: FIRST LOAD SPINNER ────────────────────────
  if (loading) {
    return (
      <div className="incidents-list">
        <LoadingState message="Loading incidents..." />
      </div>
    )
  }

  // ── RENDER: FIRST LOAD ERROR ──────────────────────────
  if (error) {
    return (
      <div className="incidents-list">
        <div className="incidents-error">
          <p className="error-icon">⚠️</p>
          <p className="error-message">Failed to load incidents</p>
          <p className="error-detail">{error}</p>
          <button
            className="btn btn--primary"
            onClick={() => fetchIncidents(true)}
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  // ── RENDER: MAIN VIEW ─────────────────────────────────
  return (
    <div className="incidents-list">

      {/* ── FILTER BAR ───────────────────────────────── */}
      <div className="filter-bar">

        {/* LEFT: filter and sort dropdowns */}
        <div className="filter-bar__controls">

          {/* Type filter */}
          <div className="filter-group">
            <label className="filter-label" htmlFor="type-filter">Type</label>
            <select
              id="type-filter"
              className="filter-select"
              value={filterType}
              onChange={e => setFilterType(e.target.value)}
            >
              <option value="all">All Types</option>
              <option value="fire">🔥 Fire</option>
              <option value="medical">🚑 Medical</option>
              <option value="police">🚔 Police</option>
              <option value="crime">🚨 Crime</option>
              <option value="infrastructure">🏗️ Infrastructure</option>
              <option value="other">📋 Other</option>
            </select>
          </div>

          {/* Sort dropdown */}
          <div className="filter-group">
            <label className="filter-label" htmlFor="sort-select">Sort By</label>
            <select
              id="sort-select"
              className="filter-select"
              value={`${sortField}_${sortDirection}`}
              onChange={e => {
                // The value is "fieldName_direction" e.g. "risk_score_desc"
                // Split from the right to handle field names with underscores
                const parts = e.target.value.split('_')
                const direction = parts.pop()       // last part = direction
                const field = parts.join('_')       // rest = field name
                setSortField(field)
                setSortDirection(direction)
              }}
            >
              <option value="created_at_desc">🕐 Newest First</option>
              <option value="created_at_asc">🕐 Oldest First</option>
              <option value="risk_score_desc">🔴 Highest Risk</option>
              <option value="risk_score_asc">🟢 Lowest Risk</option>
              <option value="severity_desc">⚠️ Severity (High→Low)</option>
              <option value="incident_type_asc">📋 Type (A→Z)</option>
            </select>
          </div>

        </div>

        {/* RIGHT: results count + live refresh indicator */}
        <div className="filter-bar__right">

          {/* Results count */}
          <span className="results-count">
            {filterType !== 'all'
              ? `Showing ${displayedIncidents.length} of ${incidents.length}`
              : `${incidents.length} incident${incidents.length !== 1 ? 's' : ''}`
            }
          </span>

          {/* Filtered badge */}
          {filterType !== 'all' && (
            <span className="filter-active-badge">Filtered</span>
          )}

          {/* ── LIVE REFRESH INDICATOR ─────────────── */}
          {/* Shows current refresh status and last update time */}
          <div className="refresh-indicator">

            {/* Background refresh error — show red dot and retry */}
            {refreshError && !isRefreshing && (
              <div className="refresh-status refresh-status--error">
                {/* Red dot */}
                <span className="refresh-dot refresh-dot--error" />
                <span className="refresh-text">Refresh failed</span>
                {/* Retry button triggers an immediate manual refresh */}
                <button
                  className="refresh-retry-btn"
                  onClick={triggerRefresh}
                >
                  Retry
                </button>
              </div>
            )}

            {/* Currently refreshing in background */}
            {isRefreshing && (
              <div className="refresh-status refresh-status--updating">
                {/* Spinning dot */}
                <span className="refresh-dot refresh-dot--spinning" />
                <span className="refresh-text">Updating...</span>
              </div>
            )}

            {/* Idle — show last updated time */}
            {!isRefreshing && !refreshError && (
              <div className="refresh-status refresh-status--idle">
                {/* Green dot — system is healthy */}
                <span className="refresh-dot refresh-dot--live" />
                <span className="refresh-text">
                  {/* Show "Live" label and last updated time */}
                  Live
                  {lastUpdated && (
                    // Separator dot + time ago string
                    <span className="refresh-time">
                      {' · '}{formatTimeAgo(lastUpdated)}
                    </span>
                  )}
                </span>
                {/* Manual refresh button */}
                <button
                  className="refresh-now-btn"
                  onClick={triggerRefresh}
                  title="Refresh now"
                >
                  {/* Refresh icon — a simple circular arrow */}
                  ↻
                </button>
              </div>
            )}

          </div>
          {/* END: refresh-indicator */}

        </div>
        {/* END: filter-bar__right */}

      </div>
      {/* END: filter-bar */}

      {/* ── EMPTY STATE ──────────────────────────────── */}
      {displayedIncidents.length === 0 && (
        <div className="incidents-empty">
          {filterType !== 'all' ? (
            <>
              <p className="empty-icon">🔍</p>
              <p className="empty-message">No {filterType} incidents found</p>
              <button
                className="btn btn--secondary btn--small"
                onClick={() => setFilterType('all')}
              >
                Clear Filter
              </button>
            </>
          ) : (
            <>
              <p className="empty-icon">📋</p>
              <p className="empty-message">No incidents yet</p>
              <p className="empty-hint">Submit an incident using the form</p>
            </>
          )}
        </div>
      )}

      {/* ── INCIDENT TABLE ───────────────────────────── */}
      {displayedIncidents.length > 0 && (
        <IncidentTable
          incidents={displayedIncidents}
          selectedIncidentId={selectedIncidentId}
          onSelectIncident={onSelectIncident}
          sortField={sortField}
          sortDirection={sortDirection}
          onSort={handleSort}
        />
      )}

    </div>
  )
}

export default IncidentsList