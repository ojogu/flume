import { AlertCircle, RotateCcw, Home } from 'lucide-react'
import { buttonVariants } from '@/components/ui/button'
import { useWebStore } from '@/stores/webStore'
import type { JobDetailResponse } from '@/lib/web'
import { cn } from '@/lib/utils'

export function JobFailureCard({ job }: { job: JobDetailResponse }) {
  const resetJob = useWebStore((s) => s.resetJob)
  const resetUI = useWebStore((s) => s.resetUI)

  const failedSteps = job.steps.filter((s) => s.status === 'failed')

  return (
    <div
      className="rounded-xl border border-destructive/20 bg-destructive/5 p-6 space-y-5"
      role="alert"
    >
      <div className="flex items-start gap-3 text-destructive">
        <AlertCircle className="mt-0.5 h-5 w-5 shrink-0" aria-hidden="true" />
        <div className="min-w-0 space-y-1">
          <p className="text-sm font-semibold">Processing failed</p>
          <p className="break-words text-sm leading-relaxed text-[var(--text-secondary)]">
            {job.error ?? 'Something went wrong while processing your media.'}
          </p>
        </div>
      </div>

      {failedSteps.length > 0 && (
        <div className="space-y-1.5">
          {failedSteps.map((step) => (
            <div key={step.id} className="flex items-start gap-2.5">
              <span className="mt-0.5 text-xs font-medium uppercase tracking-wide text-[var(--text-muted)]">
                Step {step.step_index + 1}
              </span>
              <div className="min-w-0">
                <p className="text-sm text-[var(--text-primary)]">
                  {step.operation.replace(/_/g, ' ')}
                </p>
                {step.error && (
                  <p className="text-xs text-destructive">{step.error}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="flex flex-col sm:flex-row gap-3">
        <button
          onClick={resetJob}
          className={cn(buttonVariants({ variant: 'default', size: 'sm' }), 'gap-2')}
        >
          <RotateCcw className="h-4 w-4" />
          Try again
        </button>
        <button
          onClick={resetUI}
          className={cn(buttonVariants({ variant: 'outline', size: 'sm' }), 'gap-2')}
        >
          <Home className="h-4 w-4" />
          Start over
        </button>
      </div>
    </div>
  )
}
