import type { ReactNode } from 'react'
import type { Job } from '@/lib/jobs'
import { formatRelativeTime } from '@/lib/utils'
import { formatAbsoluteTime, formatSourceType } from './jobDetailFormatters'

function MetadataRow({
  label,
  children,
  mono = false,
}: {
  label: string
  children: ReactNode
  mono?: boolean
}) {
  return (
    <div className="grid gap-1.5 border-b border-[var(--border-subtle)] py-3 first:pt-0 last:border-b-0 last:pb-0 sm:grid-cols-[6.5rem_minmax(0,1fr)] sm:gap-4">
      <dt className="text-xs font-medium text-[var(--text-muted)]">{label}</dt>
      <dd className={mono ? 'min-w-0 break-words font-mono text-xs text-[var(--text-primary)]' : 'min-w-0 text-sm text-[var(--text-primary)]'}>
        {children}
      </dd>
    </div>
  )
}

function TimeValue({ value }: { value: string }) {
  return (
    <time dateTime={value} title={formatAbsoluteTime(value)}>
      {formatRelativeTime(value)}
      <span className="sr-only">, {formatAbsoluteTime(value)}</span>
    </time>
  )
}

export function JobOverviewPanel({
  job,
  sourceTitle,
}: {
  job: Job
  sourceTitle: string | null
}) {
  return (
    <section className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-5 sm:p-6" aria-labelledby="job-overview-heading">
      <div className="mb-4">
        <h2 id="job-overview-heading" className="text-base font-semibold text-[var(--text-primary)]">Job overview</h2>
        <p className="mt-1 text-sm leading-relaxed text-[var(--text-secondary)]">The inputs and lifecycle of this job.</p>
      </div>

      <dl>
        <MetadataRow label="Source">
          <div className="min-w-0 space-y-1">
            <p className="min-w-0 break-all">{sourceTitle || formatSourceType(job.source_type)}</p>
            <p className="min-w-0 break-all font-mono text-xs text-[var(--text-secondary)]">{job.source_uri}</p>
          </div>
        </MetadataRow>
        <MetadataRow label="Source type">{formatSourceType(job.source_type)}</MetadataRow>
        {job.api_key_name && <MetadataRow label="API key">{job.api_key_name}</MetadataRow>}
        <MetadataRow label="Created">
          <TimeValue value={job.created_at} />
        </MetadataRow>
        <MetadataRow label="Updated">
          <TimeValue value={job.updated_at} />
        </MetadataRow>
        {job.completed_at && (
          <MetadataRow label="Completed">
            <TimeValue value={job.completed_at} />
          </MetadataRow>
        )}
        {job.max_retries > 0 && (
          <MetadataRow label="Retries" mono>
            {job.retry_count} of {job.max_retries}
          </MetadataRow>
        )}
        {job.parent_job_id && (
          <MetadataRow label="Parent job" mono>
            {job.parent_job_id}
          </MetadataRow>
        )}
        {job.playlist_entry_index !== null && (
          <MetadataRow label="Playlist entry" mono>
            {job.playlist_entry_index}
          </MetadataRow>
        )}
      </dl>
    </section>
  )
}
