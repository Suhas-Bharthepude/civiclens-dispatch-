import { useEffect } from 'react'
import { CheckCircle2, AlertCircle, AlertTriangle, Info, X } from 'lucide-react'
import { cn } from '../../lib/cn'

const VARIANTS = {
  success: {
    icon: CheckCircle2,
    classes: 'border-emerald-700/60 bg-emerald-950/90 text-emerald-300',
    dot: 'bg-emerald-400',
  },
  error: {
    icon: AlertCircle,
    classes: 'border-red-700/60 bg-red-950/90 text-red-300',
    dot: 'bg-red-400',
  },
  warning: {
    icon: AlertTriangle,
    classes: 'border-amber-700/60 bg-amber-950/90 text-amber-300',
    dot: 'bg-amber-400',
  },
  info: {
    icon: Info,
    classes: 'border-blue-700/60 bg-blue-950/90 text-blue-300',
    dot: 'bg-blue-400',
  },
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
        'flex items-start gap-3 px-4 py-3 rounded-xl border',
        'min-w-[300px] max-w-sm',
        'shadow-[0_8px_32px_rgba(0,0,0,0.6)] backdrop-blur-sm',
        'animate-toast-in',
        classes,
      )}
      role="alert"
    >
      <Icon size={15} className="flex-shrink-0 mt-0.5" />
      <span className="flex-1 text-body">{message}</span>
      {onClose && (
        <button
          onClick={onClose}
          className="flex-shrink-0 opacity-50 hover:opacity-100 transition-opacity focus:outline-none"
          aria-label="Dismiss"
        >
          <X size={13} />
        </button>
      )}
    </div>
  )
}

export default Toast
