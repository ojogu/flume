import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { toast } from 'sonner'
import { Loader2, Clock, ArrowRight, LogIn } from 'lucide-react'
import { Navbar } from '@/components/common/Navbar'
import { Footer } from '@/components/common/Footer'
import { SourceInput } from '@/components/web/SourceInput'
import { PresetPicker } from '@/components/web/PresetPicker'
import { PresetParams } from '@/components/web/PresetParams'
import { RateLimitBadge } from '@/components/web/RateLimitBadge'
import { JobSourceCard } from '@/components/web/JobSourceCard'
import { JobProgress } from '@/components/web/JobProgress'
import { JobResult } from '@/components/web/JobResult'
import { HistoryRow } from '@/components/web/HistoryRow'
import { useWebStore } from '@/stores/webStore'
import { useAuthStore } from '@/stores/authStore'
import { submitJob, submitJobAuth, ApiError } from '@/lib/web'
import { getJobs, type Job } from '@/lib/jobs'
import { getOperation, validateRequiredParams, getDefaultParams } from '@/lib/presets'
import { buttonVariants } from '@/components/ui/button'
import { cn } from '@/lib/utils'

function HistorySection({ isAuthenticated }: { isAuthenticated: boolean }) {
  const session = useWebStore((s) => s.session)
  const { data, isLoading } = useQuery({
    queryKey: ['web-history'],
    queryFn: () => getJobs({ origin: 'web', per_page: 10 }),
    enabled: isAuthenticated,
  })

  if (!isAuthenticated) {
    return (
      <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-6 text-center space-y-3">
        <Clock className="h-8 w-8 mx-auto text-[var(--text-muted)] opacity-40" />
        <p className="text-sm text-[var(--text-secondary)]">Sign in to see your processing history.</p>
        <Link
          to="/login?returnTo=/web"
          className={cn(buttonVariants({ variant: 'outline', size: 'sm' }), 'gap-2 inline-flex items-center')}
        >
          <LogIn className="h-3.5 w-3.5" />
          Sign in
        </Link>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="space-y-3">
        <div className="h-4 w-32 animate-pulse rounded bg-[var(--bg-subtle)]" />
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="h-14 animate-pulse rounded-xl bg-[var(--bg-subtle)]" />
        ))}
      </div>
    )
  }

  const jobs = data?.jobs ?? []
  if (jobs.length === 0) return null

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-label text-[var(--text-muted)]">Recent activity</h2>
        <Link
          to="/web/history"
          className="text-xs font-medium text-brand hover:underline flex items-center gap-1"
        >
          View all
          <ArrowRight className="h-3 w-3" />
        </Link>
      </div>
      <div className="divide-y divide-[var(--border-subtle)] rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)]">
        {jobs.map((job: Job) => (
          <HistoryRow key={job.id} job={job} apiKey={session?.apiKey ?? null} />
        ))}
      </div>
    </div>
  )
}

export function WebPage() {
  const {
    session,
    initSession,
    resetUI,
    sourceUri,
    selectedPreset,
    presetParams,
    currentJobId,
    jobDetail,
    error,
    isSubmitting,
    setSubmitting,
    setError,
    setJobId,
    decrementJobsRemaining,
  } = useWebStore()

  const { accessToken } = useAuthStore()
  const isAuthenticated = !!accessToken

  const [validationErrors, setValidationErrors] = useState<string[]>([])

  useEffect(() => {
    resetUI()
    initSession()
  }, [resetUI, initSession])

  const canSubmit = session && sourceUri && selectedPreset && !isSubmitting && !currentJobId && !jobDetail

  const handleSubmit = async () => {
    if (!session || !selectedPreset) return

    const op = getOperation(selectedPreset)
    if (!op) return

    const errors = validateRequiredParams(op, presetParams)
    if (errors.length > 0) {
      setValidationErrors(errors)
      return
    }
    setValidationErrors([])

    const isJoin = selectedPreset === 'join'
    const isDownload = selectedPreset === 'download'

    setSubmitting(true)
    setError(null)

    try {
      const sourceType: 'audio' | 'video' = op.inputTypes.includes('audio') && !op.inputTypes.includes('video') ? 'audio' : 'video'
      const payload = {
        source: {
          type: sourceType,
          uri: isJoin ? '' : sourceUri,
        },
        pipeline: isDownload ? [] : [{ operation: selectedPreset, params: { ...getDefaultParams(op), ...presetParams } }],
      }
      const job = isAuthenticated
        ? await submitJobAuth(payload)
        : await submitJob(session.apiKey, payload)
      setJobId(job.id)
      if (!isAuthenticated) {
        decrementJobsRemaining()
      }
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.errorCode === 'monthly_limit_reached') {
          if (!isAuthenticated) {
            toast.error('Monthly limit reached', {
              description: 'Sign in to get 20 jobs per month.',
              action: {
                label: 'Sign in',
                onClick: () => { window.location.href = '/login?returnTo=/web' },
              },
            })
          }
          setError(err.message)
        } else {
          setError(err.message)
        }
      } else {
        setError('Something went wrong. Please try again.')
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1 pb-20 md:pb-0">
        <section className="py-12 sm:py-16">
          <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 space-y-8">
            <div className="text-center space-y-3">
              <h1 className="text-display text-3xl sm:text-4xl text-[var(--text-primary)]">
                Process your media
              </h1>
              <p className="text-[var(--text-secondary)]">
                Paste a link or upload a file, pick an operation, get the result.
              </p>
              <RateLimitBadge />
            </div>

            {!currentJobId && !jobDetail && (
              <>
                <SourceInput />

                <div className="space-y-4">
                  <h2 className="text-label text-[var(--text-muted)]">Choose an operation</h2>
                  <PresetPicker />
                </div>

                {selectedPreset && (
                  <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-6 space-y-5">
                    <h3 className="font-semibold text-[var(--text-primary)]">
                      {getOperation(selectedPreset)?.label} parameters
                    </h3>
                    <PresetParams />

                    {validationErrors.length > 0 && (
                      <div className="rounded-lg bg-red-50 border border-red-200 p-3 dark:bg-red-950 dark:border-red-900">
                        {validationErrors.map((err) => (
                          <p key={err} className="text-sm text-red-600 dark:text-red-400">{err}</p>
                        ))}
                      </div>
                    )}

                    {error && (
                      <div className="rounded-lg bg-red-50 border border-red-200 p-3 dark:bg-red-950 dark:border-red-900">
                        <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
                      </div>
                    )}

                    <button
                      onClick={handleSubmit}
                      disabled={!canSubmit}
                      className={cn(
                        buttonVariants({ variant: 'default', size: 'lg' }),
                        'w-full gap-2',
                        !canSubmit && 'opacity-50 cursor-not-allowed',
                      )}
                    >
                      {isSubmitting ? (
                        <>
                          <Loader2 className="h-4 w-4 animate-spin" />
                          Processing...
                        </>
                      ) : (
                        'Process video'
                      )}
                    </button>
                  </div>
                )}
              </>
            )}

            {currentJobId && !jobDetail && (
              <div className="space-y-4">
                <JobSourceCard />
                <JobProgress />
              </div>
            )}
            {jobDetail && <JobResult />}

            {error && !currentJobId && !jobDetail && (
              <div className="rounded-xl border border-red-200 bg-red-50 p-6 dark:border-red-900 dark:bg-red-950">
                <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
              </div>
            )}
          </div>
        </section>

        {!currentJobId && !jobDetail && (
          <section className="pb-16">
            <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
              <HistorySection isAuthenticated={isAuthenticated} />
            </div>
          </section>
        )}
      </main>
      <Footer />
    </div>
  )
}
