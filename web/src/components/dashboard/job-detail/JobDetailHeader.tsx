import { Check, ChevronLeft, Copy, RotateCcw, Timer } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import type { Job } from '@/lib/jobs'
import { formatDuration, formatRelativeTime, cn } from '@/lib/utils'
import { formatAbsoluteTime, formatJobStatus, formatSourceType } from './jobDetailFormatters'

export function JobDetailHeader({
  job,
  copiedId,
  canRetry,
  elapsedMs,
  onCopyId,
  onOpenRetry,
}: {
  job: Job
  copiedId: boolean
  canRetry: boolean
  elapsedMs: number
  onCopyId: () => void
  onOpenRetry: () => void
}) {
  const isFailed = job.status === 'failed' || job.status === 'dead'
  const sourceTitle = typeof job.source_metadata?.source?.title === 'string' ? job.source_metadata.source.title : null

  return (
    <header className="space-y-6">
      <Link to="/dashboard/jobs" className="inline-flex items-center gap-1.5 text-sm font-medium text-[var(--text-secondary)] transition-colors hover:text-brand">
        <ChevronLeft className="h-4 w-4" aria-hidden="true" />
        Back to jobs
      </Link>

      <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0 space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <h1 className="text-display text-3xl text-[var(--text-primary)] sm:text-4xl">
              {formatSourceType(job.source_type)} processing
            </h1>
            <Badge variant={job.status === 'succeeded' ? 'default' : isFailed ? 'destructive' : 'secondary'} className="gap-1.5">
              {formatJobStatus(job.status)}
            </Badge>
            {job.retry_count > 0 && (
              <Badge variant="outline" className="text-[var(--text-secondary)]">
                Retry {job.retry_count}/{job.max_retries}
              </Badge>
            )}
          </div>

          <div className="flex min-w-0 items-center gap-2">
            <code className="min-w-0 max-w-full break-all rounded-md border border-[var(--border-subtle)] bg-[var(--bg-subtle)] px-2 py-1 font-mono text-xs text-[var(--text-primary)]">
              {job.id}
            </code>
            <Tooltip>
              <TooltipTrigger
                render={
                  <Button variant="ghost" size="icon" className="size-11 shrink-0" onClick={onCopyId} aria-label={copiedId ? 'Job ID copied' : 'Copy job ID'}>
                    {copiedId ? <Check className="h-4 w-4 text-brand" /> : <Copy className="h-4 w-4 text-[var(--text-muted)]" />}
                  </Button>
                }
              />
              <TooltipContent>{copiedId ? 'Copied' : 'Copy job ID'}</TooltipContent>
            </Tooltip>
          </div>

          <div className="space-y-1 text-sm text-[var(--text-secondary)]">
            {sourceTitle && <p className="truncate">{sourceTitle}</p>}
            <p className="break-all font-mono text-xs text-[var(--text-muted)]">{job.source_uri}</p>
          </div>
        </div>

        <div className="flex flex-col items-stretch gap-3 sm:flex-row sm:items-center lg:items-start">
          {canRetry && (
            <Button variant="outline" size="lg" className="gap-2" onClick={onOpenRetry}>
              <RotateCcw className="h-4 w-4" />
              Retry job
            </Button>
          )}
          <div className="flex min-w-[9rem] items-center gap-3 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] px-4 py-3 sm:block sm:text-right">
            <Timer className="h-4 w-4 text-brand sm:ml-auto" aria-hidden="true" />
            <div className="sm:mt-1">
              <p className="text-xs font-medium text-[var(--text-secondary)]">Duration</p>
              <p className="font-mono text-xl font-bold text-[var(--text-primary)]">{formatDuration(elapsedMs)}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-[var(--text-secondary)]">
        <time dateTime={job.created_at} title={formatAbsoluteTime(job.created_at)}>
          Started {formatRelativeTime(job.created_at)}
          <span className="sr-only">, {formatAbsoluteTime(job.created_at)}</span>
        </time>
        <span className="text-[var(--text-muted)]" aria-hidden="true">·</span>
        <span className={cn('font-medium', job.status === 'succeeded' ? 'text-brand' : 'text-[var(--text-secondary)]')}>
          {job.status === 'succeeded' ? 'Finished successfully' : formatJobStatus(job.status)}
        </span>
      </div>
    </header>
  )
}
