import { cn } from '../../lib/cn'

export function Tabs({ tabs, active, onChange, className }) {
  return (
    <div className={cn('flex items-center gap-1 relative', className)}>
      {tabs.map(({ id, label, icon: Icon }) => {
        const isActive = active === id
        return (
          <button
            key={id}
            onClick={() => onChange(id)}
            className={cn(
              'relative flex items-center gap-2 px-4 py-2 text-body font-medium rounded-lg',
              'transition-colors duration-100',
              isActive
                ? 'text-text-primary bg-surface-2'
                : 'text-text-muted hover:text-text-secondary hover:bg-surface-2/50',
            )}
          >
            {Icon && <Icon size={14} />}
            {label}
            {isActive && (
              <span className="absolute bottom-0 left-2 right-2 h-0.5 rounded-full bg-accent" />
            )}
          </button>
        )
      })}
    </div>
  )
}
