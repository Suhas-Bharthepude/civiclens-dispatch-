import { cn } from '../../lib/cn'

export function Skeleton({ className, ...props }) {
  return (
    <div
      className={cn(
        'rounded-md bg-surface-2 animate-pulse',
        className,
      )}
      {...props}
    />
  )
}
