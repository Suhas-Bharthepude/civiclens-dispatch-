import { useState, useRef, useEffect } from 'react'
import { ChevronDown, Check } from 'lucide-react'
import { cn } from '../../lib/cn'

export function Select({ value, onChange, options, placeholder, icon: Icon, className }) {
  const [open, setOpen] = useState(false)
  const ref = useRef(null)

  useEffect(() => {
    const handler = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  useEffect(() => {
    if (!open) return
    const handler = (e) => { if (e.key === 'Escape') setOpen(false) }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [open])

  const selected = options.find(o => o.value === value)

  return (
    <div ref={ref} className={cn('relative', className)}>
      <button
        type="button"
        onClick={() => setOpen(v => !v)}
        className={cn(
          'flex items-center gap-2 px-3 py-1.5 rounded-lg text-body',
          'bg-surface-2 border border-border',
          'text-text-primary hover:border-border-strong hover:bg-surface-2',
          'focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent/30',
          'transition-colors whitespace-nowrap cursor-pointer select-none',
        )}
      >
        {Icon && <Icon size={12} className="text-text-muted flex-shrink-0" />}
        <span className="flex-1 text-left min-w-0">{selected?.label ?? placeholder}</span>
        <ChevronDown
          size={12}
          className={cn('text-text-muted transition-transform duration-150 flex-shrink-0', open && 'rotate-180')}
        />
      </button>

      {open && (
        <div className={cn(
          'absolute z-50 top-full mt-1.5 min-w-full',
          'bg-surface border border-border-strong rounded-xl',
          'shadow-[0_8px_32px_rgba(0,0,0,0.5)]',
          'py-1 overflow-hidden',
          'animate-in fade-in-0 zoom-in-95 duration-100',
        )}>
          {options.map(opt => {
            const isSelected = opt.value === value
            return (
              <button
                key={opt.value}
                type="button"
                onClick={() => { onChange(opt.value); setOpen(false) }}
                className={cn(
                  'flex items-center gap-2.5 w-full px-3 py-2 text-body text-left',
                  'transition-colors duration-75',
                  isSelected
                    ? 'bg-surface-2 text-accent'
                    : 'text-text-primary hover:bg-surface-2 hover:text-text-primary',
                )}
              >
                <Check
                  size={12}
                  className={cn('flex-shrink-0 transition-opacity', isSelected ? 'opacity-100 text-accent' : 'opacity-0')}
                />
                {opt.label}
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}
