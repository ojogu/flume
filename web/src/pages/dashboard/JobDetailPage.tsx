import { useEffect, useState, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ChevronLeft, Copy, Check, AlertCircle, Clock, CheckCircle2, Circle, ExternalLink, RotateCcw } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Separator } from '@/components/ui/separator'
import { Button } from '@/components/ui/button'
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { toast } from 'sonner'
import { getJob, Job, JobStep, retryJob } from '@/lib/jobs'
import { formatDuration, formatRelativeTime, cn } from '@/lib/utils'
import { apiClient } from '@/lib/api'
import { useQueryClient } from '@tanstack/react-query'

const RETRYABLE_STATUSES = ['pending', 'processing', 'failed']

function useElapsedTime(startTime: string | null, isRunning: boolean) {
  const [elapsed, setElapsed] = useState(0)

  useEffect(() => {
    if (!startTime) return
    const start = new Date(startTime).getTime()
    setElapsed(Date.now() - start)

    if (!isRunning) return

    const interval = setInterval(() => {
      setElapsed(Date.now() - start)
    }, 1000)

    return () => clearInterval(interval)
  }, [startTime, isRunning])

  return elapsed
}

export function JobDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [job, setJob] = useState<Job | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [copiedId, setCopiedId] = useState(false)
  const [showRetryDialog, setShowRetryDialog] = useState(false)
  const [retrying, setRetrying] = useState(false)
  const queryClient = useQueryClient()

  const fetchJob = useCallback(async () => {
    if (!id) return
    try {
      const data = await getJob(id)
      setJob(data)
      setError(null)
    } catch (err: any) {
      setError(err.message || 'Failed to load job')
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => {
    if (id) {
      fetchJob()
    }
  }, [id, fetchJob])

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopiedId(true)
    setTimeout(() => setCopiedId(false), 2000)
  }

  const handleDownload = async (jobId: string) => {
    const win = window.open('', '_blank')
    if (!win) return

    const response = await apiClient<{status: string, data: {url: string}}>(`/jobs/${jobId}/download`)
    win.location.href = response.data.url
  }

  const handleRetry = async () => {
    if (!id) return
    setRetrying(true)
    try {
      await retryJob(id)
      await fetchJob()
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
      setShowRetryDialog(false)
      toast.success('Job restarted')
    } catch (err: any) {
      setError(err.message || 'Failed to retry job')
    } finally {
      setRetrying(false)
    }
  }

  const isRunning = job?.status === 'pending' || job?.status === 'processing'
  const elapsed = useElapsedTime(job?.created_at || null, isRunning)
  const completedSteps = job?.steps?.filter(s => s.status === 'completed' || s.status === 'failed').length || 0
  const totalSteps = job?.steps?.length || 0
  const canRetry = job && RETRYABLE_STATUSES.includes(job.status)
  const sourceTitle = job?.source_metadata?.source?.title || job?.source_uri || null

  if (loading) {
    return (
      <div className="max-w-4xl space-y-8 animate-pulse">
        <div className="flex items-center gap-4">
          <Skeleton className="h-5 w-24" />
        </div>
        <div className="flex justify-between items-start">
          <div className="space-y-4">
            <Skeleton className="h-10 w-64" />
            <Skeleton className="h-5 w-48" />
          </div>
          <Skeleton className="h-12 w-24" />
        </div>
        <div className="space-y-6 pt-8">
          <Skeleton className="h-16 w-full rounded-xl" />
          <Skeleton className="h-16 w-full rounded-xl" />
          <Skeleton className="h-16 w-full rounded-xl" />
        </div>
      </div>
    )
  }

  if (error || !job) {
    return (
      <div className="text-center py-20">
        <h2 className="text-display text-2xl text-[var(--text-primary)]">Job not found</h2>
        <p className="text-[var(--text-secondary)] mt-2">
          {error || 'The job you are looking for does not exist or has been deleted.'}
        </p>
        <Link to="/dashboard/jobs" className="mt-6 inline-block text-brand hover:underline font-medium">
          Back to jobs
        </Link>
      </div>
    )
  }

  const StepIcon = ({ status }: { status: JobStep['status'] }) => {
    switch (status) {
      case 'completed': return <CheckCircle2 className="h-5 w-5 text-brand" />
      case 'failed': return <AlertCircle className="h-5 w-5 text-destructive" />
      case 'running': return <Clock className="h-5 w-5 text-brand animate-spin" />
      case 'pending': return <Circle className="h-5 w-5 text-[var(--text-muted)]" />
    }
  }

  return (
    <TooltipProvider>
      <div className="max-w-4xl space-y-8">
        {/* Header */}
        <div className="space-y-4">
          <Link
            to="/dashboard/jobs"
            className="inline-flex items-center gap-1.5 text-sm font-medium text-[var(--text-secondary)] hover:text-brand transition-colors"
          >
            <ChevronLeft className="h-4 w-4" />
            Back to jobs
          </Link>

          <div className="flex flex-wrap items-center justify-between gap-6">
            <div className="space-y-1">
              <div className="flex items-center gap-3">
                <h1 className="text-display text-3xl sm:text-4xl text-[var(--text-primary)] capitalize">
                  {job.source_type} Processing
                </h1>
                <Badge
                  variant={
                    job.status === 'succeeded' ? 'default'
                    : job.status === 'failed' || job.status === 'dead' ? 'destructive'
                    : job.status === 'partial_success' ? 'secondary'
                    : 'secondary'
                  }
                  className="mt-1 capitalize"
                >
                  {job.status.replace('_', ' ')}
                </Badge>
                {job.retry_count > 0 && (
                  <Badge variant="outline" className="mt-1 capitalize border-[var(--border-subtle)] text-[var(--text-muted)]">
                    Retry {job.retry_count}/{job.max_retries}
                  </Badge>
                )}
              </div>
              <div className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
                <code className="bg-[var(--bg-subtle)] px-1.5 py-0.5 rounded text-xs font-mono border border-[var(--border-subtle)]">{job.id}</code>
                <Button
                  variant="ghost"
                  size="icon"
                  aria-label="Copy job ID"
                  onClick={() => copyToClipboard(job.id)}
                >
                  {copiedId ? <Check className="h-3.5 w-3.5 text-brand" /> : <Copy className="h-3.5 w-3.5" />}
                </Button>
              </div>
              {job.api_key_name && (
                <p className="text-xs text-[var(--text-muted)]">API Key: {job.api_key_name}</p>
              )}
              {sourceTitle && sourceTitle !== job.source_uri && (
                <p className="text-xs text-[var(--text-secondary)] truncate max-w-md">
                  {sourceTitle}
                </p>
              )}
            </div>

            <div className="flex items-center gap-3">
              {canRetry && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowRetryDialog(true)}
                  className="h-9 gap-2 border-[var(--border-subtle)]"
                >
                  <RotateCcw className="h-4 w-4" />
                  Retry
                </Button>
              )}
              <div className="bg-[var(--bg-card)] border border-[var(--border-subtle)] p-4 rounded-xl text-right min-w-[140px]">
                <p className="text-label text-[var(--text-muted)] mb-1 tracking-wider">Duration</p>
                <p className="text-2xl font-mono text-[var(--text-primary)] font-bold">
                  {formatDuration(elapsed)}
                </p>
              </div>
            </div>
          </div>

          {/* Start time */}
          <Tooltip>
            <TooltipTrigger asChild>
              <p className="text-xs text-[var(--text-muted)] cursor-default">
                Started {formatRelativeTime(job.created_at)}
              </p>
            </TooltipTrigger>
            <TooltipContent>
              {new Date(job.created_at).toLocaleString()}
            </TooltipContent>
          </Tooltip>

          {/* Step count summary */}
          {totalSteps > 0 && (
            <p className="text-xs text-[var(--text-secondary)]">
              {completedSteps} of {totalSteps} steps complete
            </p>
          )}
        </div>

        <Separator className="bg-[var(--border-subtle)]" />

        {/* Timeline */}
        <div className="relative space-y-0 pb-12 px-2">
          {job.steps?.map((step, index) => (
            <div key={step.id} className="relative flex gap-6 pb-10 last:pb-0">
              {/* Connector Line */}
              {index < (job.steps?.length || 0) - 1 && (
                <div className="absolute left-[9px] top-6 w-[2px] h-full bg-[var(--border-subtle)]" />
              )}

              {/* Node Icon Container */}
              <div className="relative z-10 pt-0.5 bg-[var(--background)]">
                <StepIcon status={step.status} />
              </div>

              {/* Step Content */}
              <div className="flex-1 space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className={cn(
                    "font-semibold text-base",
                    step.status === 'failed' ? "text-destructive" : "text-[var(--text-primary)]"
                  )}>
                    {step.operation}
                  </h3>
                  <div className="flex items-center gap-2">
                    {step.started_at && (
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <span className="text-xs font-mono text-[var(--text-muted)] font-medium cursor-default">
                            {formatRelativeTime(step.started_at)}
                          </span>
                        </TooltipTrigger>
                        <TooltipContent>
                          Started: {new Date(step.started_at).toLocaleString()}
                        </TooltipContent>
                      </Tooltip>
                    )}
                    {step.completed_at && (
                      <>
                        <span className="text-xs text-[var(--text-muted)]">→</span>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <span className="text-xs font-mono text-[var(--text-muted)] font-medium cursor-default">
                              {formatRelativeTime(step.completed_at)}
                            </span>
                          </TooltipTrigger>
                          <TooltipContent>
                            Completed: {new Date(step.completed_at).toLocaleString()}
                          </TooltipContent>
                        </Tooltip>
                      </>
                    )}
                    {step.started_at && step.completed_at && (
                      <span className="text-xs font-mono text-[var(--text-muted)] ml-2">
                        ({formatDuration(new Date(step.completed_at).getTime() - new Date(step.started_at).getTime())})
                      </span>
                    )}
                  </div>
                </div>

                {index === (job.steps?.length ?? 0) - 1 && step.output_url && (
                  <Button
                    variant="outline"
                    onClick={() => handleDownload(id!)}
                    className="w-full justify-start gap-2 border-brand/20 bg-brand/5 hover:bg-brand/10 text-brand"
                  >
                    <ExternalLink className="h-5 w-5" />
                    <div className="space-y-1 text-left">
                      <p className="text-sm font-bold uppercase tracking-wider">View Output</p>
                      <p className="text-sm opacity-90 leading-relaxed truncate">
                        {`https://api.flume.ojogulabs.xyz/internal/jobs/${id}/download`}
                      </p>
                    </div>
                  </Button>
                )}

                {step.error && (
                  <div className="rounded-xl border border-destructive/20 bg-destructive/5 p-4">
                    <div className="flex items-start gap-3 text-destructive">
                      <AlertCircle className="h-5 w-5 shrink-0 mt-0.5" />
                      <div className="space-y-1">
                        <p className="text-sm font-bold uppercase tracking-wider">Step failed</p>
                        <p className="text-sm opacity-90 leading-relaxed">{step.error}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Retry Dialog */}
        <AlertDialog open={showRetryDialog} onOpenChange={setShowRetryDialog}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Retry this job?</AlertDialogTitle>
              <AlertDialogDescription>
                This will restart the job from the beginning. {job.retry_count === 0 ? 'This will be your first retry.' : `Currently on attempt ${job.retry_count + 1} of ${job.max_retries}.`}
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel disabled={retrying}>Cancel</AlertDialogCancel>
              <AlertDialogAction onClick={handleRetry} disabled={retrying}>
                {retrying ? 'Retrying...' : 'Retry Job'}
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </TooltipProvider>
  )
}
