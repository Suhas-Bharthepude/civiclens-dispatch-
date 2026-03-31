// frontend/src/components/dashboard/IncidentTable.jsx
//
// This is the "dumb" display component for the incidents table.
// It receives already-sorted and already-filtered data as props.
// It does NOT fetch data, sort data, or filter data itself.
//
// "Dumb" component responsibilities:
//   - Render a proper HTML table from the incidents array
//   - Show sortable column headers with direction arrows
//   - Highlight high-risk rows with a red tint
//   - Highlight the currently selected row
//   - Call onSelectIncident() when a row is clicked
//   - Call onSort() when a header is clicked
//
// Day 36 changes:
//   - Added sortable column headers (click to sort)
//   - Added sort direction arrows (↑ / ↓)
//   - Added high-risk row highlighting (risk_score > 0.7)
//   - Added selected row highlighting
//   - Receives sortField, sortDirection, onSort as new props

// Import React (required for JSX)
import React from 'react'

// CSS styles for the table — colors, spacing, hover effects, row highlights
import './IncidentTable.css'

// ============================================================
// SEVERITY ORDER MAP
// Used to sort severity levels correctly.
// "critical" should rank higher than "high" which ranks higher than "medium".
// Without this, alphabetical sort would put "critical" before "high" which
// happens to be correct, but "low" would come before "medium" (wrong order).
// Assigning numbers lets us sort numerically.
// ============================================================
const SEVERITY_ORDER = {
  critical: 4,
  high:     3,
  medium:   2,
  low:      1,
}

// ============================================================
// SORTABLE HEADER CELL - Small inline component
// ============================================================
// Renders a single <th> (table header cell) that can be clicked to sort.
//
// Props:
//   field         - The data field this header sorts by (e.g., 'risk_score')
//   label         - The display text shown to the user (e.g., 'Risk Score')
//   currentField  - Which field is currently being sorted (from parent state)
//   direction     - Current sort direction: 'asc' or 'desc'
//   onSort        - Function to call when this header is clicked
//   className     - Optional extra CSS class for width/alignment
const SortableHeader = ({ field, label, currentField, direction, onSort, className }) => {
  // Is THIS header the one currently being sorted?
  // We use this to decide whether to show the sort arrow
  const isActive = currentField === field

  return (
    <th
      // Combine base class, optional className, and 'active' if this column is sorted
      className={`table-th table-th--sortable ${className || ''} ${isActive ? 'table-th--active' : ''}`}
      // When clicked, call onSort with this column's field name
      onClick={() => onSort(field)}
      // Role and aria attributes make the header accessible to screen readers
      role="columnheader"
      aria-sort={isActive ? (direction === 'asc' ? 'ascending' : 'descending') : 'none'}
    >
      {/* Label text (e.g., "Risk Score") */}
      <span className="th-label">{label}</span>

      {/* Sort direction arrow — only visible when this column is active */}
      <span className={`sort-arrow ${isActive ? 'sort-arrow--visible' : ''}`}>
        {/* Show up arrow for ascending, down arrow for descending */}
        {direction === 'asc' ? '↑' : '↓'}
      </span>
    </th>
  )
}

