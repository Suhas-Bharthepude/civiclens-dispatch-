import { useState, useEffect } from 'react'
import { Bot } from 'lucide-react'
import { getAIStatus } from '../../api/client'
import { StatusDot } from '../ui/StatusDot'

const STATUS_MAP = {
  healthy:  { dot: 'live',  label: 'AI Healthy'  },
  degraded: { dot: 'idle',  label: 'AI Degraded' },
  down:     { dot: 'error', label: 'AI Down'     },
  checking: { dot: 'idle',  label: 'AI…'         },
  unknown:  { dot: 'idle',  label: 'AI Unknown'  },
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
        setModelsReady(data.models_ready  || 0)
        setModelsTotal(data.models_total  || 4)
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
    <div
      className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-surface-2 border border-border cursor-default"
      title={`${modelsReady}/${modelsTotal} AI models responding`}
    >
      <StatusDot variant={cfg.dot} size="sm" />
      <Bot size={12} className="text-text-muted" />
      <span className="text-caption text-text-secondary">{cfg.label}</span>
      {status !== 'checking' && (
        <span className="text-caption text-text-muted font-normal">
          {modelsReady}/{modelsTotal}
        </span>
      )}
    </div>
  )
}

export default AIStatusIndicator
