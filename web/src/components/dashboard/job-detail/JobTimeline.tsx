import { ListChecks } from 'lucide-react'
import type { JobStep } from '@/lib/jobs'
import { JobStepRow } from './JobStepRow'

export function JobTimeline({ steps }: { steps: JobStep[] }) {
  if (!steps.length) {
    return (
      <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-[var(--border-subtle)] px-5 py-12 text-center">
        <ListChecks className="mb-3 h-6 w-6 text-[var(--text-muted)]" aria-hidden="true" />
        <p className="text-sm font-medium text-[var(--text-primary)]">No processing steps yet</p>
        <p className="mt-1 max-w-sm text-sm leading-relaxed text-[var(--text-secondary)]">
          Step details will appear here once the job starts processing.
        </p>
      </div>
    )
  }

  return (
    <ol className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-5 sm:p-6" aria-labelledby="processing-steps-heading">
      {steps.map((step, index) => (
        <JobStepRow key={step.id} step={step} index={index} isLast={index === steps.length - 1} />
      ))}
    </ol>
  )
}
