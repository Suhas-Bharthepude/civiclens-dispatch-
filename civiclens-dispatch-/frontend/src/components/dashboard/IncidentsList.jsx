// frontend/src/components/dashboard/IncidentsList.jsx
//
// The "smart" container for the incidents table.
// Owns all state: incidents data, sort, filter, search, selected incident.
//
// Day 44 changes:
//   - Added searchTerm state for the search input
//   - Added useDebounce to delay API calls until user stops typing
//   - Updated fetchIncidents to pass search term to the backend API
//   - Added search input to the filter bar UI
//   - Added "Searching: X" badge when search is active
//   - Backend search covers description, location, transcript, summary
//
// The search is done on the BACKEND (not client-side) so it searches
// ALL incidents in the database, not just the ones currently loaded.

// React hooks
import { useState, useEffect, useMemo, useCallback } from 'react'

// getIncidents accepts { search: "term" } in its filters object
// It converts this to ?search=term in the URL query string
import { getIncidents } from '../../api/client'

// Table display component
import IncidentTable from './IncidentTable'

// Loading spinner for first load
import LoadingState from '../shared/LoadingState'

// Auto-refresh hook — polls every 30 seconds
import useAutoRefresh from '../../hooks/useAutoRefresh'

// Debounce hook — delays search until user stops typing
// This prevents an API call on every single keystroke
import useDebounce from '../../hooks/useDebounce'

// CSS for the filter bar and layout
import './IncidentsList.css'


