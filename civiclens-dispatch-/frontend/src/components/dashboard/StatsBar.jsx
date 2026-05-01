import { useState, useEffect } from 'react'
import { ClipboardList, AlertTriangle, Activity, TrendingUp } from 'lucide-react'
import { getIncidents } from '../../api/client'
import { Skeleton } from '../ui/Skeleton'
import { cn } from '../../lib/cn'

const DAY_MS = 86_400_000

function countToday(incidents) {
  const cutoff = Date.now() - DAY_MS
  return incidents.filter(i => new Date(i.created_at).getTime() > cutoff).length
}

function avgRisk(incidents) {
  const scored = incidents.filter(i => i.risk_score != null)
  if (!scored.length) return null
  return Math.round(scored.reduce((s, i) => s + i.risk_score, 0) / scored.length * 100)
}

function Delta({ value, label = 'today' }) {
  if (value == null || value === 0) return null
  const isUp = value > 0
  return (
    <span className={cn(
      'text-label tabular-nums font-semibold',
      isUp ? 'text-red-400' : 'text-emerald-400',
    )}>
      {isUp ? '↑' : '↓'}{Math.abs(value)} {label}
    </span>
  )
}

const STAT_CARDS = [
  {
    key: 'total',
    label: 'Total Incidents',
    icon: ClipboardList,
    accent: 'border-l-slate-600',
    compute: (inc) => ({ value: inc.length, delta: countToday(inc) }),
    deltaLabel: 'today',
  },
  {
    key: 'high',
    label: 'High Priority',
    icon: AlertTriangle,
    accent: 'border-l-red-500',
    compute: (inc) => {
      const high = inc.filter(i => ['high', 'critical'].includes(i.severity?.toLowerCase()))
      const highToday = high.filter(i => new Date(i.created_at).getTime() > Date.now() - DAY_MS).length
      return { value: high.length, delta: highToday }
    },
    deltaLabel: 'today',
  },
  {
    key: 'active',
    label: 'AI Processed',
    icon: Activity,
    accent: 'border-l-blue-500',
    compute: (inc) => {
      const processed = inc.filter(i => i.summary || i.incident_type)
      const pending   = inc.filter(i => !i.summary && !i.incident_type).length
      return { value: processed.length, delta: pending > 0 ? -pending : 0, deltaLabel: 'pending' }
    },
    deltaLabel: 'pending',
  },
  {
    key: 'avg_risk',
    label: 'Avg Risk Score',
    icon: TrendingUp,
    accent: 'border-l-accent',
    compute: (inc) => {
      const risk = avgRisk(inc)
      const label = risk == null ? '—' : `${risk}`
      return { value: label, delta: null }
    },
    deltaLabel: null,
  },
]

function StatCard({ label, value, delta, deltaLabel, icon: Icon, accent, loading }) {
  if (loading) {
    return (
      <div className="bg-surface border border-border rounded-xl p-4 border-l-2 border-l-border">
        <Skeleton className="h-10 w-16 mb-2" />
        <Skeleton className="h-3 w-20" />
      </div>
    )
  }
  return (
    <div className={cn('bg-surface border border-border rounded-xl p-4 border-l-2 flex flex-col gap-2', accent)}>
      <div className="flex items-start justify-between">
        <span className="text-display font-bold text-text-primary tabular-nums leading-none">{value}</span>
        <div className="w-8 h-8 rounded-lg bg-surface-2 flex items-center justify-center flex-shrink-0">
          <Icon size={16} className="text-text-muted" />
        </div>
      </div>
      <div className="flex items-center justify-between">
        <span className="text-label text-text-muted uppercase tracking-widest">{label}</span>
        <Delta value={delta} label={deltaLabel} />
      </div>
    </div>
  )
}

function StatsBar({ refreshTrigger }) {
  const [incidents, setIncidents] = useState([])
  const [loading,   setLoading]   = useState(true)

  useEffect(() => {
    async function fetchData() {
      try {
        const data = await getIncidents()
        setIncidents(data)
      } catch (err) {
        console.error('StatsBar fetch error:', err)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [refreshTrigger])

  return (
    <div className="grid grid-cols-4 gap-4 flex-shrink-0">
      {STAT_CARDS.map(({ key, label, icon, accent, compute, deltaLabel }) => {
        const result = loading ? {} : compute(incidents)
        return (
          <StatCard
            key={key}
            label={label}
            value={loading ? null : result.value}
            delta={loading ? null : result.delta}
            deltaLabel={result.deltaLabel ?? deltaLabel}
            icon={icon}
            accent={accent}
            loading={loading}
          />
        )
      })}
    </div>
  )
}

export default StatsBar
