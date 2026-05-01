import { MapPin, ChevronDown, ChevronUp } from 'lucide-react'
import { Badge } from '../ui/Badge'
import { RiskBar } from '../ui/RiskBar'
import { cn } from '../../lib/cn'

const SEVERITY_VARIANT = {
  critical: 'critical',
  high:     'high',
  medium:   'medium',
  low:      'low',
}

const TYPE_VARIANT = {
  fire:           'fire',
  medical:        'info',
  police:         'medium',
  crime:          'crime',
  infrastructure: 'default',
  other:          'default',
}

const SEVERITY_BORDER = {
  critical: 'border-l-red-500',
  high:     'border-l-red-500',
  medium:   'border-l-amber-500',
  low:      'border-l-slate-600',
}

function formatTimeAgo(dateString) {
  if (!dateString) return '—'
  const secs = Math.floor((Date.now() - new Date(dateString).getTime()) / 1000)
  if (secs < 60)   return `${secs}s ago`
  const mins = Math.floor(secs / 60)
  if (mins < 60)   return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24)    return `${hrs}h ago`
  const days = Math.floor(hrs / 24)
  if (days < 30)   return `${days}d ago`
  return new Date(dateString).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

function formatAbsolute(dateString) {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleString('en-US', {
    month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit',
  })
}

function SortableHeader({ field, label, currentField, direction, onSort, className }) {
  const isActive = currentField === field
  const Icon = direction === 'asc' ? ChevronUp : ChevronDown
  return (
    <th
      className={cn(
        'px-3 py-2.5 text-left text-label text-text-muted uppercase tracking-widest',
        'cursor-pointer select-none whitespace-nowrap',
        'hover:text-text-secondary transition-colors',
        isActive && 'text-text-primary',
        className,
      )}
      onClick={() => onSort(field)}
      aria-sort={isActive ? (direction === 'asc' ? 'ascending' : 'descending') : 'none'}
    >
      <span className="inline-flex items-center gap-1">
        {label}
        {isActive && <Icon size={10} className="text-accent" />}
      </span>
    </th>
  )
}

const IncidentTable = ({ incidents, selectedIncidentId, onSelectIncident, sortField, sortDirection, onSort }) => {
  return (
    <div className="overflow-auto h-full rounded-lg border border-border">
      <table className="w-full border-collapse text-body">

        <thead className="sticky top-0 z-10 bg-surface border-b border-border">
          <tr>
            <th className="px-3 py-2.5 text-left text-label text-text-muted uppercase tracking-widest w-16">ID</th>
            <SortableHeader field="incident_type" label="Type"     currentField={sortField} direction={sortDirection} onSort={onSort} />
            <th className="px-3 py-2.5 text-left text-label text-text-muted uppercase tracking-widest">Description</th>
            <th className="px-3 py-2.5 text-left text-label text-text-muted uppercase tracking-widest">Location</th>
            <SortableHeader field="severity"    label="Severity"  currentField={sortField} direction={sortDirection} onSort={onSort} className="w-24" />
            <SortableHeader field="risk_score"  label="Risk"      currentField={sortField} direction={sortDirection} onSort={onSort} className="w-32" />
            <SortableHeader field="created_at"  label="Time"      currentField={sortField} direction={sortDirection} onSort={onSort} className="w-24" />
          </tr>
        </thead>

        <tbody className="divide-y divide-border">
          {incidents.map((incident) => {
            const isSelected   = incident.id === selectedIncidentId
            const riskPct      = incident.risk_score != null ? Math.round(incident.risk_score * 100) : null
            const sevKey       = incident.severity?.toLowerCase()
            const severityBorder = SEVERITY_BORDER[sevKey] ?? 'border-l-border'

            return (
              <tr
                key={incident.id}
                onClick={() => onSelectIncident(incident)}
                className={cn(
                  'cursor-pointer transition-all duration-150',
                  'border-l-2',
                  isSelected
                    ? 'bg-surface-2 border-l-accent'
                    : cn('hover:bg-surface-2/60', severityBorder),
                )}
              >
                {/* ID */}
                <td className="px-3 py-2.5 font-mono text-caption text-text-muted tabular-nums whitespace-nowrap">
                  #{String(incident.id).padStart(4, '0')}
                </td>

                {/* Type */}
                <td className="px-3 py-2.5">
                  {incident.incident_type ? (
                    <Badge variant={TYPE_VARIANT[incident.incident_type.toLowerCase()] ?? 'default'}>
                      {incident.incident_type}
                    </Badge>
                  ) : (
                    <span className="text-text-muted text-caption">—</span>
                  )}
                </td>

                {/* Description */}
                <td className="px-3 py-2.5 max-w-0">
                  <p
                    className="truncate text-body text-text-secondary"
                    title={incident.description}
                  >
                    {incident.description}
                  </p>
                </td>

                {/* Location */}
                <td className="px-3 py-2.5 max-w-0">
                  <span className="flex items-center gap-1 min-w-0">
                    <MapPin size={11} className="text-text-muted flex-shrink-0" />
                    <span className="truncate text-body text-text-secondary" title={incident.location}>
                      {incident.location || '—'}
                    </span>
                  </span>
                </td>

                {/* Severity */}
                <td className="px-3 py-2.5">
                  {incident.severity ? (
                    <Badge variant={SEVERITY_VARIANT[incident.severity.toLowerCase()] ?? 'default'} dot>
                      {incident.severity}
                    </Badge>
                  ) : (
                    <span className="text-text-muted text-caption">—</span>
                  )}
                </td>

                {/* Risk */}
                <td className="px-3 py-2.5">
                  {riskPct != null ? (
                    <RiskBar score={riskPct} />
                  ) : (
                    <span className="text-text-muted text-caption">—</span>
                  )}
                </td>

                {/* Time */}
                <td className="px-3 py-2.5 whitespace-nowrap">
                  <span
                    className="text-caption text-text-muted tabular-nums"
                    title={formatAbsolute(incident.created_at)}
                  >
                    {formatTimeAgo(incident.created_at)}
                  </span>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

export default IncidentTable
