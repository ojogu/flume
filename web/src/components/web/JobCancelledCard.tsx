import { Ban, RotateCcw } from 'lucide-react'
import { buttonVariants } from '@/components/ui/button'
import { useWebStore } from '@/stores/webStore'
import { cn } from '@/lib/utils'

/** Shown in place of the progress card after a job was cancelled. */
export function JobCancelledCard() {
  const resetJob = useWebStore((s) => s.resetJob)

  return (
    <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-6 space-y-5">
      <div className="flex items-start gap-3">
        <Ban className="mt-0.5 h-5 w-5 shrink-0 text-[var(--text-muted)]" aria-hidden="true" />
        <div className="min-w-0 space-y-1">
          <p className="text-sm font-semibold text-[var(--text-primary)]">Cancelled</p>
          <p className="text-sm leading-relaxed text-[var(--text-secondary)]">
            This job was cancelled and won't use your monthly limit.
          </p>
        </div>
      </div>

      <button
        onClick={resetJob}
        className={cn(buttonVariants({ variant: 'default', size: 'sm' }), 'gap-2')}
      >
        <RotateCcw className="h-4 w-4" />
        Back to form
      </button>
    </div>
  )
}
