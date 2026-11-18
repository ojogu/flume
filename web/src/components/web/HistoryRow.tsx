import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { toast } from 'sonner'
import { ChevronRight, Download, Folder, Loader2 } from 'lucide-react'
import { getDownloadUrlForWeb } from '@/lib/web'
import {
  getJobChildren,
  getSourceThumbnail,
  getSourceTitle,
  isPlaylistParent,
  type Job,
} from '@/lib/jobs'
import { formatRelativeTime, cn } from '@/lib/utils'

export function getStatusBadge(status: string) {
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

/** "12 videos · 9 done · 1 failed" for a playlist folder. */
export function formatFolderCounts(job: Pick<Job, 'child_count' | 'children_done' | 'children_failed' | 'source_metadata'>): string {
  const playlist = job.source_metadata?.playlist as { selected_count?: number } | undefined
  const total = job.child_count ?? playlist?.selected_count ?? null
  if (total === null) return 'Playlist'
  const parts = [`${total} ${total === 1 ? 'video' : 'videos'}`]
  if (job.children_done != null) parts.push(`${job.children_done} done`)
  if (job.children_failed) parts.push(`${job.children_failed} failed`)
  return parts.join(' · ')
}

interface HistoryRowProps {
  job: Job
  apiKey: string | null
}

export function HistoryRow({ job, apiKey }: HistoryRowProps) {
  // A playlist parent is a folder, never a downloadable file.
  if (isPlaylistParent(job)) return <FolderRow job={job} />
  return <VideoRow job={job} apiKey={apiKey} />
}

function FolderRow({ job }: { job: Job }) {
  const [imgError, setImgError] = useState(false)

  const ownThumbnail = getSourceThumbnail(job.source_metadata)
  const ownTitle = getSourceTitle(job.source_metadata)

  // Playlists created before folders existed have no saved title/thumbnail —
  // borrow the first video's.
  const needsFallback = !ownThumbnail || !ownTitle
  const { data: firstChild } = useQuery({
    queryKey: ['web-folder-first-child', job.id],
    queryFn: () => getJobChildren(job.id, 1, 1),
    enabled: needsFallback,
    staleTime: 60_000,
    select: (res) => res.jobs[0],
  })

  const thumbnailUrl = ownThumbnail ?? getSourceThumbnail(firstChild?.source_metadata)
  const title = ownTitle ?? getSourceTitle(firstChild?.source_metadata) ?? 'Playlist'

  return (
    <Link
      to={`/web/history/${job.id}`}
      aria-label={`Open playlist ${title}`}
      className="flex w-full items-center gap-3 px-4 py-3 text-left transition-colors hover:bg-[var(--bg-subtle)]/50"
    >
      <div className="relative h-10 w-[72px] shrink-0 overflow-hidden rounded bg-[var(--bg-subtle)]">
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
        <span className="absolute bottom-0.5 right-0.5 flex h-4 w-4 items-center justify-center rounded bg-black/65 text-white">
          <Folder className="h-2.5 w-2.5" aria-hidden="true" />
        </span>
      </div>
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium text-[var(--text-primary)]">{title}</p>
        <p className="truncate text-xs text-[var(--text-muted)]">
          {formatFolderCounts(job)} · {formatRelativeTime(job.created_at)}
        </p>
      </div>
      <span className={cn('shrink-0 rounded-full px-2 py-0.5 text-[10px] font-medium capitalize', getStatusBadge(job.status))}>
        {job.status.replace('_', ' ')}
      </span>
      <ChevronRight className="h-4 w-4 shrink-0 text-[var(--text-muted)]" aria-hidden="true" />
    </Link>
  )
}

function VideoRow({ job, apiKey }: HistoryRowProps) {
  const [imgError, setImgError] = useState(false)
  const [downloading, setDownloading] = useState(false)

  // Only terminal successful jobs can serve a download.
  const downloadable = job.status === 'succeeded' || job.status === 'partial_success'

  const thumbnailUrl = getSourceThumbnail(job.source_metadata)
  const title = getSourceTitle(job.source_metadata)

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
