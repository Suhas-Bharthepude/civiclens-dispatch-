import { Loader2 } from 'lucide-react'
import { cn } from '../../lib/cn'

const variants = {
  primary:   'bg-accent text-accent-fg hover:bg-amber-400 focus-visible:ring-accent',
  secondary: 'bg-surface-2 text-text-primary border border-border hover:bg-border hover:border-border-strong',
  ghost:     'text-text-secondary hover:text-text-primary hover:bg-surface-2',
  danger:    'bg-red-900/40 text-red-400 border border-red-800 hover:bg-red-900/70 hover:border-red-700',
}

const sizes = {
  sm: 'h-7 px-3 text-caption gap-1.5',
  md: 'h-9 px-4 text-body gap-2',
  lg: 'h-11 px-6 text-body gap-2',
}

export function Button({
  variant = 'secondary',
  size = 'md',
  loading = false,
  disabled = false,
  icon: Icon,
  children,
  className,
  ...props
}) {
  return (
    <button
      disabled={disabled || loading}
      className={cn(
        'inline-flex items-center justify-center rounded-lg font-medium',
        'transition-colors duration-100',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-background',
        'disabled:opacity-50 disabled:pointer-events-none',
        variants[variant],
        sizes[size],
        className,
      )}
      {...props}
    >
      {loading ? (
        <Loader2 size={14} className="animate-spin flex-shrink-0" />
      ) : Icon ? (
        <Icon size={14} className="flex-shrink-0" />
      ) : null}
      {children}
    </button>
  )
}
