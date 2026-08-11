import { useState } from 'react'
import { useParams, useSearchParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { JobDetailHeader } from '@/components/dashboard/job-detail/JobDetailHeader'
import { JobDetailErrorState, JobDetailLoadingState } from '@/components/dashboard/job-detail/JobDetailStates'
import { JobErrorCallout } from '@/components/dashboard/job-detail/JobErrorCallout'
import { JobOutputAction } from '@/components/dashboard/job-detail/JobOutputAction'
import { JobOverviewPanel } from '@/components/dashboard/job-detail/JobOverviewPanel'
import { JobProgressSummary } from '@/components/dashboard/job-detail/JobProgressSummary'
import { JobTimeline } from '@/components/dashboard/job-detail/JobTimeline'
import { RetryJobDialog } from '@/components/dashboard/job-detail/RetryJobDialog'
import { useElapsedTime } from '@/hooks/useElapsedTime'
import { getJob, retryJob } from '@/lib/jobs'
import { apiClient } from '@/lib/api'
import { isCompletedStepStatus } from '@/components/dashboard/job-detail/jobDetailFormatters'

const RETRYABLE_STATUSES = new Set(['pending', 'processing', 'failed'])

export function JobDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [searchParams] = useSearchParams()
  const queryClient = useQueryClient()
  const [copiedId, setCopiedId] = useState(false)
  const [showRetryDialog, setShowRetryDialog] = useState(false)
  const [isDownloading, setIsDownloading] = useState(false)

  const backUrl = `/dashboard/jobs${searchParams.toString() ? `?${searchParams.toString()}` : ''}`

  const jobQuery = useQuery({
    queryKey: ['job', id],
    queryFn: () => getJob(id!),
    enabled: Boolean(id),
  })

  const retryMutation = useMutation({
    mutationFn: () => retryJob(id!),
    onSuccess: async () => {
      await jobQuery.refetch()
      await queryClient.invalidateQueries({ queryKey: ['jobs'] })
      setShowRetryDialog(false)
      toast.success('Job restarted')
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to retry job')
    },
  })

  const job = jobQuery.data
  const steps = job?.steps ?? []
  const isRunning = job?.status === 'pending' || job?.status === 'processing'
  const elapsed = useElapsedTime(job?.created_at ?? null, job?.completed_at ?? null, isRunning)
  const completedSteps = steps.filter((step) => isCompletedStepStatus(step.status) || step.status === 'failed').length
  const failedSteps = steps.filter((step) => step.status === 'failed').length
  const canRetry = Boolean(job && RETRYABLE_STATUSES.has(job.status))
  const finalStep = steps[steps.length - 1]
  const sourceTitle = typeof job?.source_metadata?.source?.title === 'string' ? job.source_metadata.source.title : null

  const handleCopyId = async () => {
    if (!job) return

    try {
      await navigator.clipboard.writeText(job.id)
      setCopiedId(true)
      window.setTimeout(() => setCopiedId(false), 2000)
    } catch {
      toast.error('Could not copy job ID')
    }
  }

  const handleDownload = async () => {
    if (!job || isDownloading) return

    const newWindow = window.open('', '_blank')
    if (!newWindow) {
      toast.error('Allow pop-ups to open the job output')
      return
    }

    setIsDownloading(true)
    try {
      const response = await apiClient<{ status: string; data: { url: string } }>(`/jobs/${job.id}/download`)
      newWindow.location.href = response.data.url
    } catch (error) {
      newWindow.close()
      toast.error(error instanceof Error ? error.message : 'Failed to prepare job output')
    } finally {
      setIsDownloading(false)
    }
  }

  if (jobQuery.isLoading) return <JobDetailLoadingState />

  if (jobQuery.isError || !job) {
    return (
      <JobDetailErrorState
        message={jobQuery.error instanceof Error ? jobQuery.error.message : 'The job you are looking for does not exist or has been deleted.'}
        onRetry={() => void jobQuery.refetch()}
      />
    )
  }

  return (
    <div className="min-w-0 max-w-5xl space-y-8">
      <JobDetailHeader
        job={job}
        copiedId={copiedId}
        canRetry={canRetry}
        elapsedMs={elapsed}
        onCopyId={handleCopyId}
        onOpenRetry={() => setShowRetryDialog(true)}
        backUrl={backUrl}
      />

      <div className="grid min-w-0 gap-6 lg:grid-cols-[minmax(0,1fr)_18rem] lg:items-start">
        <div className="min-w-0 space-y-6">
          <JobProgressSummary
            completedSteps={completedSteps}
            totalSteps={steps.length}
            failedSteps={failedSteps}
            isRunning={isRunning}
          />
          <JobTimeline steps={steps} />
        </div>

        <aside className="min-w-0 space-y-6">
          {job.error && <JobErrorCallout message={job.error} variant="job" />}
          <JobOverviewPanel job={job} sourceTitle={sourceTitle} />
          {finalStep?.output_url && <JobOutputAction onDownload={handleDownload} isDownloading={isDownloading} />}
        </aside>
      </div>

      <RetryJobDialog
        open={showRetryDialog}
        retrying={retryMutation.isPending}
        retryCount={job.retry_count}
        maxRetries={job.max_retries}
        onOpenChange={setShowRetryDialog}
        onConfirm={() => retryMutation.mutate()}
      />
    </div>
  )
}
