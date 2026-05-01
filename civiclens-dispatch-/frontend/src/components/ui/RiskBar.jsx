import { cn } from '../../lib/cn'

function barColor(score) {
  if (score >= 70) return 'bg-red-500'
  if (score >= 40) return 'bg-amber-500'
  return 'bg-emerald-500'
}

export function RiskBar({ score, className }) {
  const pct = Math.min(100, Math.max(0, score ?? 0))
  return (
    <div className={cn('flex items-center gap-2', className)}>
      <div className="w-16 h-1.5 rounded-full bg-border overflow-hidden flex-shrink-0">
        <div
          className={cn('h-full rounded-full transition-all duration-300', barColor(pct))}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className={cn('font-mono text-caption tabular-nums', barColor(pct).replace('bg-', 'text-'))}>
        {pct}
      </span>
    </div>
  )
}
