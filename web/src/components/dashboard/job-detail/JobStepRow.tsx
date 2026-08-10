import { AlertCircle, CheckCircle2, Circle, Clock3 } from 'lucide-react'
import type { JobStep } from '@/lib/jobs'
import { formatRelativeTime, cn } from '@/lib/utils'
import { formatAbsoluteTime, formatOperation, formatStepDuration, formatStepStatus, isCompletedStepStatus } from './jobDetailFormatters'
import { JobErrorCallout } from './JobErrorCallout'

function StepStatusIcon({ status }: { status: JobStep['status'] }) {
  if (isCompletedStepStatus(status)) {
    return <CheckCircle2 className="h-5 w-5 text-brand" aria-hidden="true" />
  }

  switch (status) {
    case 'failed':
      return <AlertCircle className="h-5 w-5 text-destructive" aria-hidden="true" />
    case 'running':
      return <Clock3 className="h-5 w-5 text-brand motion-safe:animate-spin" aria-hidden="true" />
    default:
      return <Circle className="h-5 w-5 text-[var(--text-muted)]" aria-hidden="true" />
  }
}

function StepTime({ label, value }: { label: string; value: string }) {
  return (
    <time className="text-xs text-[var(--text-secondary)]" dateTime={value} title={formatAbsoluteTime(value)}>
      {label} {formatRelativeTime(value)}
      <span className="sr-only">, {formatAbsoluteTime(value)}</span>
    </time>
  )
}

export function JobStepRow({
  step,
  index,
  isLast,
}: {
  step: JobStep
  index: number
  isLast: boolean
}) {
  const duration = formatStepDuration(step.started_at, step.completed_at)

  return (
    <li className={cn('relative grid grid-cols-[2rem_minmax(0,1fr)] gap-4', !isLast && 'pb-8')}>
      {!isLast && <span className="absolute bottom-0 left-4 top-8 w-px -translate-x-1/2 bg-[var(--border-subtle)]" aria-hidden="true" />}
      <div className="relative z-10 flex h-8 w-8 items-center justify-center rounded-full bg-[var(--bg-card)]">
        <StepStatusIcon status={step.status} />
      </div>

      <div className="min-w-0 space-y-3">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
          <div className="min-w-0">
            <p className="text-xs font-medium text-[var(--text-muted)]">Step {String(index + 1).padStart(2, '0')} · {formatStepStatus(step.status)}</p>
            <h3 className={cn('mt-1 break-words text-base font-semibold', step.status === 'failed' ? 'text-destructive' : 'text-[var(--text-primary)]')}>
              {formatOperation(step.operation)}
            </h3>
          </div>
          {duration && <span className="shrink-0 font-mono text-xs text-[var(--text-secondary)]">{duration}</span>}
        </div>

        {(step.started_at || step.completed_at) && (
          <div className="flex flex-wrap gap-x-4 gap-y-1">
            {step.started_at && <StepTime label="Started" value={step.started_at} />}
            {step.completed_at && <StepTime label="Completed" value={step.completed_at} />}
          </div>
        )}

        {step.error && <JobErrorCallout message={step.error} variant="step" />}
      </div>
    </li>
  )
}
