import { useState, useEffect } from 'react'
import {
  LineChart, Line,
  BarChart, Bar,
  XAxis, YAxis,
  CartesianGrid, Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { BarChart3, AlertTriangle, TrendingUp, ClipboardList } from 'lucide-react'

import { getAnalyticsSummary, getTimeseries, getRiskDistribution } from '../../api/client'
import { Card }      from '../ui/Card'
import { Skeleton }  from '../ui/Skeleton'
import { EmptyState } from '../ui/EmptyState'

const CHART_THEME = {
  grid:   '#1f2a40',
  axis:   '#64748b',
  accent: '#f59e0b',
  high:   '#ef4444',
  medium: '#f59e0b',
  bg:     '#111726',
  border: '#1f2a40',
  text:   '#94a3b8',
}

const TOOLTIP_STYLE = {
  contentStyle: {
    background: CHART_THEME.bg,
    border: `1px solid ${CHART_THEME.border}`,
    borderRadius: 8,
    fontSize: 12,
    color: '#f1f5f9',
  },
  labelStyle: { color: '#94a3b8', fontWeight: 600 },
}

function StatCard({ label, value, icon: Icon, accentClass }) {
  return (
    <Card className={`border-l-2 ${accentClass}`}>
      <div className="flex items-center justify-between mb-1">
        <span className="text-display font-bold text-text-primary tabular-nums">{value}</span>
        <Icon size={16} className="text-text-muted" />
      </div>
      <span className="text-caption text-text-muted uppercase tracking-widest">{label}</span>
    </Card>
  )
}

function ChartSection({ title, subtitle, children }) {
  return (
    <Card className="flex flex-col gap-3">
      <div>
        <h3 className="text-heading text-text-primary">{title}</h3>
        {subtitle && <p className="text-caption text-text-muted mt-0.5">{subtitle}</p>}
      </div>
      {children}
    </Card>
  )
}

const fmtRisk = (v) => `${(v * 100).toFixed(1)}%`
const fmtName = (s) => s ? s.charAt(0).toUpperCase() + s.slice(1) : '—'

const AnalyticsView = () => {
  const [summary,    setSummary]    = useState(null)
  const [timeseries, setTimeseries] = useState([])
  const [riskDist,   setRiskDist]   = useState([])
  const [loading,    setLoading]    = useState(true)
  const [error,      setError]      = useState(null)

  useEffect(() => {
    const fetchAll = async () => {
      setLoading(true)
      setError(null)
      try {
        const [summaryData, timeseriesData, riskData] = await Promise.all([
          getAnalyticsSummary(),
          getTimeseries(30),
          getRiskDistribution(),
        ])
        setSummary(summaryData)
        setTimeseries(timeseriesData)
        setRiskDist(riskData)
      } catch (err) {
        setError(err.message || 'Failed to load analytics data')
      } finally {
        setLoading(false)
      }
    }
    fetchAll()
  }, [])

  if (loading) {
    return (
      <div className="flex flex-col gap-4 max-w-5xl mx-auto">
        <div className="grid grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-20" />)}
        </div>
        <Skeleton className="h-64" />
        <div className="grid grid-cols-2 gap-4">
          <Skeleton className="h-52" />
          <Skeleton className="h-52" />
        </div>
        <Skeleton className="h-52" />
      </div>
    )
  }

  if (error) {
    return (
      <EmptyState
        icon={AlertTriangle}
        title="Failed to load analytics"
        description={error}
      />
    )
  }

  if (!summary || summary.total_incidents === 0) {
    return (
      <EmptyState
        icon={BarChart3}
        title="No data yet"
        description="Submit an incident to start seeing analytics."
      />
    )
  }

  return (
    <div className="flex flex-col gap-6 max-w-5xl mx-auto">

      {/* Header */}
      <div>
        <h2 className="text-display text-text-primary">Incident Analytics</h2>
        <p className="text-body text-text-muted mt-1">Aggregate statistics across all incidents</p>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard label="Total Incidents"   value={summary.total_incidents}          icon={ClipboardList} accentClass="border-l-text-muted" />
        <StatCard label="Avg Risk Score"    value={fmtRisk(summary.average_risk_score)} icon={TrendingUp}    accentClass="border-l-accent"     />
        <StatCard label="High Severity"     value={summary.high_severity_count}      icon={AlertTriangle} accentClass="border-l-sev-high"   />
        <StatCard label="Most Common Type"  value={fmtName(summary.most_common_type)} icon={BarChart3}     accentClass="border-l-blue-500"   />
      </div>

      {/* Time-series */}
      <ChartSection title="Incidents per Day" subtitle="Last 30 days">
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={timeseries} margin={{ top: 8, right: 16, left: -10, bottom: 4 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={CHART_THEME.grid} />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 11, fill: CHART_THEME.axis }}
              tickFormatter={(d) => d.slice(5)}
              interval={4}
            />
            <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: CHART_THEME.axis }} width={28} />
            <Tooltip {...TOOLTIP_STYLE} />
            <Line
              type="monotone"
              dataKey="count"
              stroke={CHART_THEME.accent}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: CHART_THEME.accent }}
            />
          </LineChart>
        </ResponsiveContainer>
      </ChartSection>

      {/* By Type + By Severity */}
      <div className="grid grid-cols-2 gap-4">
        <ChartSection title="By Incident Type">
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={summary.by_type} margin={{ top: 8, right: 8, left: -10, bottom: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={CHART_THEME.grid} />
              <XAxis dataKey="name" tick={{ fontSize: 11, fill: CHART_THEME.axis }} tickFormatter={fmtName} />
              <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: CHART_THEME.axis }} width={28} />
              <Tooltip {...TOOLTIP_STYLE} formatter={(v, _n, p) => [v, fmtName(p.payload.name)]} />
              <Bar dataKey="count" fill={CHART_THEME.accent} radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartSection>

        <ChartSection title="By Severity">
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={summary.by_severity} margin={{ top: 8, right: 8, left: -10, bottom: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={CHART_THEME.grid} />
              <XAxis dataKey="name" tick={{ fontSize: 11, fill: CHART_THEME.axis }} tickFormatter={fmtName} />
              <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: CHART_THEME.axis }} width={28} />
              <Tooltip {...TOOLTIP_STYLE} formatter={(v, _n, p) => [v, fmtName(p.payload.name)]} />
              <Bar dataKey="count" fill={CHART_THEME.high} radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartSection>
      </div>

      {/* Risk distribution */}
      <ChartSection
        title="Risk Score Distribution"
        subtitle="AI-processed incidents by risk range (0 = low, 100 = critical)"
      >
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={riskDist} margin={{ top: 8, right: 16, left: -10, bottom: 4 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={CHART_THEME.grid} />
            <XAxis dataKey="bucket" tick={{ fontSize: 11, fill: CHART_THEME.axis }} />
            <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: CHART_THEME.axis }} width={28} />
            <Tooltip {...TOOLTIP_STYLE} formatter={(v) => [v, 'Incidents']} />
            <Bar dataKey="count" fill={CHART_THEME.high} radius={[3, 3, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartSection>

    </div>
  )
}

export default AnalyticsView
