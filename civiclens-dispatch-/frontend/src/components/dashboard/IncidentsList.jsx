import { useState, useEffect, useMemo, useCallback } from 'react'
import { Search, X, RefreshCw, ClipboardList, AlertTriangle, Filter, ArrowUpDown } from 'lucide-react'

import { getIncidents }   from '../../api/client'
import IncidentTable      from './IncidentTable'
import { EmptyState }     from '../ui/EmptyState'
import { Skeleton }       from '../ui/Skeleton'
import { Button }         from '../ui/Button'
import { Select }         from '../ui/Select'
import { cn }             from '../../lib/cn'
import useAutoRefresh     from '../../hooks/useAutoRefresh'
import useDebounce        from '../../hooks/useDebounce'

const TYPE_OPTIONS = [
  { value: 'all',            label: 'All Types'      },
  { value: 'fire',           label: 'Fire'           },
  { value: 'medical',        label: 'Medical'        },
  { value: 'police',         label: 'Police'         },
  { value: 'crime',          label: 'Crime'          },
  { value: 'infrastructure', label: 'Infrastructure' },
  { value: 'other',          label: 'Other'          },
]

const SORT_OPTIONS = [
  { value: 'created_at_desc',    label: 'Newest First'        },
  { value: 'created_at_asc',     label: 'Oldest First'        },
  { value: 'risk_score_desc',    label: 'Highest Risk'        },
  { value: 'risk_score_asc',     label: 'Lowest Risk'         },
  { value: 'severity_desc',      label: 'Severity ↓'          },
  { value: 'incident_type_asc',  label: 'Type (A→Z)'          },
]

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
    const hrs = Math.floor(mins / 60)
    if (hrs < 24) return `${hrs}h ago`
    return `${Math.floor(hrs / 24)}d ago`
  }

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('desc')
    }
  }

  const handleSortSelect = (val) => {
    const parts = val.split('_')
    const dir   = parts.pop()
    setSortField(parts.join('_'))
    setSortDirection(dir)
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
          <Skeleton key={i} className="h-11 w-full" />
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

  const isFiltered = debouncedSearch || filterType !== 'all'
  const sortValue  = `${sortField}_${sortDirection}`

  return (
    <div className="flex flex-col h-full gap-3 overflow-hidden">

      {/* Filter bar */}
      <div className="flex items-center gap-2 flex-shrink-0 flex-wrap">

        {/* Search */}
        <div className="relative flex-1 min-w-48">
          <Search size={13} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-text-muted pointer-events-none" />
          <input
            type="text"
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            onKeyDown={e => { if (e.key === 'Escape') setSearchTerm('') }}
            placeholder="Search incidents…"
            aria-label="Search incidents"
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

        {/* Filter + Sort grouped in a single pill */}
        <div className="flex items-center bg-surface-2 border border-border rounded-xl overflow-visible">
          <Select
            value={filterType}
            onChange={setFilterType}
            options={TYPE_OPTIONS}
            icon={Filter}
            compact
          />
          <div className="w-px h-5 bg-border flex-shrink-0 mx-0.5" />
          <Select
            value={sortValue}
            onChange={handleSortSelect}
            options={SORT_OPTIONS}
            icon={ArrowUpDown}
            compact
          />
        </div>

        {/* Count + refresh */}
        <div className="flex items-center gap-2 ml-auto flex-shrink-0">
          <span className={cn(
            'text-caption tabular-nums px-2 py-0.5 rounded-full',
            isFiltered
              ? 'bg-accent/10 text-accent border border-accent/30'
              : 'text-text-muted',
          )}>
            {isFiltered
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
