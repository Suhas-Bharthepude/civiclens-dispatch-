import { useState, useEffect } from 'react'
import { ClipboardList, AlertTriangle, Activity, TrendingUp } from 'lucide-react'
import { getIncidents } from '../../api/client'
import { Skeleton } from '../ui/Skeleton'

const STAT_CARDS = [
  {
    key: 'total',
    label: 'Total Incidents',
    icon: ClipboardList,
    accent: 'border-l-text-muted',
    compute: (inc) => inc.length,
  },
  {
    key: 'high',
    label: 'High Priority',
    icon: AlertTriangle,
    accent: 'border-l-sev-high',
    compute: (inc) => inc.filter(i => i.severity?.toLowerCase() === 'high').length,
  },
  {
    key: 'active',
    label: 'Active',
    icon: Activity,
    accent: 'border-l-blue-500',
    compute: (inc) => inc.filter(i => i.summary || i.incident_type).length,
  },
  {
    key: 'avg_risk',
    label: 'Avg Risk Score',
    icon: TrendingUp,
    accent: 'border-l-accent',
    compute: (inc) => {
      const scored = inc.filter(i => i.risk_score != null)
      if (!scored.length) return '—'
      const avg = scored.reduce((s, i) => s + i.risk_score, 0) / scored.length
      return `${Math.round(avg * 100)}`
    },
  },
]

function StatCard({ label, value, icon: Icon, accent, loading }) {
  if (loading) {
    return (
      <div className="bg-surface border border-border rounded-lg p-4 border-l-2 border-l-border">
        <Skeleton className="h-7 w-10 mb-2" />
        <Skeleton className="h-3 w-20" />
      </div>
    )
  }
  return (
    <div className={`bg-surface border border-border rounded-lg p-4 border-l-2 ${accent} flex flex-col gap-1`}>
      <div className="flex items-center justify-between">
        <span className="text-display font-bold text-text-primary tabular-nums">{value}</span>
        <Icon size={16} className="text-text-muted flex-shrink-0" />
      </div>
      <span className="text-caption text-text-muted uppercase tracking-widest">{label}</span>
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
      {STAT_CARDS.map(({ key, label, icon, accent, compute }) => (
        <StatCard
          key={key}
          label={label}
          value={loading ? null : compute(incidents)}
          icon={icon}
          accent={accent}
          loading={loading}
        />
      ))}
    </div>
  )
}

export default StatsBar
