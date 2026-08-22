import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useWebStore } from '@/stores/webStore'
import { getJob, type JobDetailResponse } from '@/lib/web'

function getHostname(uri: string): string | null {
  try {
    return new URL(uri).hostname.replace(/^www\./, '')
  } catch {
    return null
  }
}

function getSourceMeta(meta: Record<string, unknown> | null) {
  if (!meta || typeof meta !== 'object') return null
  const source = meta.source as Record<string, unknown> | undefined
  return source ?? null
}

export function JobSourceCard() {
  const session = useWebStore((s) => s.session)
  const currentJobId = useWebStore((s) => s.currentJobId)
  const uploadedFile = useWebStore((s) => s.uploadedFile)
  const sourceUri = useWebStore((s) => s.sourceUri)

  const [imgError, setImgError] = useState(false)

  const { data: job } = useQuery<JobDetailResponse>({
    queryKey: ['web-job', currentJobId],
    queryFn: () => getJob(session!.apiKey, currentJobId!),
    enabled: Boolean(session && currentJobId),
  })

  const meta = getSourceMeta(job?.source_metadata ?? null)
  const title = (meta?.title as string) ?? uploadedFile?.name ?? sourceUri ?? null
  const platform = (meta?.platform as string) ?? null
  const videoId = (meta?.video_id as string) ?? null

  const isYouTube = platform === 'youtube' && Boolean(videoId)
  const thumbnailUrl = isYouTube && !imgError
    ? `https://i.ytimg.com/vi/${videoId}/mqdefault.jpg`
    : null

  useEffect(() => {
    setImgError(false)
  }, [videoId])

  const hostname = !platform && sourceUri ? getHostname(sourceUri) : null
  const subtitle = platform ?? hostname ?? null

  const isInitialLoading = !job && Boolean(currentJobId)

  return (
    <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-4 flex gap-4 items-center">
      {/* Thumbnail slot — fixed 16:9, always reserved. Non-YouTube shows pulsing placeholder. */}
      <div className="h-14 w-24 shrink-0 overflow-hidden rounded-md bg-[var(--bg-subtle)]">
        {thumbnailUrl ? (
          <img
            src={thumbnailUrl}
            alt=""
            className="h-full w-full object-cover"
            onError={() => setImgError(true)}
            loading="eager"
          />
        ) : (
          <div className="h-full w-full animate-pulse bg-[var(--bg-subtle)]" />
        )}
      </div>

      {/* Title + subtitle — always visible */}
      <div className="min-w-0 flex-1">
        {isInitialLoading && !title ? (
          <div className="space-y-2">
            <div className="h-4 w-3/4 animate-pulse rounded bg-[var(--bg-subtle)]" />
            <div className="h-3 w-1/3 animate-pulse rounded bg-[var(--bg-subtle)]" />
          </div>
        ) : (
          <>
            <h3 className="truncate text-sm font-medium text-[var(--text-primary)]">
              {title ?? 'Preparing media...'}
            </h3>
            {subtitle && (
              <p className="truncate text-xs capitalize text-[var(--text-muted)]">
                {subtitle}
              </p>
            )}
          </>
        )}
      </div>
    </div>
  )
}