// ============================================================
// COMPONENT
// ============================================================
// Props from App.jsx:
//   onSelectIncident(incident) - called when dispatcher clicks a row
//   selectedIncidentId         - ID of currently selected incident
//   refreshTrigger             - incremented by App.jsx after changes
const IncidentsList = ({ onSelectIncident, selectedIncidentId, refreshTrigger }) => {

  // ── DATA STATE ───────────────────────────────────────
  const [incidents,    setIncidents]    = useState([])
  const [loading,      setLoading]      = useState(true)
  const [error,        setError]        = useState(null)

  // ── SORT STATE ───────────────────────────────────────
  const [sortField,     setSortField]     = useState('created_at')
  const [sortDirection, setSortDirection] = useState('desc')

  // ── FILTER STATE ─────────────────────────────────────
  // filterType: which incident type to show ('all' or 'fire', 'medical', etc.)
  const [filterType, setFilterType] = useState('all')

  // ── SEARCH STATE ─────────────────────────────────────
  // searchTerm: the raw value of the search input — updates on every keystroke
  // This is what the user sees typed in the box
  const [searchTerm, setSearchTerm] = useState('')

  // debouncedSearch: delayed version of searchTerm
  // Only updates 400ms after the user stops typing
  // This is what we send to the API — prevents a request on every keystroke
  const debouncedSearch = useDebounce(searchTerm, 400)

  // ── DISPLAY TICKER (for "X seconds ago" in refresh indicator) ────
  const [, setSecondsTick] = useState(0)

  // ── FETCH FUNCTION ────────────────────────────────────
  // Wrapped in useCallback so it has a stable reference for useAutoRefresh
  const fetchIncidents = useCallback(async (isFirstLoad = false) => {
    try {
      if (isFirstLoad) {
        setLoading(true)
        setError(null)
      }

      // Build the filters object to send to the API
      // Include search term if one is active
      const filters = {}

      // Only add search to filters if there's actually something to search
      // An empty string would send ?search= which is unnecessary
      if (debouncedSearch.trim()) {
        filters.search = debouncedSearch.trim()
      }

      // Call the API with filters
      // getIncidents converts { search: "oak" } to ?search=oak in the URL
      const data = await getIncidents(filters)

      setIncidents(data)
      setError(null)

    } catch (err) {
      if (isFirstLoad) {
        setError(err.message || 'Failed to fetch incidents')
      }
      throw err
    } finally {
      setLoading(false)
    }
  }, [debouncedSearch])
  // ^ debouncedSearch is a dependency — if search changes, fetchIncidents
  //   returns a new function that uses the new search term

  // ── FIRST LOAD ────────────────────────────────────────
  // Fetch incidents once when the component first appears on screen
  useEffect(() => {
    fetchIncidents(true)
  }, [fetchIncidents])
  // ^ fetchIncidents changes when debouncedSearch changes, which triggers
  //   a new fetch automatically — this is how search re-fetches work!

  // ── REFRESH TRIGGER ───────────────────────────────────
  // Re-fetch when App.jsx increments refreshTrigger (after form submit etc.)
  useEffect(() => {
    if (refreshTrigger > 0) {
      fetchIncidents(false)
    }
  }, [refreshTrigger, fetchIncidents])

  // ── AUTO REFRESH ──────────────────────────────────────
  // Poll every 30 seconds for new incidents
  const {
    isRefreshing,
    lastUpdated,
    refreshError,
    triggerRefresh,
  } = useAutoRefresh(fetchIncidents, 30000, !loading)

  // ── LIVE TIMESTAMP UPDATER ────────────────────────────
  // Increments a counter every second to make "14 seconds ago" count up live
  useEffect(() => {
    const tickId = setInterval(() => setSecondsTick(n => n + 1), 1000)
    return () => clearInterval(tickId)
  }, [])

  // ── FORMAT "TIME AGO" ─────────────────────────────────
  // Converts a Date object to "just now", "14s ago", "3m ago"
  const formatTimeAgo = (date) => {
    if (!date) return 'never'
    const secs = Math.floor((Date.now() - date.getTime()) / 1000)
    if (secs < 5)  return 'just now'
    if (secs < 60) return `${secs}s ago`
    const mins = Math.floor(secs / 60)
    if (mins < 60) return `${mins}m ago`
    return `${Math.floor(mins / 60)}h ago`
  }

  // ── SORT HANDLER ─────────────────────────────────────
  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('desc')
    }
  }

  // ── COMPUTED: CLIENT-SIDE TYPE FILTER + SORT ─────────
  // NOTE: Search is done on the BACKEND (API returns pre-filtered results).
  // Type filtering and sorting are still done client-side here because
  // they're fast and don't require extra API calls.
  const displayedIncidents = useMemo(() => {
    // Filter by type (client-side — the backend already handled search)
    let result = incidents.filter(incident => {
      if (filterType === 'all') return true
      return incident.incident_type?.toLowerCase() === filterType
    })

    // Sort (client-side)
    result = [...result].sort((a, b) => {
      let valA = a[sortField]
      let valB = b[sortField]
      if (valA == null) return 1
      if (valB == null) return -1
      if (typeof valA === 'string') {
        const cmp = valA.localeCompare(valB)
        return sortDirection === 'asc' ? cmp : -cmp
      }
      const cmp = valA > valB ? 1 : valA < valB ? -1 : 0
      return sortDirection === 'asc' ? cmp : -cmp
    })

    return result
  }, [incidents, sortField, sortDirection, filterType])

  // ── RENDER: LOADING ───────────────────────────────────
  if (loading) {
    return (
      <div className="incidents-list">
        <LoadingState message="Loading incidents..." />
      </div>
    )
  }

  // ── RENDER: ERROR ─────────────────────────────────────
  if (error) {
    return (
      <div className="incidents-list">
        <div className="incidents-error">
          <p className="error-icon">⚠️</p>
          <p className="error-message">Failed to load incidents</p>
          <p className="error-detail">{error}</p>
          <button className="btn btn--primary" onClick={() => fetchIncidents(true)}>
            Retry
          </button>
        </div>
      </div>
    )
  }

  // ── RENDER: MAIN VIEW ─────────────────────────────────
  return (
    <div className="incidents-list">

      {/* ── FILTER BAR ─────────────────────────────────── */}
      <div className="filter-bar">

        {/* LEFT: dropdowns + search input */}
        <div className="filter-bar__controls">

          {/* Type filter dropdown */}
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
                const parts = e.target.value.split('_')
                const direction = parts.pop()
                const field = parts.join('_')
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

          {/* ── SEARCH INPUT ── NEW DAY 44 ─────────────── */}
          {/* Text box where dispatcher types a search term */}
          <div className="filter-group search-group">
            {/* Screen-reader label (visually hidden via CSS) */}
            <label className="filter-label sr-only" htmlFor="search-input">
              Search
            </label>
            {/* The search icon prefix */}
            <div className="search-input-wrapper">
              {/* Search icon — purely decorative */}
              <span className="search-icon" aria-hidden="true">🔍</span>
              <input
                id="search-input"
                type="text"
                className="search-input"
                // Placeholder text shown when box is empty
                placeholder="Search incidents..."
                // value is controlled by searchTerm state
                // React owns the input value
                value={searchTerm}
                // Update searchTerm on every keystroke
                // useDebounce handles the delay — this just keeps React in sync
                onChange={e => setSearchTerm(e.target.value)}
                // Allow pressing Escape to clear the search
                onKeyDown={e => {
                  if (e.key === 'Escape') setSearchTerm('')
                }}
                // Accessibility: describe what the field searches
                aria-label="Search incidents by description, location, or transcript"
              />
              {/* Clear button — only visible when there's text in the box */}
              {searchTerm && (
                <button
                  className="search-clear-btn"
                  onClick={() => setSearchTerm('')}
                  // Aria label for screen readers
                  aria-label="Clear search"
                  title="Clear search"
                >
                  ✕
                </button>
              )}
            </div>
          </div>

        </div>

        {/* RIGHT: results count + refresh indicator */}
        <div className="filter-bar__right">

          {/* Results count */}
          <span className="results-count">
            {/* Show different text depending on active filters */}
            {debouncedSearch || filterType !== 'all'
              ? `${displayedIncidents.length} of ${incidents.length}`
              : `${incidents.length} incident${incidents.length !== 1 ? 's' : ''}`
            }
          </span>

          {/* "Filtered" badge — shown when type filter is active */}
          {filterType !== 'all' && (
            <span className="filter-active-badge">Filtered</span>
          )}

          {/* "Searching: X" badge — shown when search is active */}
          {/* debouncedSearch (not searchTerm) so it only shows after the delay */}
          {debouncedSearch && (
            <span className="search-active-badge">
              {/* Show a truncated version of the search term */}
              🔍 {debouncedSearch.length > 15
                ? debouncedSearch.slice(0, 15) + '...'
                : debouncedSearch
              }
            </span>
          )}

          {/* Refresh indicator (same as before) */}
          <div className="refresh-indicator">
            {refreshError && !isRefreshing && (
              <div className="refresh-status refresh-status--error">
                <span className="refresh-dot refresh-dot--error" />
                <span className="refresh-text">Refresh failed</span>
                <button className="refresh-retry-btn" onClick={triggerRefresh}>Retry</button>
              </div>
            )}
            {isRefreshing && (
              <div className="refresh-status refresh-status--updating">
                <span className="refresh-dot refresh-dot--spinning" />
                <span className="refresh-text">Updating...</span>
              </div>
            )}
            {!isRefreshing && !refreshError && (
              <div className="refresh-status refresh-status--idle">
                <span className="refresh-dot refresh-dot--live" />
                <span className="refresh-text">
                  Live
                  {lastUpdated && (
                    <span className="refresh-time">{' · '}{formatTimeAgo(lastUpdated)}</span>
                  )}
                </span>
                <button className="refresh-now-btn" onClick={triggerRefresh} title="Refresh now">↻</button>
              </div>
            )}
          </div>

        </div>

      </div>
      {/* END filter-bar */}

      {/* ── EMPTY STATE ──────────────────────────────────── */}
      {displayedIncidents.length === 0 && (
        <div className="incidents-empty">
          {debouncedSearch ? (
            // Search returned no results
            <>
              <p className="empty-icon">🔍</p>
              <p className="empty-message">No incidents found for "{debouncedSearch}"</p>
              <p className="empty-hint">Try different keywords or clear the search</p>
              <button
                className="btn btn--secondary btn--small"
                onClick={() => setSearchTerm('')}
              >
                Clear Search
              </button>
            </>
          ) : filterType !== 'all' ? (
            // Type filter returned no results
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
            // Database is empty
            <>
              <p className="empty-icon">📋</p>
              <p className="empty-message">No incidents yet</p>
              <p className="empty-hint">Submit an incident using the form</p>
            </>
          )}
        </div>
      )}

      {/* ── INCIDENT TABLE ───────────────────────────────── */}
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