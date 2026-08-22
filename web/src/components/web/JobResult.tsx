import { Download, RotateCcw } from 'lucide-react'
import { buttonVariants } from '@/components/ui/button'
import { useWebStore } from '@/stores/webStore'
import { getDownloadUrlForWeb } from '@/lib/web'
import { cn } from '@/lib/utils'

function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  const units = ['KB', 'MB', 'GB', 'TB']
  let value = bytes / 1024
  let unit = 0
  while (value >= 1024 && unit < units.length - 1) {
    value /= 1024
    unit++
  }
  return `${value >= 100 ? Math.round(value) : value.toFixed(1)} ${units[unit]}`
}

function getSourceMetadata(meta: Record<string, unknown> | null) {
  if (!meta || typeof meta !== 'object') return null
  const source = meta.source as Record<string, unknown> | undefined
  const media = meta.media as Record<string, unknown> | undefined
  return { source, media }
}

export function JobResult() {
  const { session, jobDetail, resetJob, selectPreset, setSourceUri, setUploadedFile } = useWebStore()
  if (!jobDetail) return null

  const meta = getSourceMetadata(jobDetail.source_metadata)
  const title = (meta?.source?.title as string) ?? null

  const mediaParts: string[] = []
  // Output file size from the final completed step — falls back to duration only.
  const finalStep = [...(jobDetail.steps ?? [])]
    .reverse()
    .find((s) => s.status === 'complete')
  const file = finalStep?.output_artifact?.file as { size_bytes?: number } | undefined
  if (file?.size_bytes && file.size_bytes > 0) {
    mediaParts.push(formatFileSize(file.size_bytes))
  }
  if (meta?.media) {
    const m = meta.media
    if (m.duration_seconds) mediaParts.push(formatDuration(m.duration_seconds as number))
  }

  const handleProcessAnother = () => {
    resetJob()
    selectPreset(null)
    setSourceUri('')
    setUploadedFile(null)
  }

  const handleDownload = async () => {
    if (!session) return
    try {
      const url = await getDownloadUrlForWeb(session.apiKey, jobDetail.id)
      window.open(url, '_blank')
    } catch {
      // fallback: let browser handle the redirect
      window.open(`/v1/job/${jobDetail.id}/download`, '_blank')
    }
  }

  return (
    <div className="rounded-xl border border-green-200 bg-green-50 p-6 dark:border-green-900 dark:bg-green-950 space-y-4">
      <div className="flex items-center gap-3">
        <div className="h-8 w-8 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center">
          <Download className="h-4 w-4 text-green-600 dark:text-green-400" />
        </div>
        <div>
          <h3 className="font-semibold text-[var(--text-primary)]">Your file is ready</h3>
          {title && (
            <p className="text-sm text-[var(--text-secondary)] truncate">{title}</p>
          )}
          {mediaParts.length > 0 && (
            <p className="text-xs text-[var(--text-muted)]">{mediaParts.join(' · ')}</p>
          )}
        </div>
      </div>

      <div className="flex gap-3">
        <button
          onClick={handleDownload}
          className={cn(buttonVariants({ variant: 'default', size: 'sm' }), 'gap-2')}
        >
          <Download className="h-4 w-4" />
          Download
        </button>
        <button
          onClick={handleProcessAnother}
          className={cn(buttonVariants({ variant: 'outline', size: 'sm' }), 'gap-2')}
        >
          <RotateCcw className="h-4 w-4" />
          Process another
        </button>
      </div>
    </div>
  )
}
