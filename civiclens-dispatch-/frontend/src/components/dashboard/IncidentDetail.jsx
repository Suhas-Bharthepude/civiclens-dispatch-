import { useState, useEffect, useRef } from 'react'
import {
  MapPin, Clock, Mic, FileImage, Headphones,
  RefreshCw, Trash2, X, AlertTriangle, CheckCircle2,
  Zap, RotateCcw, Bot, ClipboardList,
} from 'lucide-react'

import { updateIncidentStatus, reprocessIncident, deleteIncident } from '../../api/client'
import { Badge }      from '../ui/Badge'
import { RiskBar }    from '../ui/RiskBar'
import { Button }     from '../ui/Button'
import { EmptyState } from '../ui/EmptyState'
import { cn }         from '../../lib/cn'

const SEVERITY_VARIANT = { critical: 'critical', high: 'high', medium: 'medium', low: 'low' }
const STATUS_VARIANT   = { pending: 'pending',  active: 'active', resolved: 'resolved' }

function SectionHeading({ icon: Icon, children }) {
  return (
    <div className="flex items-center gap-2 pt-4 pb-1 border-t border-border mt-2">
      <Icon size={13} className="text-text-muted flex-shrink-0" />
      <span className="text-label text-text-muted uppercase tracking-widest">{children}</span>
    </div>
  )
}

function Field({ label, children, aiBadge = false }) {
  return (
    <div className="flex flex-col gap-1">
      <span className="text-label text-text-muted uppercase tracking-widest flex items-center gap-1.5">
        {label}
        {aiBadge && <Badge variant="info" className="text-[10px] py-0 px-1.5">AI</Badge>}
      </span>
      <div className="text-body text-text-primary">{children}</div>
    </div>
  )
}

