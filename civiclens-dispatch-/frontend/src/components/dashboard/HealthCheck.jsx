import { useState, useEffect } from 'react'
import { checkHealth } from '../../api/client'
import { StatusDot } from '../ui/StatusDot'

const HealthCheck = () => {
  const [status, setStatus] = useState('checking')

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
    const id = setInterval(check, 30000)
    return () => clearInterval(id)
  }, [])

  const dot   = status === 'ok' ? 'live' : status === 'error' ? 'error' : 'idle'
  const label = status === 'ok' ? 'API Connected' : status === 'error' ? 'API Offline' : 'Connecting…'

  return (
    <div className="flex items-center gap-1.5">
      <StatusDot variant={dot} size="sm" />
      <span className="text-caption text-text-secondary">{label}</span>
    </div>
  )
}

export default HealthCheck
