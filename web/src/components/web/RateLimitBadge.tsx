import { useWebStore } from '@/stores/webStore'

export function RateLimitBadge() {
  const session = useWebStore((s) => s.session)
  if (!session) return null

  const remaining = session.jobsRemaining
  const dotColor =
    remaining === 0
      ? 'bg-red-500'
      : remaining <= 2
        ? 'bg-amber-500'
        : 'bg-green-500'

  return (
    <div className="inline-flex items-center gap-1.5 rounded-full border border-[var(--border-subtle)] bg-[var(--bg-card)] px-3 py-1 text-xs text-[var(--text-muted)]">
      <span className={`h-1.5 w-1.5 rounded-full ${dotColor}`} />
      {remaining} of 5 jobs left
    </div>
  )
}
