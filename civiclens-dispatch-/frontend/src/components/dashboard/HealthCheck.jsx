// frontend/src/components/dashboard/HealthCheck.jsx
// Shows a small inline status indicator in the header.
// Green dot = backend is reachable. Red dot = backend is down.

import { useState, useEffect } from 'react'
import { checkHealth } from '../../api/client'

const HealthCheck = () => {
  const [status, setStatus] = useState('checking') // 'checking' | 'ok' | 'error'

  useEffect(() => {
    const check = async () => {
      try {
        await checkHealth()
        setStatus('ok')
      } catch {
        setStatus('error')
      }
    }
    check()
    // Re-check every 30 seconds
    const interval = setInterval(check, 30000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
      {/* Colored dot */}
      <span style={{
        width: 8,
        height: 8,
        borderRadius: '50%',
        flexShrink: 0,
        backgroundColor:
          status === 'ok'       ? '#22c55e' :
          status === 'error'    ? '#ef4444' :
                                  '#94a3b8',
        // Pulse animation when ok
        boxShadow: status === 'ok'
          ? '0 0 0 2px rgba(34,197,94,0.25)'
          : 'none',
      }} />
      {/* Status text */}
      <span style={{
        fontSize: 12,
        fontWeight: 500,
        color:
          status === 'ok'    ? '#22c55e' :
          status === 'error' ? '#ef4444' :
                               '#94a3b8',
      }}>
        {status === 'ok'       ? 'API Connected' :
         status === 'error'    ? 'API Offline' :
                                 'Connecting...'}
      </span>
    </div>
  )
}

export default HealthCheck