// ============================================================
// MAIN COMPONENT: IncidentTable
// ============================================================
// Props this component receives from IncidentsList.jsx:
//   incidents          - Array of already-filtered and already-sorted incident objects
//   selectedIncidentId - ID of the currently open incident (to highlight its row)
//   onSelectIncident   - Function to call when a row is clicked
//   sortField          - Which field is currently sorted (to show arrow on correct header)
//   sortDirection      - 'asc' or 'desc' (to show correct arrow direction)
//   onSort             - Function to call when a header is clicked
const IncidentTable = ({
  incidents,
  selectedIncidentId,
  onSelectIncident,
  sortField,
  sortDirection,
  onSort,
}) => {

  // ── HELPER: Format risk score as percentage ───────────────
  // Converts 0.87 → "87%" and null → "—"
  const formatRisk = (score) => {
    if (score === null || score === undefined) return '—'
    return `${Math.round(score * 100)}%`
  }

  // ── HELPER: Format a date string to short readable format ─
  // Converts "2025-03-31T14:22:00" → "Mar 31, 2:22 PM"
  const formatDate = (dateString) => {
    if (!dateString) return '—'
    // Create a Date object from the ISO string
    const date = new Date(dateString)
    // Format with abbreviated month, day, hour, and minute
    return date.toLocaleString('en-US', {
      month: 'short', // "Mar"
      day:   'numeric', // "31"
      hour:  'numeric', // "2"
      minute: '2-digit', // "22"
    })
  }

  // ── HELPER: Get CSS class for severity badge color ────────
  const getSeverityClass = (severity) => {
    const map = {
      critical: 'badge--critical',
      high:     'badge--high',
      medium:   'badge--medium',
      low:      'badge--low',
    }
    return map[severity?.toLowerCase()] || 'badge--medium'
  }

  // ── HELPER: Determine row highlight class ─────────────────
  // Returns CSS classes for a table row based on:
  //   1. Whether this row is the currently selected incident
  //   2. Whether this row has a high risk score (> 0.7 = above 70%)
  const getRowClass = (incident) => {
    // Start with the base row class
    let classes = 'table-row'

    // If this row is selected, add the selected class
    if (incident.id === selectedIncidentId) {
      classes += ' table-row--selected'
    }

    // If risk score is above 70%, add high-risk highlight
    // This is independent of selection — a row can be both selected AND high-risk
    if (incident.risk_score > 0.7) {
      classes += ' table-row--high-risk'
    }

    return classes
  }

  // ── RENDER ────────────────────────────────────────────────
  return (
    // Wrapper div enables horizontal scrolling on small screens
    // without the table breaking the page layout
    <div className="table-wrapper">

      {/* The actual HTML table element */}
      <table className="incidents-table">

        {/* ── TABLE HEADER ─────────────────────────────────── */}
        {/* thead stays sticky at the top when the table body scrolls */}
        <thead className="table-head">
          <tr>

            {/* ID column — not sortable, it's always unique */}
            <th className="table-th table-th--id">#</th>

            {/* Type column — sortable alphabetically */}
            <SortableHeader
              field="incident_type"
              label="Type"
              currentField={sortField}
              direction={sortDirection}
              onSort={onSort}
              className="table-th--type"
            />

            {/* Description column — not sortable (free text, not meaningful to sort) */}
            <th className="table-th table-th--description">Description</th>

            {/* Location column — not sortable */}
            <th className="table-th table-th--location">Location</th>

            {/* Severity column — sortable by the SEVERITY_ORDER numeric mapping */}
            <SortableHeader
              field="severity"
              label="Severity"
              currentField={sortField}
              direction={sortDirection}
              onSort={onSort}
              className="table-th--severity"
            />

            {/* Risk Score column — sortable numerically — MAIN SORT COLUMN */}
            <SortableHeader
              field="risk_score"
              label="Risk"
              currentField={sortField}
              direction={sortDirection}
              onSort={onSort}
              className="table-th--risk"
            />

            {/* Created At column — sortable by date */}
            <SortableHeader
              field="created_at"
              label="Time"
              currentField={sortField}
              direction={sortDirection}
              onSort={onSort}
              className="table-th--time"
            />

          </tr>
        </thead>

        {/* ── TABLE BODY ───────────────────────────────────── */}
        {/* Each incident in the array becomes one table row */}
        <tbody>
          {incidents.map(incident => (
            // key is required by React for list items — use the unique database ID
            // The className is dynamically computed by getRowClass() above
            <tr
              key={incident.id}
              className={getRowClass(incident)}
              // When clicked, tell the parent which incident was selected
              onClick={() => onSelectIncident(incident)}
              // Pointer cursor makes it obvious the row is clickable
              style={{ cursor: 'pointer' }}
            >

              {/* ID cell */}
              <td className="table-td table-td--id">
                {/* Show risk indicator dot before ID for very high risk incidents */}
                {incident.risk_score > 0.7 && (
                  <span
                    className="risk-dot"
                    // Accessible label for screen readers
                    aria-label="High risk"
                    title="High risk incident"
                  >
                    🔴
                  </span>
                )}
                {incident.id}
              </td>

              {/* Type cell — shows the incident type as an uppercase badge */}
              <td className="table-td table-td--type">
                {incident.incident_type
                  ? (
                    <span className="type-badge">
                      {incident.incident_type.toUpperCase()}
                    </span>
                  )
                  : <span className="text-muted">—</span>
                }
              </td>

              {/* Description cell — truncated with ellipsis if too long */}
              <td className="table-td table-td--description">
                {/* The CSS class 'truncate' applies text-overflow: ellipsis */}
                <span className="truncate" title={incident.description}>
                  {incident.description}
                </span>
              </td>

              {/* Location cell — also truncated */}
              <td className="table-td table-td--location">
                <span className="truncate" title={incident.location}>
                  {incident.location || '—'}
                </span>
              </td>

              {/* Severity cell — colored badge */}
              <td className="table-td table-td--severity">
                {incident.severity
                  ? (
                    <span className={`badge ${getSeverityClass(incident.severity)}`}>
                      {incident.severity.toUpperCase()}
                    </span>
                  )
                  : <span className="text-muted">—</span>
                }
              </td>

              {/* Risk Score cell — number with conditional color class */}
              <td className="table-td table-td--risk">
                <span className={`risk-score ${
                  // Color the risk score based on its value
                  incident.risk_score > 0.7
                    ? 'risk-score--high'    // Red for > 70%
                    : incident.risk_score > 0.4
                      ? 'risk-score--medium'  // Orange for > 40%
                      : 'risk-score--low'     // Green for everything else
                }`}>
                  {formatRisk(incident.risk_score)}
                </span>
              </td>

              {/* Created At cell — formatted date/time */}
              <td className="table-td table-td--time">
                <span className="time-text">
                  {formatDate(incident.created_at)}
                </span>
              </td>

            </tr>
          ))}
        </tbody>

      </table>
    </div>
  )
}

// Export so IncidentsList.jsx can import it
export default IncidentTable