import { AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

export function JobErrorCallout({
  message,
  variant,
}: {
  message: string
  variant: 'job' | 'step'
}) {
  return (
    <div
      className={cn(
        'rounded-xl border border-destructive/20 bg-destructive/5 p-4',
        variant === 'job' ? 'p-5 sm:p-6' : 'p-4',
      )}
      role="alert"
    >
      <div className="flex items-start gap-3 text-destructive">
        <AlertCircle className="mt-0.5 h-5 w-5 shrink-0" aria-hidden="true" />
        <div className="min-w-0 space-y-1">
          <p className="text-sm font-semibold">
            {variant === 'job' ? 'Job error' : 'Step failed'}
          </p>
          <p className="break-words text-sm leading-relaxed text-[var(--text-secondary)]">
            {message}
          </p>
          <p className="pt-1 text-sm">
            <a
              href="/dashboard/support"
              className="font-medium text-destructive underline underline-offset-4 hover:text-destructive/80"
            >
              Contact support
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}
