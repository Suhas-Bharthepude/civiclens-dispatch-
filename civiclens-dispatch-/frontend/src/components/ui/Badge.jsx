import { cn } from '../../lib/cn'

const variants = {
  default:   'bg-surface-2 text-text-secondary border border-border',
  low:       'bg-slate-900/60 text-slate-400 border border-slate-700',
  medium:    'bg-amber-950/60 text-amber-400 border border-amber-800',
  high:      'bg-red-950/60 text-red-400 border border-red-800',
  critical:  'bg-red-950 text-red-300 border border-red-700',
  info:      'bg-blue-950/60 text-blue-400 border border-blue-800',
  success:   'bg-emerald-950/60 text-emerald-400 border border-emerald-800',
  pending:   'bg-surface-2 text-text-muted border border-border',
  active:    'bg-blue-950/60 text-blue-400 border border-blue-800',
  resolved:  'bg-emerald-950/60 text-emerald-400 border border-emerald-800',
  role:      'bg-amber-950/60 text-amber-300 border border-amber-800',
}

const dots = {
  low:      'bg-slate-400',
  medium:   'bg-amber-400',
  high:     'bg-red-400',
  critical: 'bg-red-300',
  info:     'bg-blue-400',
  success:  'bg-emerald-400',
  pending:  'bg-slate-500',
  active:   'bg-blue-400',
  resolved: 'bg-emerald-400',
}

export function Badge({ variant = 'default', dot = false, children, className }) {
  const dotColor = dots[variant]
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full',
        'text-caption font-medium uppercase tracking-widest whitespace-nowrap',
        variants[variant],
        className,
      )}
    >
      {dot && dotColor && (
        <span className={cn('w-1.5 h-1.5 rounded-full flex-shrink-0', dotColor)} />
      )}
      {children}
    </span>
  )
}
