// frontend/src/components/analytics/AnalyticsView.jsx
// Analytics dashboard showing aggregate incident statistics.
//
// Day 70: Analytics page — summary cards, time-series line chart,
//          type/severity bar charts, risk-score histogram.
//
// Data is fetched from three backend endpoints in parallel on mount.
// Each chart uses recharts with a ResponsiveContainer so they scale
// with the viewport rather than having fixed pixel widths.

import { useState, useEffect } from 'react'
import {
  LineChart, Line,
  BarChart, Bar,
  XAxis, YAxis,
  CartesianGrid, Tooltip,
  ResponsiveContainer,
} from 'recharts'

import {
  getAnalyticsSummary,
  getTimeseries,
  getRiskDistribution,
} from '../../api/client'

import './AnalyticsView.css'


// ============================================================
// SUMMARY CARD — reusable KPI tile
// ============================================================
// label: card heading (e.g., "Total Incidents")
// value: the big number or string to display
// accent: optional CSS class suffix for colour coding
const SummaryCard = ({ label, value, accent }) => (
  <div className={`analytics-card analytics-card--${accent || 'default'}`}>
    <div className="analytics-card__value">{value}</div>
    <div className="analytics-card__label">{label}</div>
  </div>
)


// ============================================================
// MAIN COMPONENT
// ============================================================
const AnalyticsView = () => {

  // ── DATA STATE ───────────────────────────────────────────
  // summary: KPI numbers + by_type[] + by_severity[] from /summary
  const [summary,    setSummary]    = useState(null)
  // timeseries: [{date, count}] from /timeseries
  const [timeseries, setTimeseries] = useState([])
  // riskDist: [{bucket, count}] from /risk-distribution
  const [riskDist,   setRiskDist]   = useState([])

  // ── UI STATE ─────────────────────────────────────────────
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState(null)


  // ── FETCH ALL THREE ENDPOINTS IN PARALLEL ────────────────
  // Promise.all ensures we only show the view once ALL data is ready.
  // A single endpoint failure sets the error state instead of a partial render.
  useEffect(() => {
    const fetchAll = async () => {
      setLoading(true)
      setError(null)
      try {
        // All three requests fire simultaneously — total time = slowest request
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
  }, []) // Only fetch once on mount — analytics are not real-time


  // ── LOADING STATE ────────────────────────────────────────
  if (loading) {
    return (
      <div className="analytics-view analytics-view--loading">
        <div className="analytics-loading-spinner" />
        <p className="analytics-loading-text">Loading analytics…</p>
      </div>
    )
  }

  // ── ERROR STATE ──────────────────────────────────────────
  if (error) {
    return (
      <div className="analytics-view analytics-view--error">
        <p className="analytics-error-icon">⚠️</p>
        <p className="analytics-error-message">Failed to load analytics</p>
        <p className="analytics-error-detail">{error}</p>
      </div>
    )
  }

  // ── EMPTY STATE ──────────────────────────────────────────
  // No incidents have been created yet
  if (!summary || summary.total_incidents === 0) {
    return (
      <div className="analytics-view analytics-view--empty">
        <p className="analytics-empty-icon">📊</p>
        <p className="analytics-empty-message">No incidents yet</p>
        <p className="analytics-empty-hint">Submit an incident to see analytics data</p>
      </div>
    )
  }


  // ── FORMAT HELPERS ────────────────────────────────────────
  // Convert 0.0–1.0 to "65.0%" for the average risk card
  const fmtRisk = (v) => `${(v * 100).toFixed(1)}%`
  // Capitalise first letter of a type/severity string
  const fmtName = (s) => s ? s.charAt(0).toUpperCase() + s.slice(1) : '—'


  // ── MAIN RENDER ───────────────────────────────────────────
  return (
    <div className="analytics-view">

      {/* ── SECTION HEADER ────────────────────────────────── */}
      <div className="analytics-header">
        <h2 className="analytics-title">📊 Incident Analytics</h2>
        <p className="analytics-subtitle">Aggregate statistics across all incidents</p>
      </div>

      {/* ── SUMMARY CARDS ─────────────────────────────────── */}
      {/* 4 KPI tiles in a responsive row */}
      <div className="analytics-cards">
        <SummaryCard
          label="Total Incidents"
          value={summary.total_incidents}
          accent="total"
        />
        <SummaryCard
          label="Avg Risk Score"
          value={fmtRisk(summary.average_risk_score)}
          accent="risk"
        />
        <SummaryCard
          label="High Severity"
          value={summary.high_severity_count}
          accent="high"
        />
        <SummaryCard
          label="Most Common Type"
          value={fmtName(summary.most_common_type)}
          accent="type"
        />
      </div>

      {/* ── TIME-SERIES LINE CHART ─────────────────────────── */}
      {/* Shows incidents per day over the last 30 days */}
      <div className="analytics-chart-section">
        <h3 className="analytics-chart-title">Incidents per Day (Last 30 Days)</h3>

        {/* ResponsiveContainer stretches the chart to fill its parent width */}
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={timeseries} margin={{ top: 8, right: 16, left: -10, bottom: 4 }}>
            {/* Subtle grid lines help the eye track values */}
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            {/* X axis: show every 5th date to avoid crowding */}
            <XAxis
              dataKey="date"
              tick={{ fontSize: 11, fill: '#94a3b8' }}
              tickFormatter={(d) => d.slice(5)} // "MM-DD" instead of "YYYY-MM-DD"
              interval={4}
            />
            <YAxis
              allowDecimals={false}
              tick={{ fontSize: 11, fill: '#94a3b8' }}
              width={28}
            />
            <Tooltip
              contentStyle={{ fontSize: 12, borderRadius: 6, border: '1px solid #e2e8f0' }}
              labelStyle={{ fontWeight: 600 }}
            />
            <Line
              type="monotone"
              dataKey="count"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={false}      // Skip dots for a cleaner 30-day line
              activeDot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* ── SIDE-BY-SIDE BAR CHARTS ────────────────────────── */}
      {/* By Type | By Severity, each in a 50% column */}
      <div className="analytics-bar-row">

        {/* Incidents by Type */}
        <div className="analytics-chart-section analytics-chart-section--half">
          <h3 className="analytics-chart-title">By Incident Type</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart
              data={summary.by_type}
              margin={{ top: 8, right: 8, left: -10, bottom: 4 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis
                dataKey="name"
                tick={{ fontSize: 11, fill: '#94a3b8' }}
                tickFormatter={fmtName}
              />
              <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: '#94a3b8' }} width={28} />
              <Tooltip
                contentStyle={{ fontSize: 12, borderRadius: 6, border: '1px solid #e2e8f0' }}
                formatter={(v, _n, p) => [v, fmtName(p.payload.name)]}
              />
              {/* Blue bars match the line chart colour for visual consistency */}
              <Bar dataKey="count" fill="#3b82f6" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Incidents by Severity */}
        <div className="analytics-chart-section analytics-chart-section--half">
          <h3 className="analytics-chart-title">By Severity</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart
              data={summary.by_severity}
              margin={{ top: 8, right: 8, left: -10, bottom: 4 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis
                dataKey="name"
                tick={{ fontSize: 11, fill: '#94a3b8' }}
                tickFormatter={fmtName}
              />
              <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: '#94a3b8' }} width={28} />
              <Tooltip
                contentStyle={{ fontSize: 12, borderRadius: 6, border: '1px solid #e2e8f0' }}
                formatter={(v, _n, p) => [v, fmtName(p.payload.name)]}
              />
              {/* Orange bars visually distinguish severity from type */}
              <Bar dataKey="count" fill="#f59e0b" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

      </div>
      {/* END side-by-side bar charts */}

      {/* ── RISK SCORE HISTOGRAM ───────────────────────────── */}
      {/* Shows distribution of AI risk scores in 20-point buckets */}
      <div className="analytics-chart-section">
        <h3 className="analytics-chart-title">Risk Score Distribution</h3>
        <p className="analytics-chart-subtitle">
          Count of AI-processed incidents in each risk-score range (0 = low, 100 = critical)
        </p>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart
            data={riskDist}
            margin={{ top: 8, right: 16, left: -10, bottom: 4 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="bucket" tick={{ fontSize: 11, fill: '#94a3b8' }} />
            <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: '#94a3b8' }} width={28} />
            <Tooltip
              contentStyle={{ fontSize: 12, borderRadius: 6, border: '1px solid #e2e8f0' }}
              formatter={(v) => [v, 'Incidents']}
            />
            {/* Red-tinted bars signal that higher buckets are more critical */}
            <Bar dataKey="count" fill="#ef4444" radius={[3, 3, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

    </div>
  )
}

export default AnalyticsView
