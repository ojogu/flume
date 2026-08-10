import { AlertCircle, RefreshCw } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'

export function JobDetailLoadingState() {
  return (
    <div className="min-w-0 max-w-5xl space-y-8" aria-busy="true" aria-label="Loading job details">
      <Skeleton className="h-5 w-28" />
      <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0 space-y-4">
          <Skeleton className="h-10 w-72 max-w-full" />
          <Skeleton className="h-8 w-full max-w-md" />
          <Skeleton className="h-8 w-full max-w-xl" />
        </div>
        <div className="flex gap-3">
          <Skeleton className="h-10 w-24" />
          <Skeleton className="h-20 w-36 rounded-xl" />
        </div>
      </div>
      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_18rem]">
        <div className="space-y-6">
          <Skeleton className="h-32 w-full rounded-xl" />
          <Skeleton className="h-[28rem] w-full rounded-xl" />
        </div>
        <Skeleton className="h-80 w-full rounded-xl" />
      </div>
    </div>
  )
}

export function JobDetailErrorState({
  message,
  onRetry,
}: {
  message: string
  onRetry: () => void
}) {
  return (
    <div className="flex min-h-[24rem] max-w-2xl flex-col items-center justify-center px-6 py-16 text-center">
      <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-xl border border-destructive/20 bg-destructive/5">
        <AlertCircle className="h-6 w-6 text-destructive" aria-hidden="true" />
      </div>
      <h1 className="text-display text-3xl text-[var(--text-primary)]">Job details unavailable</h1>
      <p className="mt-2 max-w-md text-sm leading-relaxed text-[var(--text-secondary)]">{message}</p>
      <div className="mt-6 flex flex-col gap-2 sm:flex-row">
        <Button variant="outline" onClick={onRetry} className="gap-2">
          <RefreshCw className="h-4 w-4" />
          Try again
        </Button>
        <Button render={<Link to="/dashboard/jobs" />} variant="ghost">
          Back to jobs
        </Button>
      </div>
    </div>
  )
}
