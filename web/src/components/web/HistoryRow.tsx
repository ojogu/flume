import { useState } from 'react'
import { toast } from 'sonner'
import { Download, Loader2 } from 'lucide-react'
import { getDownloadUrlForWeb } from '@/lib/web'
import type { Job } from '@/lib/jobs'
import { formatRelativeTime, cn } from '@/lib/utils'

function getThumbnailUrl(meta: Record<string, unknown> | null): string | null {
  if (!meta || typeof meta !== 'object') return null
  const source = meta.source as Record<string, unknown> | undefined
  const platform = source?.platform as string | undefined
  const videoId = source?.video_id as string | undefined
  if (platform === 'youtube' && videoId) {
    return `https://i.ytimg.com/vi/${videoId}/mqdefault.jpg`
  }
  return null
}

function getStatusBadge(status: string) {
  const styles: Record<string, string> = {
    succeeded: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400',
    failed: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
    dead: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
    processing: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
    pending: 'bg-[var(--bg-subtle)] text-[var(--text-muted)]',
    partial_success: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400',
  }
  return styles[status] ?? styles.pending
}

interface HistoryRowProps {
  job: Job
  apiKey: string | null
}

export function HistoryRow({ job, apiKey }: HistoryRowProps) {
  const [imgError, setImgError] = useState(false)
  const [downloading, setDownloading] = useState(false)

  // Only terminal successful jobs can serve a download.
  const downloadable = job.status === 'succeeded' || job.status === 'partial_success'

  const thumbnailUrl = getThumbnailUrl(job.source_metadata)
  const meta = job.source_metadata as Record<string, unknown> | null
  const source = meta?.source as Record<string, unknown> | undefined
  const title = (source?.title as string) ?? null

  const handleDownload = async () => {
    if (!downloadable || downloading) return
    setDownloading(true)
    try {
      const url = await getDownloadUrlForWeb(apiKey, job.id)
      window.open(url, '_blank')
    } catch {
      toast.error("Couldn't start your download. Please try again.")
    } finally {
      setDownloading(false)
    }
  }

  const content = (
    <>
      <div className="h-10 w-[72px] shrink-0 overflow-hidden rounded bg-[var(--bg-subtle)]">
        {thumbnailUrl && !imgError ? (
          <img
            src={thumbnailUrl}
            alt=""
            className="h-full w-full object-cover"
            onError={() => setImgError(true)}
          />
        ) : (
          <div className="h-full w-full bg-[var(--bg-subtle)]" />
        )}
      </div>
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium text-[var(--text-primary)]">
          {title ?? job.source_uri ?? 'Untitled'}
        </p>
        <p className="text-xs text-[var(--text-muted)]">
          {formatRelativeTime(job.created_at)}
        </p>
      </div>
      {downloadable && (
        downloading ? (
          <Loader2 className="h-4 w-4 shrink-0 animate-spin text-brand" aria-hidden="true" />
        ) : (
          <Download className="h-4 w-4 shrink-0 text-[var(--text-muted)]" aria-hidden="true" />
        )
      )}
      <span className={cn('shrink-0 rounded-full px-2 py-0.5 text-[10px] font-medium capitalize', getStatusBadge(job.status))}>
        {job.status.replace('_', ' ')}
      </span>
    </>
  )

  if (!downloadable) {
    return (
      <div className="flex items-center gap-3 px-4 py-3">
        {content}
      </div>
    )
  }

  return (
    <button
      onClick={handleDownload}
      disabled={downloading}
      aria-label={`Download ${title ?? 'media'}`}
      title="Download"
      className="flex w-full items-center gap-3 px-4 py-3 text-left hover:bg-[var(--bg-subtle)]/50 transition-colors cursor-pointer disabled:cursor-wait"
    >
      {content}
    </button>
  )
}
