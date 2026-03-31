// frontend/src/components/dashboard/IncidentsList.jsx
//
// This is the "smart" container component for the left side of the dashboard.
// It is responsible for:
//   1. Fetching incidents from the backend API
//   2. Owning ALL state: incidents data, loading, error, sort, filter, selected incident
//   3. Rendering the filter bar (dropdowns to sort and filter)
//   4. Passing sorted/filtered data down to IncidentTable
//   5. Passing the selected incident up to the parent (App.jsx) so the detail panel opens
//
// "Smart" vs "Dumb" components:
//   Smart (this file)  = fetches data, owns state, has logic
//   Dumb (IncidentTable) = receives data as props, just renders it
//
// Day 36 changes:
//   - Added sortField, sortDirection, filterType state
//   - Added useMemo to compute sorted+filtered list efficiently
//   - Added filter bar UI above the table
//   - Added results count display

// React core: useState for state, useEffect for side effects, useMemo for caching
import { useState, useEffect, useMemo } from 'react'

// getIncidents fetches all incidents from the backend API
// It lives in api/client.js which handles the fetch() calls
import { getIncidents } from '../../api/client'

// IncidentTable renders the actual HTML table rows
// It receives sorted/filtered incidents as a prop
import IncidentTable from './IncidentTable'

// LoadingState shows a spinner or skeleton while data is loading
import LoadingState from '../shared/LoadingState'

// CSS styles for the filter bar and layout of this component
import './IncidentsList.css'

