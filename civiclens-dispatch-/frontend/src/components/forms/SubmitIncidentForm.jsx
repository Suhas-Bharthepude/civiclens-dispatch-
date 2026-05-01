import { useState } from 'react'
import { Mic, Image, Send, Loader2, RotateCcw, MapPin, CheckCircle2, AlertCircle, X } from 'lucide-react'

import { createIncident, uploadAudio, uploadImage } from '../../api/client'
import { Button }   from '../ui/Button'
import { cn }       from '../../lib/cn'

const INPUT_CLASS = cn(
  'w-full px-3 py-2 text-body rounded-lg',
  'bg-surface-2 border border-border',
  'text-text-primary placeholder:text-text-muted',
  'focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent/30',
  'transition-colors',
)

const LABEL_CLASS = 'text-caption text-text-muted uppercase tracking-widest'

function FormField({ id, label, required, hint, children }) {
  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={id} className={LABEL_CLASS}>
        {label}{required && <span className="text-red-400 ml-0.5">*</span>}
      </label>
      {children}
      {hint && <p className="text-caption text-text-muted">{hint}</p>}
    </div>
  )
}

function FileDropZone({ id, name, accept, file, onClear, onChange, icon: Icon, placeholder, hint }) {
  return (
    <div className="flex flex-col gap-1.5">
      {file ? (
        <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-surface-2 border border-border">
          <Icon size={14} className="text-accent flex-shrink-0" />
          <span className="text-body text-text-primary flex-1 truncate">{file.name}</span>
          <span className="text-caption text-text-muted whitespace-nowrap">
            {(file.size / 1024).toFixed(1)} KB
          </span>
          <button onClick={onClear} className="text-text-muted hover:text-text-primary transition-colors">
            <X size={14} />
          </button>
        </div>
      ) : (
        <label
          htmlFor={id}
          className={cn(
            'flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer',
            'bg-surface-2 border border-dashed border-border',
            'text-text-muted hover:border-accent hover:text-text-secondary',
            'transition-colors',
          )}
        >
          <Icon size={14} />
          <span className="text-body">{placeholder}</span>
          <input
            id={id}
            name={name}
            type="file"
            accept={accept}
            onChange={onChange}
            className="sr-only"
          />
        </label>
      )}
      {hint && <p className="text-caption text-text-muted">{hint}</p>}
    </div>
  )
}

