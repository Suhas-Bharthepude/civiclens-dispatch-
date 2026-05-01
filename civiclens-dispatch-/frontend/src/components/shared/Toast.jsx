import { useEffect } from 'react'
import { CheckCircle2, AlertCircle, AlertTriangle, Info, X } from 'lucide-react'
import { cn } from '../../lib/cn'

const VARIANTS = {
  success: { icon: CheckCircle2, classes: 'border-emerald-800 bg-emerald-950/80 text-emerald-300' },
  error:   { icon: AlertCircle,  classes: 'border-red-800 bg-red-950/80 text-red-300'             },
  warning: { icon: AlertTriangle,classes: 'border-amber-800 bg-amber-950/80 text-amber-300'       },
  info:    { icon: Info,         classes: 'border-blue-800 bg-blue-950/80 text-blue-300'          },
}

function Toast({ message, type = 'info', duration = 5000, onClose }) {
  useEffect(() => {
    if (!onClose || !duration) return
    const t = setTimeout(onClose, duration)
    return () => clearTimeout(t)
  }, [duration, onClose])

  const { icon: Icon, classes } = VARIANTS[type] ?? VARIANTS.info

  return (
    <div
      className={cn(
        'flex items-start gap-3 px-4 py-3 rounded-lg border',
        'min-w-[280px] max-w-sm shadow-lg',
        classes,
      )}
      role="alert"
    >
      <Icon size={16} className="flex-shrink-0 mt-0.5" />
      <span className="flex-1 text-body">{message}</span>
      {onClose && (
        <button
          onClick={onClose}
          className="flex-shrink-0 opacity-60 hover:opacity-100 transition-opacity"
          aria-label="Dismiss"
        >
          <X size={14} />
        </button>
      )}
    </div>
  )
}

export default Toast