function TranscriptPanel({ incident }) {
  if (!incident.audio_path) return null

  if (!incident.transcript) {
    return (
      <div className="rounded-lg bg-surface-2 border border-border p-3 flex items-start gap-2">
        <Mic size={13} className="text-text-muted flex-shrink-0 mt-0.5" />
        <div>
          <p className="text-body text-text-secondary">Transcription in progress…</p>
          <p className="text-caption text-text-muted mt-0.5">Refresh in a moment to see the result.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="rounded-lg bg-surface-2 border border-border p-3">
      <div className="flex items-center gap-1.5 mb-2">
        <Mic size={13} className="text-text-muted" />
        <span className="text-label text-text-muted uppercase tracking-widest">Transcript</span>
        <Badge variant="info" className="text-[10px] py-0 px-1.5">AI</Badge>
      </div>
      <blockquote className="text-body text-text-secondary italic border-l-2 border-border pl-3">
        {incident.transcript}
      </blockquote>
      <p className="text-caption text-text-muted mt-2">Auto-transcribed — verify before acting.</p>
    </div>
  )
}

function StatusActions({ currentStatus, isUpdating, onUpdate }) {
  return (
    <div className="flex gap-2 flex-wrap">
      {currentStatus === 'pending' && (
        <Button variant="primary" size="sm" icon={Zap} loading={isUpdating} onClick={() => onUpdate('active')}>
          Mark Active
        </Button>
      )}
      {(currentStatus === 'pending' || currentStatus === 'active') && (
        <Button
          variant={currentStatus === 'active' ? 'primary' : 'secondary'}
          size="sm"
          icon={CheckCircle2}
          loading={isUpdating}
          onClick={() => onUpdate('resolved')}
        >
          Resolve
        </Button>
      )}
      {currentStatus === 'resolved' && (
        <Button variant="secondary" size="sm" icon={RotateCcw} loading={isUpdating} onClick={() => onUpdate('pending')}>
          Reopen
        </Button>
      )}
    </div>
  )
}

const IncidentDetail = ({ incident, onClose, onStatusChange, onDeleted, userRole, showToast }) => {
  const [isUpdating, setIsUpdating] = useState(false)
  const [updateError, setUpdateError] = useState(null)
  const [visible, setVisible] = useState(false)
  const prevIdRef = useRef(null)

  useEffect(() => {
    if (!incident) { setVisible(false); return }
    if (incident.id !== prevIdRef.current) {
      setVisible(false)
      const t = setTimeout(() => setVisible(true), 40)
      prevIdRef.current = incident.id
      return () => clearTimeout(t)
    }
    setVisible(true)
  }, [incident])

  const handleStatusChange = async (newStatus) => {
    setUpdateError(null)
    setIsUpdating(true)
    const previousStatus = incident.status
    onStatusChange(incident.id, newStatus)
    try {
      await updateIncidentStatus(incident.id, newStatus)
      showToast?.(`Incident #${String(incident.id).padStart(4, '0')} marked ${newStatus}`, 'success')
    } catch (err) {
      onStatusChange(incident.id, previousStatus)
      setUpdateError(`Failed to update: ${err.message}`)
    } finally {
      setIsUpdating(false)
    }
  }

  const handleDelete = async () => {
    if (!window.confirm(`Permanently delete incident #${incident.id}? This cannot be undone.`)) return
    setIsUpdating(true)
    setUpdateError(null)
    try {
      await deleteIncident(incident.id)
      showToast?.(`Incident #${String(incident.id).padStart(4, '0')} deleted`, 'info')
      onDeleted?.()
    } catch (err) {
      setUpdateError(`Delete failed: ${err.message}`)
    } finally {
      setIsUpdating(false)
    }
  }

  const handleReprocess = async () => {
    try {
      await reprocessIncident(incident.id)
      showToast?.(`Reprocessing queued for #${String(incident.id).padStart(4, '0')}`, 'info')
    } catch (err) {
      showToast?.(`Failed to reprocess: ${err.message}`, 'error')
    }
  }

  const formatDate = (str) => {
    if (!str) return 'Unknown'
    return new Date(str).toLocaleString('en-US', {
      month: 'short', day: 'numeric', year: 'numeric',
      hour: 'numeric', minute: '2-digit',
    })
  }

  if (!incident) {
    return (
      <div className="h-full flex items-center justify-center bg-surface border border-border rounded-xl">
        <EmptyState
          icon={ClipboardList}
          title="No incident selected"
          description="Select an incident from the list to view details, AI analysis, and attached media."
        />
      </div>
    )
  }

  const riskPct = incident.risk_score != null ? Math.round(incident.risk_score * 100) : null

  return (
    <div className="h-full flex flex-col bg-surface border border-border rounded-xl overflow-hidden">

      {/* Header */}
      <div className="flex items-start justify-between px-5 py-4 border-b border-border flex-shrink-0 bg-surface-2/40">
        <div className="flex flex-col gap-2 min-w-0 flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-mono text-label text-text-muted">
              #{String(incident.id).padStart(4, '0')}
            </span>
            {incident.incident_type && (
              <Badge variant={
                incident.incident_type.toLowerCase() === 'fire' ? 'fire' :
                incident.incident_type.toLowerCase() === 'crime' ? 'crime' :
                (SEVERITY_VARIANT[incident.incident_type.toLowerCase()] ?? 'default')
              }>
                {incident.incident_type}
              </Badge>
            )}
            <Badge variant={STATUS_VARIANT[incident.status] ?? 'pending'} dot>
              {incident.status ?? 'pending'}
            </Badge>
          </div>
          {riskPct != null && <RiskBar score={riskPct} />}
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-text-muted hover:text-text-primary hover:bg-surface-2 transition-colors flex-shrink-0 ml-2"
          aria-label="Close"
        >
          <X size={15} />
        </button>
      </div>

      {/* Scrollable content with fade-in on incident switch */}
      <div
        className={cn(
          'flex-1 overflow-y-auto px-5 py-4 flex flex-col gap-3.5',
          'transition-opacity duration-200',
          visible ? 'opacity-100' : 'opacity-0',
        )}
      >
        <Field label="Description">{incident.description}</Field>

        <Field label="Location">
          <span className="flex items-center gap-1.5">
            <MapPin size={12} className="text-text-muted flex-shrink-0" />
            {incident.location || 'Not specified'}
          </span>
        </Field>

        <Field label="Reported By">
          {incident.source
            ? incident.source.charAt(0).toUpperCase() + incident.source.slice(1)
            : 'Unknown'}
        </Field>

        <Field label="Reported At">
          <span className="flex items-center gap-1.5">
            <Clock size={12} className="text-text-muted flex-shrink-0" />
            {formatDate(incident.created_at)}
          </span>
        </Field>

        {/* AI Analysis section */}
        <SectionHeading icon={Bot}>AI Analysis</SectionHeading>

        <Field label="Incident Type" aiBadge>
          {incident.incident_type
            ? <Badge variant={
                incident.incident_type.toLowerCase() === 'fire' ? 'fire' :
                incident.incident_type.toLowerCase() === 'crime' ? 'crime' :
                (SEVERITY_VARIANT[incident.incident_type.toLowerCase()] ?? 'default')
              }>{incident.incident_type}</Badge>
            : <span className="text-text-muted">Not classified</span>
          }
        </Field>

        <Field label="Severity" aiBadge>
          {incident.severity
            ? <Badge variant={SEVERITY_VARIANT[incident.severity.toLowerCase()] ?? 'medium'} dot>{incident.severity}</Badge>
            : <Badge variant="medium" dot>Medium</Badge>
          }
        </Field>

        {riskPct != null && (
          <Field label="Risk Score" aiBadge>
            <RiskBar score={riskPct} />
          </Field>
        )}

        {incident.summary && (
          <Field label="AI Summary" aiBadge>
            <p className="text-text-secondary leading-relaxed">{incident.summary}</p>
          </Field>
        )}

        {incident.image_caption && !incident.image_caption.startsWith('[') && (
          <Field label="Image Analysis" aiBadge>
            <p className="text-text-secondary">{incident.image_caption}</p>
          </Field>
        )}

        {/* Audio section */}
        {incident.audio_path && (
          <>
            <SectionHeading icon={Mic}>Audio</SectionHeading>
            <TranscriptPanel incident={incident} />
          </>
        )}

        {/* Attached files */}
        {(incident.audio_path || incident.image_path) && (
          <>
            <SectionHeading icon={FileImage}>Attached Files</SectionHeading>
            {incident.audio_path && (
              <Field label="Audio File">
                <span className="flex items-center gap-1.5 text-text-secondary">
                  <Headphones size={12} className="text-text-muted" />
                  {incident.audio_path.split('/').pop()}
                </span>
              </Field>
            )}
            {incident.image_path && (
              <Field label="Photo">
                <span className="flex items-center gap-1.5 text-text-secondary">
                  <FileImage size={12} className="text-text-muted" />
                  {incident.image_path.split('/').pop()}
                </span>
              </Field>
            )}
          </>
        )}
      </div>

      {/* Footer */}
      <div className="px-5 py-3 border-t border-border flex-shrink-0 flex flex-col gap-2 bg-surface-2/30">
        {updateError && (
          <div className={cn(
            'flex items-center gap-2 px-3 py-2 rounded-lg text-body',
            'bg-red-950/60 border border-red-800 text-red-300',
          )}>
            <AlertTriangle size={13} className="flex-shrink-0" />
            <span className="flex-1">{updateError}</span>
            <button onClick={() => setUpdateError(null)} className="flex-shrink-0 hover:opacity-70">
              <X size={13} />
            </button>
          </div>
        )}

        <div className="flex items-center gap-2 flex-wrap">
          <StatusActions
            currentStatus={incident.status || 'pending'}
            isUpdating={isUpdating}
            onUpdate={handleStatusChange}
          />
          <Button variant="ghost" size="sm" icon={RefreshCw} onClick={handleReprocess}>
            Reprocess
          </Button>
          {userRole === 'admin' && (
            <Button variant="danger" size="sm" icon={Trash2} loading={isUpdating} onClick={handleDelete}>
              Delete
            </Button>
          )}
          <Button variant="ghost" size="sm" onClick={onClose} className="ml-auto">
            Close
          </Button>
        </div>
      </div>
    </div>
  )
}

export default IncidentDetail
