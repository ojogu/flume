import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, Folder, Inbox, LogIn, RefreshCcw } from 'lucide-react'
import { Navbar } from '@/components/common/Navbar'
import { Footer } from '@/components/common/Footer'
import { HistoryRow, formatFolderCounts, getStatusBadge } from '@/components/web/HistoryRow'
import { Button, buttonVariants } from '@/components/ui/button'
import { useAuthStore } from '@/stores/authStore'
import { getJob, getJobChildren, getSourceThumbnail, getSourceTitle } from '@/lib/jobs'
import { cn, formatRelativeTime } from '@/lib/utils'

const PER_PAGE = 20

const isActive = (status: string) => status === 'pending' || status === 'processing'

export function WebFolderPage() {
  const { jobId = '' } = useParams<{ jobId: string }>()
  const { accessToken } = useAuthStore()
  const [page, setPage] = useState(1)
  const [imgError, setImgError] = useState(false)

  const parentQuery = useQuery({
    queryKey: ['web-folder', jobId],
    queryFn: () => getJob(jobId),
    enabled: !!accessToken && !!jobId,
    refetchInterval: (query) => {
      const status = query.state.data?.status
      return status && isActive(status) ? 5000 : false
    },
  })

  const childrenQuery = useQuery({
    queryKey: ['web-folder-children', jobId, page],
    queryFn: () => getJobChildren(jobId, page, PER_PAGE),
    enabled: !!accessToken && !!jobId,
    refetchInterval: (query) => {
      const parentActive = parentQuery.data ? isActive(parentQuery.data.status) : false
      const childActive = (query.state.data?.jobs ?? []).some((j) => isActive(j.status))
      return parentActive || childActive ? 5000 : false
    },
  })

  if (!accessToken) {
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1">
          <section className="py-12 sm:py-16">
            <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
              <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-8 text-center space-y-3">
                <p className="text-sm text-[var(--text-secondary)]">Sign in to see this playlist.</p>
                <Link
                  to={`/login?returnTo=/web/history/${jobId}`}
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

  const parent = parentQuery.data
  const children = childrenQuery.data?.jobs ?? []
  const totalPages = childrenQuery.data ? Math.max(1, Math.ceil(childrenQuery.data.total / PER_PAGE)) : 1

  // Old playlists have no saved title/thumbnail — borrow the first video's (page 1 only).
  const firstChild = page === 1 ? children[0] : undefined
  const title =
    getSourceTitle(parent?.source_metadata) ?? getSourceTitle(firstChild?.source_metadata) ?? 'Playlist'
  const thumbnailUrl =
    getSourceThumbnail(parent?.source_metadata) ?? getSourceThumbnail(firstChild?.source_metadata)

  const isError = parentQuery.isError || childrenQuery.isError
  const isLoading = parentQuery.isLoading || childrenQuery.isLoading

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1 pb-20 md:pb-0">
        <section className="py-12 sm:py-16">
          <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 space-y-6">
            <Link
              to="/web/history"
              className={cn(buttonVariants({ variant: 'ghost', size: 'sm' }), 'gap-2 self-start inline-flex')}
            >
              <ArrowLeft className="h-3.5 w-3.5" />
              Back to your media
            </Link>

            {isLoading ? (
              <div className="space-y-2">
                <div className="h-24 animate-pulse rounded-xl bg-[var(--bg-subtle)]" />
                {Array.from({ length: 4 }).map((_, i) => (
                  <div key={i} className="h-[72px] animate-pulse rounded-xl bg-[var(--bg-subtle)]" />
                ))}
              </div>
            ) : isError || !parent ? (
              <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-center dark:border-red-900 dark:bg-red-950 space-y-3">
                <p className="text-sm text-red-600 dark:text-red-400">Couldn't load this playlist.</p>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    parentQuery.refetch()
                    childrenQuery.refetch()
                  }}
                  className="gap-2"
                >
                  <RefreshCcw className="h-3.5 w-3.5" />
                  Try again
                </Button>
              </div>
            ) : (
              <>
                <div className="flex items-center gap-4 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-4">
                  <div className="h-16 w-28 shrink-0 overflow-hidden rounded-md bg-[var(--bg-subtle)]">
                    {thumbnailUrl && !imgError ? (
                      <img
                        src={thumbnailUrl}
                        alt=""
                        className="h-full w-full object-cover"
                        onError={() => setImgError(true)}
                      />
                    ) : (
                      <div className="flex h-full w-full items-center justify-center">
                        <Folder className="h-6 w-6 text-[var(--text-muted)] opacity-40" aria-hidden="true" />
                      </div>
                    )}
                  </div>
                  <div className="min-w-0 flex-1 space-y-1">
                    <h1 className="truncate text-base font-semibold text-[var(--text-primary)]">{title}</h1>
                    <p className="truncate text-xs text-[var(--text-muted)]">
                      {formatFolderCounts(parent)} · {formatRelativeTime(parent.created_at)}
                    </p>
                  </div>
                  <span
                    className={cn(
                      'shrink-0 rounded-full px-2 py-0.5 text-[10px] font-medium capitalize',
                      getStatusBadge(parent.status),
                    )}
                  >
                    {parent.status.replace('_', ' ')}
                  </span>
                </div>

                {children.length === 0 ? (
                  <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-8 text-center space-y-3">
                    <Inbox className="h-8 w-8 mx-auto text-[var(--text-muted)] opacity-20" />
                    <p className="text-sm text-[var(--text-secondary)]">
                      {isActive(parent.status) ? 'Getting your videos ready…' : 'No videos in this playlist.'}
                    </p>
                  </div>
                ) : (
                  <div className="divide-y divide-[var(--border-subtle)] rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)]">
                    {children.map((job) => (
                      <HistoryRow key={job.id} job={job} apiKey={null} />
                    ))}
                  </div>
                )}

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
                        disabled={page === 1 || childrenQuery.isFetching}
                        onClick={() => setPage(Math.max(1, page - 1))}
                      >
                        Previous
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        className="h-8 px-3 text-xs"
                        disabled={page >= totalPages || childrenQuery.isFetching}
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
