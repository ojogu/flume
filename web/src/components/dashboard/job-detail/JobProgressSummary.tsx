import { CheckCircle2, CircleX, Clock3, ListChecks } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

export function JobProgressSummary({
  completedSteps,
  totalSteps,
  failedSteps,
  isRunning,
}: {
  completedSteps: number
  totalSteps: number
  failedSteps: number
  isRunning: boolean
}) {
  const hasFailure = failedSteps > 0
  const isComplete = totalSteps > 0 && completedSteps >= totalSteps
  const status = hasFailure ? 'Needs attention' : isComplete ? 'Complete' : isRunning ? 'In progress' : 'Waiting'
  const statusVariant = hasFailure ? 'destructive' : isComplete ? 'default' : isRunning ? 'secondary' : 'outline'

  return (
    <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-5 sm:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex items-start gap-3">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-[var(--brand-light)]">
            <ListChecks className="h-4 w-4 text-brand" aria-hidden="true" />
          </div>
          <div>
            <h2 id="processing-steps-heading" className="text-base font-semibold text-[var(--text-primary)]">Processing steps</h2>
            <p className="mt-1 text-sm leading-relaxed text-[var(--text-secondary)]">
              {totalSteps ? `${completedSteps} of ${totalSteps} steps processed` : 'The processing plan is not available yet.'}
            </p>
          </div>
        </div>
        <Badge variant={statusVariant} className="self-start gap-1.5">
          {hasFailure ? <CircleX className="h-3.5 w-3.5" /> : isComplete ? <CheckCircle2 className="h-3.5 w-3.5" /> : <Clock3 className="h-3.5 w-3.5" />}
          {status}
        </Badge>
      </div>

      {totalSteps > 0 && (
        <div className="mt-5 flex gap-1.5" role="img" aria-label={`${completedSteps} of ${totalSteps} steps processed`}>
          {Array.from({ length: totalSteps }).map((_, index) => {
            const isProcessed = index < completedSteps
            return (
              <span
                key={index}
                className={cn(
                  'h-2 min-w-0 flex-1 rounded-full',
                  isProcessed ? (hasFailure ? 'bg-brand/60' : 'bg-brand') : 'bg-[var(--bg-subtle)]',
                )}
              />
            )
          })}
        </div>
      )}
    </div>
  )
}
