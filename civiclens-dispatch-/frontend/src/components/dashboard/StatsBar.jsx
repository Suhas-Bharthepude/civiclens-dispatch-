// frontend/src/components/dashboard/StatsBar.jsx
//
// A horizontal bar of KPI (Key Performance Indicator) cards shown
// at the top of the dashboard, above the incidents table.
//
// Each card shows one number and a label:
//   Total  |  🔴 High+Critical  |  Pending  |  🔥 Fire  |  ✅ Resolved
//
// The component:
//   1. Fetches stats from GET /incidents/stats on mount
//   2. Auto-refreshes every 30 seconds alongside the incidents table
//   3. Shows skeleton placeholders while loading
//   4. Silently ignores errors (stats are supplementary, not critical)
//
// Props received from App.jsx:
//   refreshTrigger - number that increments when incidents change
//                    (form submit, status change) — causes re-fetch

// useState: stores stats data and loading state
// useEffect: runs the fetch on mount and when refreshTrigger changes
import { useState, useEffect } from 'react'

// getStats calls GET /incidents/stats and returns the JSON response
import { getStats } from '../../api/client'

// CSS styles for the card layout and colors
import './StatsBar.css'

// ============================================================
// STAT CARD — tiny sub-component
// ============================================================
// Renders one number + label card.
// Using a sub-component instead of repeating the HTML keeps the
// main component clean and makes it easy to add/remove cards.
//
// Props:
//   value    - the number to display (e.g., 10)
//   label    - the text below the number (e.g., "Total Incidents")
//   color    - CSS class suffix for the accent color
//              ('blue' | 'red' | 'orange' | 'green' | 'purple')
//   loading  - if true, show a placeholder skeleton instead of the value
const StatCard = ({ value, label, color = 'blue', loading = false }) => (
  // The outer div gets a color-specific CSS class for the left border accent
  <div className={`stat-card stat-card--${color}`}>

    {/* The big number — or a skeleton placeholder while loading */}
    <div className={`stat-card__value ${loading ? 'stat-card__value--loading' : ''}`}>
      {loading
        // Skeleton placeholder: an empty div that gets an animated shimmer
        ? <span className="stat-skeleton" />
        // The actual number — shown once data is available
        : value ?? '—'
        // ?? is the "nullish coalescing" operator:
        // if value is null or undefined, show '—' instead
      }
    </div>

    {/* The label text below the number */}
    <div className="stat-card__label">{label}</div>

  </div>
)

// ============================================================
// MAIN COMPONENT: StatsBar
// ============================================================
const StatsBar = ({ refreshTrigger }) => {

  // stats: the data object returned by GET /incidents/stats
  // null means we haven't received data yet
  const [stats, setStats] = useState(null)

  // loading: true while the first fetch is in progress
  // Once we have data, background refreshes don't set this to true
  // (to avoid the skeleton flickering every 30 seconds)
  const [loading, setLoading] = useState(true)

  // ── FETCH FUNCTION ────────────────────────────────────
  // Fetches stats from the backend and updates state
  const fetchStats = async (isFirstLoad = false) => {
    try {
      // Only show the skeleton on first load
      if (isFirstLoad) setLoading(true)

      // Call the API — GET /incidents/stats
      const data = await getStats()

      // Store the response in state
      setStats(data)

    } catch (err) {
      // Stats are supplementary — if they fail, log but don't crash
      // The main incidents table still works fine without stats
      console.warn('[StatsBar] Failed to fetch stats:', err.message)

    } finally {
      // Always clear the loading state
      setLoading(false)
    }
  }

  // ── INITIAL FETCH ─────────────────────────────────────
  // Runs once when the component mounts (appears on screen for the first time)
  useEffect(() => {
    fetchStats(true) // true = first load = show skeleton
  }, []) // Empty array = run only once on mount

  // ── REFRESH WHEN INCIDENTS CHANGE ─────────────────────
  // When App.jsx increments refreshTrigger (after a form submit or status
  // change), re-fetch stats so the counts stay accurate.
  // Skip the very first render (refreshTrigger starts at 0).
  useEffect(() => {
    if (refreshTrigger > 0) {
      fetchStats(false) // false = background refresh = no skeleton
    }
  }, [refreshTrigger]) // Re-run whenever refreshTrigger changes

  // ── COMPUTED VALUES ───────────────────────────────────
  // Pre-calculate the values we'll show in cards.
  // If stats is null (still loading), these will all be undefined,
  // and StatCard handles that by showing '—'.

  // High + Critical combined — the most urgent incidents
  // We show these together because both need immediate attention
  const urgentCount = stats
    ? (stats.by_severity.high || 0) + (stats.by_severity.critical || 0)
    : null

  // ── RENDER ────────────────────────────────────────────
  return (
    // Outer wrapper — a horizontal row of cards
    <div className="stats-bar">

      {/* TOTAL INCIDENTS */}
      <StatCard
        value={stats?.total}        // stats?.total safely returns undefined if stats is null
        label="Total Incidents"
        color="blue"
        loading={loading}
      />

      {/* HIGH + CRITICAL (combined urgent count) */}
      <StatCard
        value={urgentCount}
        label="High Priority"
        color="red"
        loading={loading}
      />

      {/* PENDING — not yet acknowledged */}
      <StatCard
        value={stats?.by_status.pending}
        label="Pending"
        color="orange"
        loading={loading}
      />

      {/* ACTIVE — being handled right now */}
      <StatCard
        value={stats?.by_status.active}
        label="Active"
        color="purple"
        loading={loading}
      />

      {/* FIRE incidents */}
      <StatCard
        value={stats?.by_type.fire}
        label="🔥 Fire"
        color="red"
        loading={loading}
      />

      {/* RESOLVED — closed incidents */}
      <StatCard
        value={stats?.by_status.resolved}
        label="✅ Resolved"
        color="green"
        loading={loading}
      />

    </div>
  )
}

// Export so App.jsx can import and render it
export default StatsBar