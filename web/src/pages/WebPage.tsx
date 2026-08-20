import { useEffect, useState } from 'react'
import { Loader2 } from 'lucide-react'
import { Navbar } from '@/components/common/Navbar'
import { Footer } from '@/components/common/Footer'
import { SourceInput } from '@/components/web/SourceInput'
import { PresetPicker } from '@/components/web/PresetPicker'
import { PresetParams } from '@/components/web/PresetParams'
import { RateLimitBadge } from '@/components/web/RateLimitBadge'
import { JobProgress } from '@/components/web/JobProgress'
import { JobResult } from '@/components/web/JobResult'
import { useWebStore } from '@/stores/webStore'
import { submitJob, ApiError } from '@/lib/web'
import { getOperation, validateRequiredParams, getDefaultParams } from '@/lib/presets'
import { buttonVariants } from '@/components/ui/button'
import { cn } from '@/lib/utils'

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
      const job = await submitJob(session.apiKey, {
        source: {
          type: op.inputTypes.includes('audio') && !op.inputTypes.includes('video') ? 'audio' : 'video',
          uri: isJoin ? '' : sourceUri,
        },
        pipeline: isDownload ? [] : [{ operation: selectedPreset, params: { ...getDefaultParams(op), ...presetParams } }],
      })
      setJobId(job.id)
      decrementJobsRemaining()
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.errorCode === 'daily_limit_reached') {
          setError('Daily job limit reached (5/day). Try again tomorrow.')
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

            {currentJobId && !jobDetail && <JobProgress />}
            {jobDetail && <JobResult />}

            {error && !currentJobId && !jobDetail && (
              <div className="rounded-xl border border-red-200 bg-red-50 p-6 dark:border-red-900 dark:bg-red-950">
                <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
              </div>
            )}
          </div>
        </section>
      </main>
      <Footer />
    </div>
  )
}
