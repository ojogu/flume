import { ExternalLink, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'

export function JobOutputAction({
  onDownload,
  isDownloading,
}: {
  onDownload: () => void
  isDownloading: boolean
}) {
  return (
    <div className="rounded-xl border border-brand/20 bg-brand/5 p-4 sm:p-5">
      <div className="flex items-start gap-3">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-[var(--brand-light)]">
          <ExternalLink className="h-4 w-4 text-brand" aria-hidden="true" />
        </div>
        <div className="min-w-0">
          <p className="text-sm font-semibold text-[var(--text-primary)]">Output available</p>
          <p className="mt-1 text-sm leading-relaxed text-[var(--text-secondary)]">
            The final processing output is ready to view or download.
          </p>
        </div>
      </div>
      <Button
        variant="outline"
        className="mt-4 w-full justify-center gap-2 border-brand/20 bg-[var(--bg-card)] text-brand hover:bg-brand/10"
        onClick={onDownload}
        disabled={isDownloading}
        aria-busy={isDownloading}
      >
        {isDownloading ? <Loader2 className="h-4 w-4 animate-spin" /> : <ExternalLink className="h-4 w-4" />}
        {isDownloading ? 'Preparing output…' : 'View output'}
      </Button>
    </div>
  )
}
