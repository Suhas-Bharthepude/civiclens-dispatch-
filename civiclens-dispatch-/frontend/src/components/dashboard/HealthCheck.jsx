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
  const label = status === 'ok' ? 'API' : status === 'error' ? 'API Offline' : 'API…'

  return (
    <span className="flex items-center gap-1.5">
      <StatusDot variant={dot} size="sm" />
      <span className="text-caption text-text-muted">{label}</span>
    </span>
  )
}

export default HealthCheck
