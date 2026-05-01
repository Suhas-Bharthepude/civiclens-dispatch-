import { cn } from '../../lib/cn'

export function EmptyState({ icon: Icon, title, description, action, className }) {
  return (
    <div className={cn('flex flex-col items-center justify-center gap-3 py-16 px-8 text-center', className)}>
      {Icon && (
        <div className="w-12 h-12 rounded-xl bg-surface-2 border border-border flex items-center justify-center">
          <Icon size={24} className="text-text-muted" />
        </div>
      )}
      {title && (
        <p className="text-heading text-text-secondary">{title}</p>
      )}
      {description && (
        <p className="text-body text-text-muted max-w-xs">{description}</p>
      )}
      {action && (
        <div className="mt-2">{action}</div>
      )}
    </div>
  )
}
