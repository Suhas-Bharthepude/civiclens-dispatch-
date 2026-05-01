import { cn } from '../../lib/cn'

export function Card({ variant = 'default', className, children, ...props }) {
  return (
    <div
      className={cn(
        'rounded-lg border border-border p-4',
        variant === 'elevated' ? 'bg-surface-2' : 'bg-surface',
        className,
      )}
      {...props}
    >
      {children}
    </div>
  )
}
