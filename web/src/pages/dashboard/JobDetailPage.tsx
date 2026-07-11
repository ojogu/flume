import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ChevronLeft, Copy, Check, AlertCircle, Clock, CheckCircle2, Circle } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Separator } from '@/components/ui/separator'
import { getJob, Job, JobStep } from '@/lib/jobs'
import { formatDuration, cn } from '@/lib/utils'

export function JobDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [job, setJob] = useState<Job | null>(null)
  const [loading, setLoading] = useState(true)
  const [copiedId, setCopiedId] = useState(false)

  useEffect(() => {
    if (id) {
      getJob(id).then((data) => {
        setJob(data)
        setLoading(false)
      })
    }
  }, [id])

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopiedId(true)
    setTimeout(() => setCopiedId(false), 2000)
  }

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

  if (!job) {
    return (
      <div className="text-center py-20">
        <h2 className="text-display text-2xl text-[var(--text-primary)]">Job not found</h2>
        <p className="text-[var(--text-secondary)] mt-2">The job you are looking for does not exist or has been deleted.</p>
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
              <Badge variant={job.status === 'succeeded' ? 'default' : job.status === 'failed' ? 'destructive' : 'secondary'} className="mt-1 capitalize h-5 text-[10px] font-bold">
                {job.status.replace('_', ' ')}
              </Badge>
            </div>
            <div className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
              <code className="bg-[var(--bg-subtle)] px-1.5 py-0.5 rounded text-xs font-mono border border-[var(--border-subtle)]">{job.id}</code>
              <button
                onClick={() => copyToClipboard(job.id)}
                className="text-[var(--text-muted)] hover:text-brand transition-colors p-1"
                title="Copy full ID"
              >
                {copiedId ? <Check className="h-3.5 w-3.5 text-brand" /> : <Copy className="h-3.5 w-3.5" />}
              </button>
            </div>
          </div>
          
          <div className="bg-[var(--bg-card)] border border-[var(--border-subtle)] p-4 rounded-xl text-right min-w-[140px] shadow-xs">
            <p className="text-label text-[var(--text-muted)] mb-1 tracking-wider">Duration</p>
            <p className="text-2xl font-mono text-[var(--text-primary)] font-bold">
              {job.completed_at ? formatDuration(new Date(job.completed_at).getTime() - new Date(job.created_at).getTime()) : '---'}
            </p>
          </div>
        </div>
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
                {step.started_at && step.completed_at && (
                  <span className="text-xs font-mono text-[var(--text-muted)] font-medium">
                    {formatDuration(new Date(step.completed_at).getTime() - new Date(step.started_at).getTime())}
                  </span>
                )}
              </div>

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
    </div>
  )
}
