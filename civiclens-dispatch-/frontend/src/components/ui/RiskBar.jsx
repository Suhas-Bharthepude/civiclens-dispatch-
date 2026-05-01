import { cn } from '../../lib/cn'

function barColor(score) {
  if (score >= 60) return { bar: 'bg-red-500',     text: 'text-red-400'     }
  if (score >= 30) return { bar: 'bg-amber-500',   text: 'text-amber-400'   }
  return               { bar: 'bg-emerald-500', text: 'text-emerald-400' }
}

export function RiskBar({ score, className }) {
  const pct    = Math.min(100, Math.max(0, score ?? 0))
  const colors = barColor(pct)
  return (
    <div className={cn('flex items-center gap-2', className)}>
      <div className="w-16 h-1.5 rounded-full bg-border overflow-hidden flex-shrink-0">
        <div
          className={cn('h-full rounded-full transition-all duration-300', colors.bar)}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className={cn('font-mono text-caption tabular-nums font-semibold', colors.text)}>
        {pct}
        <span className="text-text-muted font-normal">/100</span>
      </span>
    </div>
  )
}
