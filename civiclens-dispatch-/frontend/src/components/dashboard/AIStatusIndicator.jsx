import { useState, useEffect } from 'react'
import { getAIStatus } from '../../api/client'
import { StatusDot } from '../ui/StatusDot'

const STATUS_MAP = {
  healthy:  { dot: 'live',  label: 'AI' },
  degraded: { dot: 'idle',  label: 'AI' },
  down:     { dot: 'error', label: 'AI' },
  checking: { dot: 'idle',  label: 'AI' },
  unknown:  { dot: 'idle',  label: 'AI' },
}

function AIStatusIndicator() {
  const [status,      setStatus]      = useState('checking')
  const [modelsReady, setModelsReady] = useState(0)
  const [modelsTotal, setModelsTotal] = useState(4)

  useEffect(() => {
    async function checkStatus() {
      try {
        const data = await getAIStatus()
        setStatus(data.pipeline_status || 'unknown')
        setModelsReady(data.models_ready || 0)
        setModelsTotal(data.models_total || 4)
      } catch {
        setStatus('unknown')
      }
    }
    checkStatus()
    const id = setInterval(checkStatus, 60000)
    return () => clearInterval(id)
  }, [])

  const cfg = STATUS_MAP[status] ?? STATUS_MAP.unknown

  return (
    <span
      className="flex items-center gap-1.5 cursor-default"
      title={`${modelsReady}/${modelsTotal} AI models responding`}
    >
      <StatusDot variant={cfg.dot} size="sm" />
      <span className="text-caption text-text-muted">
        {cfg.label} {status !== 'checking' ? `${modelsReady}/${modelsTotal}` : '…'}
      </span>
    </span>
  )
}

export default AIStatusIndicator