// ============================================================
// COMPONENT DEFINITION
// ============================================================
// Props this component receives from App.jsx:
//   onSelectIncident(incident) - called when dispatcher clicks a row
//                                App.jsx uses this to open the detail panel
//   selectedIncidentId         - the ID of the currently open incident
//                                used to highlight the selected row
const IncidentsList = ({ onSelectIncident, selectedIncidentId }) => {

  // ── DATA STATE ───────────────────────────────────────────
  // incidents: the raw array fetched from the API (never modified directly)
  const [incidents, setIncidents] = useState([])

  // loading: true while the API call is in flight
  const [loading, setLoading] = useState(true)

  // error: null normally, set to an error message string if fetch fails
  const [error, setError] = useState(null)

  // ── SORT STATE ───────────────────────────────────────────
  // sortField: which column to sort by
  // Options: 'created_at' | 'risk_score' | 'severity' | 'incident_type'
  // Default is 'created_at' so newest incidents appear first
  const [sortField, setSortField] = useState('created_at')

  // sortDirection: whether to sort ascending (low→high) or descending (high→low)
  // 'desc' default means newest first (most recent date at top)
  const [sortDirection, setSortDirection] = useState('desc')

  // ── FILTER STATE ─────────────────────────────────────────
  // filterType: which incident type to show
  // 'all' means show every incident regardless of type
  // Other values: 'fire' | 'medical' | 'police' | 'other'
  const [filterType, setFilterType] = useState('all')

  // ── DATA FETCHING ─────────────────────────────────────────
  // useEffect runs code AFTER the component renders
  // The empty array [] means "run this only once, when the component first mounts"
  // "Mounts" means when the component appears on the page for the first time
  useEffect(() => {
    // Define an async function inside useEffect
    // We can't make useEffect itself async, so we define a function and call it
    const fetchIncidents = async () => {
      try {
        // Set loading to true so the spinner appears
        setLoading(true)

        // Clear any previous error so stale error messages don't persist
        setError(null)

        // Call the API — this is an async operation that waits for the backend
        // getIncidents() is defined in api/client.js and uses fetch()
        const data = await getIncidents()

        // Store the fetched array in state
        // This triggers a re-render so the table shows the new data
        setIncidents(data)

      } catch (err) {
        // If anything goes wrong (network error, server error), set the error message
        // err.message is a human-readable description of what went wrong
        setError(err.message || 'Failed to fetch incidents')

      } finally {
        // 'finally' runs whether the try succeeded or the catch ran
        // Always set loading to false so the spinner disappears
        setLoading(false)
      }
    }

    // Call the function we just defined
    fetchIncidents()

  }, []) // Empty dependency array = run only on mount

  // ── SORT HANDLER ─────────────────────────────────────────
  // Called by IncidentTable when a column header is clicked
  // field: the column that was clicked ('risk_score', 'severity', etc.)
  const handleSort = (field) => {
    if (sortField === field) {
      // User clicked the SAME column that's already sorted
      // Flip the direction: 'asc' → 'desc', 'desc' → 'asc'
      setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc')
    } else {
      // User clicked a DIFFERENT column
      // Switch to that column and start with descending (high→low is usually more useful)
      setSortField(field)
      setSortDirection('desc')
    }
  }

  // ── COMPUTED: SORTED + FILTERED INCIDENTS ────────────────
  // useMemo caches the result of this computation.
  // It only recalculates when incidents, sortField, sortDirection, or filterType changes.
  // Without useMemo, this would run on EVERY re-render (even unrelated ones).
  const displayedIncidents = useMemo(() => {

    // STEP 1: Filter
    // Start with a copy of the full incidents array
    // We use .filter() to keep only incidents matching the selected type
    let result = incidents.filter(incident => {
      // If filterType is 'all', keep every incident (no filtering)
      if (filterType === 'all') return true

      // Otherwise, keep only incidents whose type matches filterType
      // We use optional chaining (?.) in case incident_type is null
      // toLowerCase() makes the comparison case-insensitive
      return incident.incident_type?.toLowerCase() === filterType
    })

    // STEP 2: Sort
    // .sort() takes a comparator function that compares two items (a and b)
    // We spread [...result] to sort a copy — never mutate the array directly in React
    result = [...result].sort((a, b) => {

      // Get the values we're comparing from each incident
      let valueA = a[sortField]
      let valueB = b[sortField]

      // Handle null/undefined values — push them to the bottom regardless of direction
      // This prevents errors when risk_score or incident_type is null
      if (valueA === null || valueA === undefined) return 1   // a goes after b
      if (valueB === null || valueB === undefined) return -1  // b goes after a

      // For string fields (incident_type, severity), use localeCompare
      // localeCompare handles alphabetical order correctly across languages
      if (typeof valueA === 'string') {
        // If ascending: a before b alphabetically
        // If descending: b before a alphabetically
        const comparison = valueA.localeCompare(valueB)
        return sortDirection === 'asc' ? comparison : -comparison
      }

      // For number/date fields (risk_score, created_at), subtract
      // Subtracting numbers gives the sign we need: negative (a first), positive (b first)
      // For dates: JavaScript can compare ISO date strings directly as numbers
      const comparison = valueA > valueB ? 1 : valueA < valueB ? -1 : 0
      return sortDirection === 'asc' ? comparison : -comparison
    })

    // Return the filtered and sorted array
    return result

  }, [incidents, sortField, sortDirection, filterType])
  // ↑ These are the dependencies — useMemo recalculates when any of these change

  // ── RENDER: LOADING STATE ────────────────────────────────
  // While the API call is in progress, show a loading indicator
  if (loading) {
    return (
      <div className="incidents-list">
        {/* LoadingState is a shared component that shows a spinner */}
        <LoadingState message="Loading incidents..." />
      </div>
    )
  }

  // ── RENDER: ERROR STATE ───────────────────────────────────
  // If the fetch failed, show the error and a retry button
  if (error) {
    return (
      <div className="incidents-list">
        <div className="incidents-error">
          {/* Error icon and message */}
          <p className="error-icon">⚠️</p>
          <p className="error-message">Failed to load incidents</p>
          <p className="error-detail">{error}</p>
          {/* Retry button reloads the page to trigger another fetch */}
          <button
            className="btn btn--primary"
            onClick={() => window.location.reload()}
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  // ── RENDER: MAIN VIEW ─────────────────────────────────────
  // We have data — render the filter bar and table
  return (
    // Outer wrapper for the entire left panel
    <div className="incidents-list">

      {/* ── FILTER BAR ─────────────────────────────────────── */}
      {/* The row of controls sitting above the table */}
      <div className="filter-bar">

        {/* LEFT SIDE: Filter and Sort dropdowns */}
        <div className="filter-bar__controls">

          {/* TYPE FILTER DROPDOWN */}
          {/* Lets dispatcher show only one type of incident */}
          <div className="filter-group">
            {/* Label is visually hidden but present for screen readers */}
            <label className="filter-label" htmlFor="type-filter">
              Type
            </label>
            {/* <select> is a native HTML dropdown */}
            {/* value={filterType} makes it a controlled component (React owns the value) */}
            {/* onChange updates filterType state when dispatcher picks an option */}
            <select
              id="type-filter"
              className="filter-select"
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
            >
              {/* Each <option> value must match what incident_type contains in the database */}
              <option value="all">All Types</option>
              <option value="fire">🔥 Fire</option>
              <option value="medical">🚑 Medical</option>
              <option value="police">🚔 Police</option>
              <option value="other">📋 Other</option>
            </select>
          </div>

          {/* SORT DROPDOWN */}
          {/* A convenience dropdown for common sort presets */}
          {/* This complements the clickable column headers */}
          <div className="filter-group">
            <label className="filter-label" htmlFor="sort-select">
              Sort By
            </label>
            <select
              id="sort-select"
              className="filter-select"
              // The value combines field and direction so one dropdown controls both
              // e.g., "risk_score_desc" means sort by risk_score descending
              value={`${sortField}_${sortDirection}`}
              onChange={(e) => {
                // Split the combined value back into field and direction
                // e.g., "risk_score_desc" → field="risk_score", direction="desc"
                // The last segment is always the direction (asc/desc)
                // Everything before it is the field name (handles underscores in field names)
                const parts = e.target.value.split('_')
                const direction = parts.pop()         // Remove and get the last part
                const field = parts.join('_')         // Rejoin the rest as the field name
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

        {/* RIGHT SIDE: Results count */}
        {/* Tells dispatcher how many incidents match the current filter */}
        <div className="filter-bar__count">
          {/* Show filtered count vs total count */}
          {/* e.g., "Showing 4 of 12 incidents" */}
          <span className="results-count">
            {filterType !== 'all'
              // If a filter is active, show "X of Y"
              ? `Showing ${displayedIncidents.length} of ${incidents.length} incidents`
              // If no filter, just show the total
              : `${incidents.length} incident${incidents.length !== 1 ? 's' : ''}`
            }
          </span>

          {/* Show a "Filtered" badge when a filter is active */}
          {filterType !== 'all' && (
            <span className="filter-active-badge">Filtered</span>
          )}
        </div>

      </div>
      {/* END: filter-bar */}

      {/* ── EMPTY STATE ────────────────────────────────────── */}
      {/* Show a helpful message when the filter returns no results */}
      {displayedIncidents.length === 0 && !loading && (
        <div className="incidents-empty">
          {filterType !== 'all'
            // If filtering is active and got nothing, offer to clear the filter
            ? (
              <>
                <p className="empty-icon">🔍</p>
                <p className="empty-message">
                  No {filterType} incidents found
                </p>
                {/* Clear filter button resets filterType to 'all' */}
                <button
                  className="btn btn--secondary btn--small"
                  onClick={() => setFilterType('all')}
                >
                  Clear Filter
                </button>
              </>
            )
            // If no filter active and still empty, the database is empty
            : (
              <>
                <p className="empty-icon">📋</p>
                <p className="empty-message">No incidents yet</p>
                <p className="empty-hint">
                  Submit an incident using the form below
                </p>
              </>
            )
          }
        </div>
      )}

      {/* ── INCIDENT TABLE ─────────────────────────────────── */}
      {/* Only render the table if there's something to show */}
      {displayedIncidents.length > 0 && (
        <IncidentTable
          // The sorted and filtered array — NOT the raw incidents
          incidents={displayedIncidents}

          // The currently selected incident ID (to highlight that row)
          selectedIncidentId={selectedIncidentId}

          // Called when dispatcher clicks a row
          // We pass it straight through from our own props
          onSelectIncident={onSelectIncident}

          // Current sort field — table uses this to show the sort arrow icon
          sortField={sortField}

          // Current sort direction — table uses this to show ↑ or ↓
          sortDirection={sortDirection}

          // Called when dispatcher clicks a column header
          // Table reports WHAT was clicked, parent decides HOW to sort
          onSort={handleSort}
        />
      )}

    </div>
  )
}

// Export so App.jsx can import and render this component
export default IncidentsList