import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useWebStore } from '@/stores/webStore'
import { useAuthStore } from '@/stores/authStore'
import { getJobs } from '@/lib/jobs'

const DISMISS_KEY_PREFIX = 'flume_dismissed_job_'

export function ActiveJobBanner() {
  const { accessToken } = useAuthStore()
  const currentJobId = useWebStore((s) => s.currentJobId)
  const [dismissedId, setDismissedId] = useState<string | null>(null)

  const { data } = useQuery({
    queryKey: ['web-active-job-banner'],
    queryFn: () => getJobs({ origin: 'web', per_page: 1 }),
    enabled: !!accessToken && !currentJobId,
    refetchInterval: (query) => {
      const job = query.state.data?.jobs?.[0]
      return job && (job.status === 'pending' || job.status === 'processing') ? 5000 : false
    },
  })

  const job = data?.jobs?.[0]
  const sessionDismissed = job ? sessionStorage.getItem(DISMISS_KEY_PREFIX + job.id) === '1' : false
  const visible =
    !!accessToken &&
    !currentJobId &&
    !sessionDismissed &&
    !dismissedId &&
    !!job &&
    (job.status === 'pending' || job.status === 'processing')

  // Any click anywhere dismisses the banner without swallowing the event.
  useEffect(() => {
    if (!visible || !job) return
    const dismiss = () => {
      sessionStorage.setItem(DISMISS_KEY_PREFIX + job.id, '1')
      setDismissedId(job.id)
    }
    document.addEventListener('click', dismiss)
    return () => document.removeEventListener('click', dismiss)
  }, [visible, job])

  if (!visible || !job) return null

  return (
    <div className="flex items-center justify-center gap-2.5 rounded-xl border border-brand/20 bg-brand/10 px-4 py-2.5">
      <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-brand animate-pulse" aria-hidden="true" />
      <span className="text-sm text-[var(--text-secondary)]">A video is still processing</span>
      <Link
        to="/web/history"
        className="text-sm font-medium text-brand hover:underline"
      >
        View progress →
      </Link>
    </div>
  )
}
