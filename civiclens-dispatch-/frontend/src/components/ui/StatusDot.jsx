import { cn } from '../../lib/cn'

const config = {
  live:  { color: 'bg-emerald-400', pulse: true  },
  idle:  { color: 'bg-slate-500',   pulse: false },
  error: { color: 'bg-red-500',     pulse: false },
}

export function StatusDot({ variant = 'idle', size = 'md', className }) {
  const { color, pulse } = config[variant] ?? config.idle
  const sz = size === 'sm' ? 'w-1.5 h-1.5' : 'w-2 h-2'

  return (
    <span className={cn('relative inline-flex', className)}>
      {pulse && (
        <span
          className={cn(
            'absolute inline-flex rounded-full opacity-75 animate-ping',
            sz, color,
          )}
        />
      )}
      <span className={cn('relative inline-flex rounded-full', sz, color)} />
    </span>
  )
}
