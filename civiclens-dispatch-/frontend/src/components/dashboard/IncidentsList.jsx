import { useState, useEffect, useMemo, useCallback } from 'react'
import { Search, X, RefreshCw, ClipboardList, AlertTriangle, Filter } from 'lucide-react'

import { getIncidents }   from '../../api/client'
import IncidentTable      from './IncidentTable'
import { EmptyState }     from '../ui/EmptyState'
import { Skeleton }       from '../ui/Skeleton'
import { Button }         from '../ui/Button'
import { cn }             from '../../lib/cn'
import useAutoRefresh     from '../../hooks/useAutoRefresh'
import useDebounce        from '../../hooks/useDebounce'

const IncidentsList = ({
  onSelectIncident,
  selectedIncidentId,
  refreshTrigger,
  wsUpdate,
  wsConnected,
}) => {
  const [incidents,      setIncidents]      = useState([])
  const [loading,        setLoading]        = useState(true)
  const [error,          setError]          = useState(null)
  const [sortField,      setSortField]      = useState('created_at')
  const [sortDirection,  setSortDirection]  = useState('desc')
  const [filterType,     setFilterType]     = useState('all')
  const [searchTerm,     setSearchTerm]     = useState('')
  const [,               setSecondsTick]    = useState(0)
  const debouncedSearch = useDebounce(searchTerm, 400)

  const fetchIncidents = useCallback(async (isFirstLoad = false) => {
    try {
      if (isFirstLoad) { setLoading(true); setError(null) }
      const filters = {}
      if (debouncedSearch.trim()) filters.search = debouncedSearch.trim()
      const data = await getIncidents(filters)
      setIncidents(data)
      setError(null)
    } catch (err) {
      if (isFirstLoad) setError(err.message || 'Failed to fetch incidents')
      throw err
    } finally {
      setLoading(false)
    }
  }, [debouncedSearch])

  useEffect(() => { fetchIncidents(true) }, [fetchIncidents])
  useEffect(() => { if (refreshTrigger > 0) fetchIncidents(false) }, [refreshTrigger, fetchIncidents])

  useEffect(() => {
    if (!wsUpdate) return
    if (wsUpdate.event === 'incident_created') {
      setIncidents(prev => [wsUpdate.incident, ...prev])
    } else if (wsUpdate.event === 'incident_updated') {
      setIncidents(prev => prev.map(inc => inc.id === wsUpdate.incident.id ? wsUpdate.incident : inc))
    }
  }, [wsUpdate])

  const { isRefreshing, lastUpdated, refreshError, triggerRefresh } =
    useAutoRefresh(fetchIncidents, 30000, !loading && !wsConnected)

  useEffect(() => {
    const id = setInterval(() => setSecondsTick(n => n + 1), 1000)
    return () => clearInterval(id)
  }, [])

  const formatTimeAgo = (date) => {
    if (!date) return 'never'
    const secs = Math.floor((Date.now() - date.getTime()) / 1000)
    if (secs < 5)  return 'just now'
    if (secs < 60) return `${secs}s ago`
    const mins = Math.floor(secs / 60)
    if (mins < 60) return `${mins}m ago`
    return `${Math.floor(mins / 60)}h ago`
  }

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('desc')
    }
  }

  const displayedIncidents = useMemo(() => {
    let result = incidents.filter(inc =>
      filterType === 'all' || inc.incident_type?.toLowerCase() === filterType
    )
    return [...result].sort((a, b) => {
      let valA = a[sortField], valB = b[sortField]
      if (valA == null) return 1
      if (valB == null) return -1
      const cmp = typeof valA === 'string' ? valA.localeCompare(valB) : (valA > valB ? 1 : valA < valB ? -1 : 0)
      return sortDirection === 'asc' ? cmp : -cmp
    })
  }, [incidents, sortField, sortDirection, filterType])

  if (loading) {
    return (
      <div className="flex flex-col gap-2 h-full">
        {[...Array(6)].map((_, i) => (
          <Skeleton key={i} className="h-10 w-full" />
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <EmptyState
        icon={AlertTriangle}
        title="Failed to load incidents"
        description={error}
        action={
          <Button variant="secondary" size="sm" onClick={() => fetchIncidents(true)}>
            Retry
          </Button>
        }
      />
    )
  }

  return (
    <div className="flex flex-col h-full gap-3 overflow-hidden">

      {/* Filter bar */}
      <div className="flex items-center gap-2 flex-shrink-0 flex-wrap">

        {/* Search input */}
        <div className="relative flex-1 min-w-48">
          <Search size={13} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-text-muted pointer-events-none" />
          <input
            type="text"
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            onKeyDown={e => { if (e.key === 'Escape') setSearchTerm('') }}
            placeholder="Search incidents…"
            aria-label="Search incidents by description, location, or transcript"
            className={cn(
              'w-full pl-8 pr-8 py-1.5 text-body',
              'bg-surface-2 border border-border rounded-lg',
              'text-text-primary placeholder:text-text-muted',
              'focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent/30',
              'transition-colors',
            )}
          />
          {searchTerm && (
            <button
              onClick={() => setSearchTerm('')}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-primary transition-colors"
              aria-label="Clear search"
            >
              <X size={13} />
            </button>
          )}
        </div>

        {/* Type filter */}
        <div className="relative">
          <Filter size={12} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-text-muted pointer-events-none" />
          <select
            value={filterType}
            onChange={e => setFilterType(e.target.value)}
            className={cn(
              'pl-7 pr-6 py-1.5 text-body appearance-none',
              'bg-surface-2 border border-border rounded-lg',
              'text-text-primary',
              'focus:outline-none focus:border-accent',
              'cursor-pointer',
            )}
          >
            <option value="all">All Types</option>
            <option value="fire">Fire</option>
            <option value="medical">Medical</option>
            <option value="police">Police</option>
            <option value="crime">Crime</option>
            <option value="infrastructure">Infrastructure</option>
            <option value="other">Other</option>
          </select>
        </div>

        {/* Sort */}
        <select
          value={`${sortField}_${sortDirection}`}
          onChange={e => {
            const parts = e.target.value.split('_')
            const dir   = parts.pop()
            setSortField(parts.join('_'))
            setSortDirection(dir)
          }}
          className={cn(
            'px-3 py-1.5 text-body appearance-none',
            'bg-surface-2 border border-border rounded-lg',
            'text-text-primary',
            'focus:outline-none focus:border-accent',
            'cursor-pointer',
          )}
        >
          <option value="created_at_desc">Newest First</option>
          <option value="created_at_asc">Oldest First</option>
          <option value="risk_score_desc">Highest Risk</option>
          <option value="risk_score_asc">Lowest Risk</option>
          <option value="severity_desc">Severity (High→Low)</option>
          <option value="incident_type_asc">Type (A→Z)</option>
        </select>

        {/* Right side: count + refresh */}
        <div className="flex items-center gap-2 ml-auto flex-shrink-0">
          <span className="text-caption text-text-muted tabular-nums">
            {debouncedSearch || filterType !== 'all'
              ? `${displayedIncidents.length} / ${incidents.length}`
              : `${incidents.length} incident${incidents.length !== 1 ? 's' : ''}`
            }
          </span>

          {isRefreshing ? (
            <RefreshCw size={13} className="text-text-muted animate-spin" />
          ) : (
            <button
              onClick={triggerRefresh}
              className="text-text-muted hover:text-text-secondary transition-colors"
              title={`Last updated ${formatTimeAgo(lastUpdated)}`}
            >
              <RefreshCw size={13} />
            </button>
          )}

          {refreshError && (
            <span className="text-caption text-red-400">Refresh failed</span>
          )}
        </div>
      </div>

      {/* Empty state */}
      {displayedIncidents.length === 0 && (
        debouncedSearch ? (
          <EmptyState
            icon={Search}
            title={`No results for "${debouncedSearch}"`}
            description="Try different keywords or clear the search."
            action={<Button variant="ghost" size="sm" onClick={() => setSearchTerm('')}>Clear Search</Button>}
          />
        ) : filterType !== 'all' ? (
          <EmptyState
            icon={Filter}
            title={`No ${filterType} incidents`}
            description="Try a different type filter."
            action={<Button variant="ghost" size="sm" onClick={() => setFilterType('all')}>Clear Filter</Button>}
          />
        ) : (
          <EmptyState
            icon={ClipboardList}
            title="No incidents yet"
            description="Submit an incident using the New Incident button."
          />
        )
      )}

      {/* Table */}
      {displayedIncidents.length > 0 && (
        <div className="flex-1 overflow-hidden min-h-0">
          <IncidentTable
            incidents={displayedIncidents}
            selectedIncidentId={selectedIncidentId}
            onSelectIncident={onSelectIncident}
            sortField={sortField}
            sortDirection={sortDirection}
            onSort={handleSort}
          />
        </div>
      )}
    </div>
  )
}

export default IncidentsList
