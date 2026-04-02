// frontend/src/components/dashboard/AIStatusIndicator.jsx
// Small badge component that shows AI pipeline health status
// Calls GET /ai/status every 60 seconds and displays a colored indicator
//
// Possible states:
//   🟢 Healthy  — all 4 AI models are responding
//   🟡 Degraded — some models are down (partial AI functionality)
//   🔴 Down     — no models are responding (AI unavailable)
//   ⚪ Checking — initial check in progress
//
// Day 53: AI status indicator for dispatcher dashboard

// Import React hooks
// useState: stores the current status
// useEffect: runs the status check on mount and sets up interval
import { useState, useEffect } from 'react'

// Import the API function to check AI health
// This calls GET /ai/status on the backend
import { getAIStatus } from '../../api/client'


// ========================================
// AI STATUS INDICATOR COMPONENT
// ========================================

function AIStatusIndicator() {

  // ========================================
  // STATE
  // ========================================

  // Current pipeline status string: "healthy", "degraded", "down", or "checking"
  // Starts as "checking" while the first request is in flight
  const [status, setStatus] = useState('checking')

  // Number of models that are ready (e.g., 3 out of 4)
  const [modelsReady, setModelsReady] = useState(0)

  // Total number of models in the pipeline
  const [modelsTotal, setModelsTotal] = useState(4)


  // ========================================
  // FETCH AI STATUS ON MOUNT + INTERVAL
  // ========================================

  useEffect(() => {

    // Function that fetches the current AI pipeline status
    async function checkStatus() {
      try {
        // Call the backend API to get AI model health
        const data = await getAIStatus()

        // Update state with the response data
        setStatus(data.pipeline_status || 'unknown')
        setModelsReady(data.models_ready || 0)
        setModelsTotal(data.models_total || 4)

      } catch (err) {
        // If the status endpoint itself fails, show "unknown"
        // This could mean the backend is down entirely
        console.error('AI status check failed:', err)
        setStatus('unknown')
      }
    }

    // Run the check immediately on component mount
    checkStatus()

    // Set up an interval to re-check every 60 seconds
    // AI model availability changes slowly, so 60s is fine
    // (compared to 30s for incident data which changes faster)
    const intervalId = setInterval(checkStatus, 60000)

    // Cleanup function: runs when the component unmounts
    // clearInterval stops the periodic checking to prevent memory leaks
    return () => clearInterval(intervalId)

  }, [])
  // Empty dependency array [] means this effect runs once on mount


  // ========================================
  // VISUAL CONFIGURATION
  // ========================================

  // Map each status to its display properties (color, label, dot color)
  const statusConfig = {
    healthy:  { label: 'AI Healthy',  dotColor: '#22c55e', textColor: '#166534' },
    degraded: { label: 'AI Degraded', dotColor: '#f59e0b', textColor: '#92400e' },
    down:     { label: 'AI Down',     dotColor: '#ef4444', textColor: '#991b1b' },
    checking: { label: 'AI...',       dotColor: '#94a3b8', textColor: '#64748b' },
    unknown:  { label: 'AI Unknown',  dotColor: '#94a3b8', textColor: '#64748b' },
  }

  // Get the config for the current status, with a fallback
  const config = statusConfig[status] || statusConfig.unknown


  // ========================================
  // RENDER
  // ========================================

  return (
    // Container — inline flex so it sits next to other header elements
    <div
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '6px',
        padding: '4px 10px',
        borderRadius: '9999px',
        backgroundColor: '#f8fafc',
        border: '1px solid #e2e8f0',
        fontSize: '11px',
        fontWeight: '600',
        color: config.textColor,
        cursor: 'default',
      }}
      // Tooltip shows model count on hover
      title={`${modelsReady}/${modelsTotal} AI models responding`}
    >
      {/* Colored dot indicator */}
      <span
        style={{
          width: '8px',
          height: '8px',
          borderRadius: '50%',
          backgroundColor: config.dotColor,
          // Pulse animation for "checking" state
          animation: status === 'checking' ? 'pulse 1.5s ease-in-out infinite' : 'none',
        }}
      />

      {/* Status label text */}
      <span>{config.label}</span>

      {/* Model count — only show when we have data */}
      {status !== 'checking' && (
        <span style={{ color: '#94a3b8', fontWeight: '400' }}>
          {modelsReady}/{modelsTotal}
        </span>
      )}
    </div>
  )
}

// Export the component
export default AIStatusIndicator