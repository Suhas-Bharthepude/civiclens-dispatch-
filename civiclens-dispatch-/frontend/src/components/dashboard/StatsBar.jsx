// frontend/src/components/dashboard/StatsBar.jsx
// Dashboard stats bar that shows incident counts at the top of the page
// Fetches incidents data directly and computes real counts
//
// Day 51: Fixed to fetch data and compute actual counts
//
// Props:
//   - refreshTrigger: Number that increments when data should be re-fetched

// Import React hooks
import { useState, useEffect } from 'react'

// Import the API function to fetch incidents
import { getIncidents } from '../../api/client'


// ========================================
// STATS BAR COMPONENT
// ========================================

function StatsBar({ refreshTrigger }) {
  
  // ========================================
  // STATE — Store the fetched incidents
  // ========================================
  
  // State to hold the incidents array for computing stats
  // Starts as empty array, populated after fetch
  const [incidents, setIncidents] = useState([])
  
  
  // ========================================
  // FETCH DATA ON MOUNT AND REFRESH
  // ========================================
  
  // useEffect runs when the component mounts and when refreshTrigger changes
  // This keeps the stats in sync with the incidents table
  useEffect(() => {
    // Define async fetch function inside useEffect
    async function fetchData() {
      try {
        // Fetch all incidents from the backend API
        const data = await getIncidents()
        // Update state with the fetched data
        setIncidents(data)
      } catch (err) {
        // If fetch fails, just log it — stats will show 0
        console.error('StatsBar fetch error:', err)
      }
    }
    // Call the fetch function
    fetchData()
  }, [refreshTrigger])
  // The [refreshTrigger] dependency array means this re-runs
  // whenever refreshTrigger changes (e.g., after a new incident is submitted)
  
  
  // ========================================
  // CALCULATE STATS FROM INCIDENTS DATA
  // ========================================
  
  // Total number of incidents
  const totalIncidents = incidents.length
  
  // Count of high priority incidents (severity === "high")
  const highPriority = incidents.filter(
    inc => inc.severity && inc.severity.toLowerCase() === 'high'
  ).length
  
  // Count of incidents without AI processing yet (no summary means not processed)
  const pending = incidents.filter(
    inc => !inc.summary && !inc.incident_type
  ).length
  
  // Count of active incidents (have been processed by AI)
  const active = incidents.filter(
    inc => inc.summary || inc.incident_type
  ).length
  
  // Count of fire incidents specifically
  const fireCount = incidents.filter(
    inc => inc.incident_type && inc.incident_type.toLowerCase() === 'fire'
  ).length
  
  // Count of incidents the dispatcher has marked resolved
  const resolved = incidents.filter(
    inc => inc.status === 'resolved'
  ).length
  
  
  // ========================================
  // STAT CARD DEFINITIONS
  // ========================================
  
  const stats = [
    { label: 'TOTAL INCIDENTS', value: totalIncidents, icon: '📋' },
    { label: 'HIGH PRIORITY',   value: highPriority,   icon: '🔴' },
    { label: 'PENDING',         value: pending,         icon: '⏳' },
    { label: 'ACTIVE',          value: active,          icon: '🟢' },
    { label: 'FIRE',            value: fireCount,       icon: '🔥' },
    { label: 'RESOLVED',        value: resolved,        icon: '✅' },
  ]
  
  
  // ========================================
  // RENDER
  // ========================================
  
  return (
    // Stats grid container
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(6, 1fr)',
      gap: '1px',
      backgroundColor: '#e5e7eb',
      borderRadius: '8px',
      overflow: 'hidden',
      marginBottom: '16px',
    }}>
      {stats.map((stat, index) => (
        <div
          key={index}
          style={{
            backgroundColor: '#ffffff',
            padding: '16px 12px',
            textAlign: 'center',
          }}
        >
          {/* The number value */}
          <div style={{
            fontSize: '1.5rem',
            fontWeight: '800',
            color: '#1f2937',
            marginBottom: '4px',
          }}>
            {stat.value}
          </div>
          
          {/* The label */}
          <div style={{
            fontSize: '0.7rem',
            fontWeight: '600',
            color: '#6b7280',
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '4px',
          }}>
            <span>{stat.icon}</span>
            <span>{stat.label}</span>
          </div>
        </div>
      ))}
    </div>
  )
}

export default StatsBar