function SubmitIncidentForm({ onSubmitted }) {
  const [formData, setFormData] = useState({
    source: '', sourceOther: '', description: '', location: '',
  })
  const [audioFile,     setAudioFile]     = useState(null)
  const [imageFile,     setImageFile]     = useState(null)
  const [submitting,    setSubmitting]    = useState(false)
  const [submitSuccess, setSubmitSuccess] = useState(false)
  const [submitError,   setSubmitError]   = useState(null)

  function validateForm() {
    setSubmitError(null)
    if (!formData.source)                                      { setSubmitError('Please select a report source'); return false }
    if (formData.source === 'other' && !formData.sourceOther.trim()) { setSubmitError('Please specify the report source'); return false }
    if (formData.description.length < 10)                     { setSubmitError('Description must be at least 10 characters'); return false }
    if (!formData.location.trim())                            { setSubmitError('Location is required'); return false }
    return true
  }

  function handleInputChange(e) {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  function resetForm() {
    setFormData({ source: '', sourceOther: '', description: '', location: '' })
    setAudioFile(null)
    setImageFile(null)
    setSubmitError(null)
    setSubmitSuccess(false)
    const audioInput = document.getElementById('audio')
    const imageInput = document.getElementById('image')
    if (audioInput) audioInput.value = ''
    if (imageInput) imageInput.value = ''
  }

  async function handleSubmit(e) {
    e.preventDefault()
    if (!validateForm()) return

    setSubmitting(true)
    setSubmitError(null)
    setSubmitSuccess(false)

    try {
      const submitData = {
        ...formData,
        source: formData.source === 'other' ? formData.sourceOther.trim() : formData.source,
      }
      delete submitData.sourceOther

      const newIncident = await createIncident(submitData)
      const incidentId  = newIncident.id

      if (audioFile) {
        try { await uploadAudio(incidentId, audioFile) }
        catch (err) { console.error('Audio upload failed:', err) }
      }
      if (imageFile) {
        try { await uploadImage(incidentId, imageFile) }
        catch (err) { console.error('Image upload failed:', err) }
      }

      setSubmitSuccess(true)
      resetForm()
      if (onSubmitted) onSubmitted()
      setTimeout(() => setSubmitSuccess(false), 5000)

    } catch (error) {
      setSubmitError(error.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-5 px-6 py-5">

      {/* Success banner */}
      {submitSuccess && (
        <div className="flex items-start gap-2 px-3 py-2.5 rounded-lg bg-emerald-950/60 border border-emerald-800 text-emerald-300 text-body">
          <CheckCircle2 size={15} className="flex-shrink-0 mt-0.5" />
          Incident submitted successfully. Dispatchers have been notified.
        </div>
      )}

      {/* Error banner */}
      {submitError && (
        <div className="flex items-start gap-2 px-3 py-2.5 rounded-lg bg-red-950/60 border border-red-800 text-red-300 text-body">
          <AlertCircle size={15} className="flex-shrink-0 mt-0.5" />
          <span className="flex-1">{submitError}</span>
          <button type="button" onClick={() => setSubmitError(null)} className="flex-shrink-0 hover:opacity-70">
            <X size={14} />
          </button>
        </div>
      )}

      {/* Source */}
      <FormField id="source" label="Report Source" required>
        <select
          id="source"
          name="source"
          value={formData.source}
          onChange={handleInputChange}
          required
          className={INPUT_CLASS}
        >
          <option value="">— Select Source —</option>
          <option value="citizen">Citizen</option>
          <option value="police">Police</option>
          <option value="dispatcher">Dispatcher</option>
          <option value="sensor">Automated Sensor</option>
          <option value="other">Other</option>
        </select>
        {formData.source === 'other' && (
          <input
            type="text"
            name="sourceOther"
            value={formData.sourceOther}
            onChange={handleInputChange}
            placeholder="Specify source…"
            required
            className={cn(INPUT_CLASS, 'mt-1.5')}
          />
        )}
      </FormField>

      {/* Description */}
      <FormField
        id="description"
        label="Incident Description"
        required
        hint={`${formData.description.length} characters${formData.description.length < 20 ? ' (minimum 20 recommended)' : ''}`}
      >
        <textarea
          id="description"
          name="description"
          value={formData.description}
          onChange={handleInputChange}
          rows={4}
          placeholder="Describe what happened in detail…"
          required
          className={cn(INPUT_CLASS, 'resize-none')}
        />
      </FormField>

      {/* Location */}
      <FormField
        id="location"
        label="Location"
        required
        hint={
          <span className="flex items-center gap-1">
            <MapPin size={11} />
            Be as specific as possible — street address, landmarks, intersections.
          </span>
        }
      >
        <input
          type="text"
          id="location"
          name="location"
          value={formData.location}
          onChange={handleInputChange}
          placeholder="123 Main Street, City, State"
          required
          className={INPUT_CLASS}
        />
      </FormField>

      {/* Audio */}
      <FormField id="audio" label="Audio Recording">
        <FileDropZone
          id="audio"
          name="audio"
          accept="audio/*"
          file={audioFile}
          onChange={e => setAudioFile(e.target.files[0] || null)}
          onClear={() => { setAudioFile(null); const el = document.getElementById('audio'); if (el) el.value = '' }}
          icon={Mic}
          placeholder="Choose audio file…"
          hint="WAV, MP3, M4A — max 10 MB"
        />
      </FormField>

      {/* Image */}
      <FormField id="image" label="Photo">
        <FileDropZone
          id="image"
          name="image"
          accept="image/*"
          file={imageFile}
          onChange={e => setImageFile(e.target.files[0] || null)}
          onClear={() => { setImageFile(null); const el = document.getElementById('image'); if (el) el.value = '' }}
          icon={Image}
          placeholder="Choose image file…"
          hint="JPG, PNG, HEIC — max 10 MB"
        />
      </FormField>

      {/* Actions */}
      <div className="flex gap-3 pt-2">
        <button
          type="submit"
          disabled={submitting}
          className={cn(
            'flex-1 flex items-center justify-center gap-2 h-10 px-4 rounded-lg',
            'bg-accent text-accent-fg font-medium text-body',
            'hover:bg-amber-400 transition-colors',
            'disabled:opacity-50 disabled:pointer-events-none',
          )}
        >
          {submitting ? (
            <><Loader2 size={15} className="animate-spin" /> Submitting…</>
          ) : (
            <><Send size={15} /> Submit Incident</>
          )}
        </button>

        <Button
          type="button"
          variant="ghost"
          size="md"
          icon={RotateCcw}
          onClick={resetForm}
          disabled={submitting}
        >
          Reset
        </Button>
      </div>

      <p className="text-caption text-text-muted leading-relaxed">
        Audio and images are processed by AI after submission. Your report will be reviewed by dispatchers.
      </p>
    </form>
  )
}

export default SubmitIncidentForm
