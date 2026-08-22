import { useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { CheckCircle, Circle, Loader2, AlertCircle } from 'lucide-react'
import { useWebStore } from '@/stores/webStore'
import { getJobForWeb, type JobDetailResponse } from '@/lib/web'
import { JobFailureCard } from '@/components/web/JobFailureCard'
import { useElapsedTime } from '@/hooks/useElapsedTime'
import { cn } from '@/lib/utils'

function StepStatusIcon({ status }: { status: string }) {
  switch (status) {
    case 'complete':
      return <CheckCircle className="h-4 w-4 text-green-500" />
    case 'running':
      return <Loader2 className="h-4 w-4 text-brand animate-spin" />
    case 'failed':
      return <AlertCircle className="h-4 w-4 text-red-500" />
    default:
      return <Circle className="h-4 w-4 text-[var(--text-muted)]" />
  }
}

function formatElapsed(ms: number): string {
  const secs = Math.floor(ms / 1000)
  if (secs < 60) return `${secs}s`
  const mins = Math.floor(secs / 60)
  return `${mins}m ${secs % 60}s`
}

export function JobProgress() {
  const session = useWebStore((s) => s.session)
  const currentJobId = useWebStore((s) => s.currentJobId)
  const setJobDetail = useWebStore((s) => s.setJobDetail)

  const jobQuery = useQuery<JobDetailResponse>({
    queryKey: ['web-job', currentJobId],
    queryFn: () => getJobForWeb(session?.apiKey ?? null, currentJobId!),
    enabled: Boolean(session && currentJobId),
    refetchInterval: (query) => {
      const status = query.state.data?.status
      if (status === 'succeeded' || status === 'partial_success' || status === 'failed' || status === 'dead') return false
      return 2000
    },
  })

  const job = jobQuery.data
  const steps = job?.steps ?? []
  const isRunning = job?.status === 'pending' || job?.status === 'processing'
  const elapsed = useElapsedTime(job?.created_at ?? null, job?.completed_at ?? null, isRunning)
  const completedSteps = steps.filter((s) => s.status === 'complete').length
  const progress = steps.length > 0 ? (completedSteps / steps.length) * 100 : 0

  const isFailed = job?.status === 'failed' || job?.status === 'dead'
  const isSucceeded = job?.status === 'succeeded' || job?.status === 'partial_success'

  useEffect(() => {
    if (job && isSucceeded) {
      setJobDetail(job)
    }
  }, [job, isSucceeded, setJobDetail])

  if (jobQuery.isLoading) {
    return (
      <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-6">
        <div className="flex items-center gap-3">
          <Loader2 className="h-5 w-5 text-brand animate-spin" />
          <span className="text-sm text-[var(--text-secondary)]">Loading job...</span>
        </div>
      </div>
    )
  }

  if (jobQuery.isError || !job) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-6 dark:border-red-900 dark:bg-red-950">
        <p className="text-sm text-red-600 dark:text-red-400">
          Failed to load job status. Please try again.
        </p>
      </div>
    )
  }

  if (isFailed) {
    return <JobFailureCard job={job} />
  }

  if (isSucceeded) {
    return null
  }

  return (
    <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-6 space-y-5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Loader2 className="h-5 w-5 text-brand animate-spin" />
          <h3 className="font-semibold text-[var(--text-primary)]">Processing...</h3>
        </div>
        <span className="text-sm text-[var(--text-muted)]">
          {formatElapsed(elapsed)}
        </span>
      </div>

      <div className="w-full bg-[var(--bg-subtle)] rounded-full h-2">
        <div
          className="bg-brand h-2 rounded-full transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>

      <div className="space-y-2">
        {steps.map((step) => (
          <div key={step.id}>
            <div className="flex items-center gap-3">
              <StepStatusIcon status={step.status} />
              <span className={cn(
                'text-sm',
                step.status === 'complete'
                  ? 'text-[var(--text-secondary)]'
                  : step.status === 'running'
                    ? 'text-[var(--text-primary)] font-medium'
                    : step.status === 'failed'
                      ? 'text-red-500'
                      : 'text-[var(--text-muted)]',
              )}>
                {step.operation.replace(/_/g, ' ')}
              </span>
            </div>
            {step.error && (
              <p className="ml-7 mt-1 text-xs text-red-500">{step.error}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
