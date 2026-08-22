import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Clock, ArrowLeft, LogIn, Inbox, RefreshCcw } from 'lucide-react'
import { Navbar } from '@/components/common/Navbar'
import { Footer } from '@/components/common/Footer'
import { HistoryRow } from '@/components/web/HistoryRow'
import { Button, buttonVariants } from '@/components/ui/button'
import { useAuthStore } from '@/stores/authStore'
import { getJobs } from '@/lib/jobs'
import { cn } from '@/lib/utils'

const PER_PAGE = 20

export function WebHistoryPage() {
  const { accessToken } = useAuthStore()
  const [page, setPage] = useState(1)

  const { data, isLoading, isError, isFetching, refetch } = useQuery({
    queryKey: ['web-history-page', page],
    queryFn: () => getJobs({ origin: 'web', page, per_page: PER_PAGE }),
    enabled: !!accessToken,
    refetchInterval: (query) => {
      const jobs = query.state.data?.jobs ?? []
      const hasActive = jobs.some((j) => j.status === 'pending' || j.status === 'processing')
      return hasActive ? 5000 : false
    },
  })

  if (!accessToken) {
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1">
          <section className="py-12 sm:py-16">
            <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 space-y-6">
              <div>
                <h1 className="text-display text-3xl text-[var(--text-primary)]">Your media</h1>
                <p className="mt-1 text-sm text-[var(--text-secondary)]">Everything you've processed with Flume Web.</p>
              </div>
              <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-8 text-center space-y-3">
                <Clock className="h-8 w-8 mx-auto text-[var(--text-muted)] opacity-40" />
                <p className="text-sm text-[var(--text-secondary)]">Sign in to see your processing history.</p>
                <Link
                  to="/login?returnTo=/web/history"
                  className={cn(buttonVariants({ variant: 'outline', size: 'sm' }), 'gap-2 inline-flex items-center')}
                >
                  <LogIn className="h-3.5 w-3.5" />
                  Sign in
                </Link>
              </div>
            </div>
          </section>
        </main>
        <Footer />
      </div>
    )
  }

  const totalPages = data ? Math.max(1, Math.ceil(data.total / PER_PAGE)) : 1
  const jobs = data?.jobs ?? []

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1 pb-20 md:pb-0">
        <section className="py-12 sm:py-16">
          <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 space-y-8">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h1 className="text-display text-3xl text-(--text-primary)">Your media</h1>
                <p className="mt-1 text-sm leading-relaxed text-(--text-secondary)">
                  Everything you've processed with Flume Web. Click a finished job to download it.
                </p>
              </div>
              <Link
                to="/web"
                className={cn(buttonVariants({ variant: 'ghost', size: 'sm' }), 'gap-2 self-start')}
              >
                <ArrowLeft className="h-3.5 w-3.5" />
                Back to Flume Web
              </Link>
            </div>

            {isLoading ? (
              <div className="space-y-2">
                {Array.from({ length: 5 }).map((_, i) => (
                  <div key={i} className="h-[72px] animate-pulse rounded-xl bg-[var(--bg-subtle)]" />
                ))}
              </div>
            ) : isError ? (
              <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-center dark:border-red-900 dark:bg-red-950 space-y-3">
                <p className="text-sm text-red-600 dark:text-red-400">Failed to load your history.</p>
                <Button variant="outline" size="sm" onClick={() => refetch()} className="gap-2">
                  <RefreshCcw className="h-3.5 w-3.5" />
                  Try again
                </Button>
              </div>
            ) : jobs.length === 0 ? (
              <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-8 text-center space-y-3">
                <Inbox className="h-8 w-8 mx-auto text-[var(--text-muted)] opacity-20" />
                <p className="text-sm font-medium text-[var(--text-secondary)]">Nothing here yet</p>
                <p className="text-xs text-[var(--text-muted)]">Process your first video and it will show up here.</p>
                <Link
                  to="/web"
                  className={cn(buttonVariants({ variant: 'default', size: 'sm' }), 'inline-flex items-center')}
                >
                  Process a video
                </Link>
              </div>
            ) : (
              <>
                <div className="divide-y divide-[var(--border-subtle)] rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)]">
                  {jobs.map((job) => (
                    <HistoryRow key={job.id} job={job} apiKey={null} />
                  ))}
                </div>

                {totalPages > 1 && (
                  <div className="flex items-center justify-between py-2">
                    <p className="text-[11px] font-medium text-[var(--text-muted)] uppercase tracking-wider">
                      Page {page} of {totalPages}
                    </p>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        className="h-8 px-3 text-xs"
                        disabled={page === 1 || isFetching}
                        onClick={() => setPage(Math.max(1, page - 1))}
                      >
                        Previous
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        className="h-8 px-3 text-xs"
                        disabled={page >= totalPages || isFetching}
                        onClick={() => setPage(page + 1)}
                      >
                        Next
                      </Button>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </section>
      </main>
      <Footer />
    </div>
  )
}
