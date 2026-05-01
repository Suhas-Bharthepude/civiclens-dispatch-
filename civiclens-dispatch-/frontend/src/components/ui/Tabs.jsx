import { cn } from '../../lib/cn'

export function Tabs({ tabs, active, onChange, className }) {
  return (
    <div className={cn(
      'flex items-center gap-0.5 p-1 rounded-xl',
      'bg-background border border-border',
      className,
    )}>
      {tabs.map(({ id, label, icon: Icon }) => {
        const isActive = active === id
        return (
          <button
            key={id}
            onClick={() => onChange(id)}
            className={cn(
              'relative flex items-center gap-2 px-5 py-1.5 rounded-lg text-body font-medium',
              'transition-all duration-150 focus:outline-none select-none',
              isActive
                ? 'text-text-primary bg-surface shadow-sm border border-border'
                : 'text-text-muted hover:text-text-secondary hover:bg-surface/40',
            )}
          >
            {Icon && <Icon size={14} className={isActive ? 'text-accent' : ''} />}
            {label}
          </button>
        )
      })}
    </div>
  )
}
