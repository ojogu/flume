import { useQuery } from '@tanstack/react-query'
import { BarChart3, Users, Briefcase, Globe } from 'lucide-react'
import { apiClient } from '@/lib/api'

interface Stats {
  period_days: number
  page_views: {
    total: number
    unique_visitors: number
    top_paths: Array<{ path: string; views: number }>
    top_referrers: Array<{ referrer: string; views: number }>
  }
  jobs: {
    total: number
    by_origin: Record<string, number>
    by_status: Record<string, number>
  }
}

async function getStats(days: number): Promise<Stats> {
  const res = await apiClient<{ status: string; data: Stats }>(`/stats?days=${days}`)
  return res.data
}

function StatCard({ label, value, icon: Icon }: { label: string; value: number | string; icon: React.ElementType }) {
  return (
    <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-4 space-y-1">
      <div className="flex items-center gap-2 text-[var(--text-muted)]">
        <Icon className="h-4 w-4" />
        <span className="text-xs font-medium uppercase tracking-wider">{label}</span>
      </div>
      <p className="text-2xl font-semibold text-[var(--text-primary)]">{value}</p>
    </div>
  )
}

export function AdminStatsPage() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['admin-stats', 30],
    queryFn: () => getStats(30),
  })

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 animate-pulse rounded bg-[var(--bg-subtle)]" />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-24 animate-pulse rounded-xl bg-[var(--bg-subtle)]" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-display text-3xl text-[var(--text-primary)]">Stats</h1>
        <p className="mt-1 text-sm text-[var(--text-secondary)]">Last 30 days overview.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Page views" value={stats?.page_views.total ?? 0} icon={BarChart3} />
        <StatCard label="Unique visitors" value={stats?.page_views.unique_visitors ?? 0} icon={Users} />
        <StatCard label="Total jobs" value={stats?.jobs.total ?? 0} icon={Briefcase} />
        <StatCard label="Web jobs" value={stats?.jobs.by_origin?.web ?? 0} icon={Globe} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-6 space-y-4">
          <h2 className="font-semibold text-[var(--text-primary)]">Jobs by origin</h2>
          <div className="space-y-2">
            {Object.entries(stats?.jobs.by_origin ?? {}).map(([origin, count]) => (
              <div key={origin} className="flex items-center justify-between text-sm">
                <span className="capitalize text-[var(--text-secondary)]">{origin}</span>
                <span className="font-mono font-medium text-[var(--text-primary)]">{count}</span>
              </div>
            ))}
            {Object.keys(stats?.jobs.by_origin ?? {}).length === 0 && (
              <p className="text-sm text-[var(--text-muted)]">No data yet.</p>
            )}
          </div>
        </div>

        <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-6 space-y-4">
          <h2 className="font-semibold text-[var(--text-primary)]">Jobs by status</h2>
          <div className="space-y-2">
            {Object.entries(stats?.jobs.by_status ?? {}).map(([status, count]) => (
              <div key={status} className="flex items-center justify-between text-sm">
                <span className="capitalize text-[var(--text-secondary)]">{status.replace('_', ' ')}</span>
                <span className="font-mono font-medium text-[var(--text-primary)]">{count}</span>
              </div>
            ))}
            {Object.keys(stats?.jobs.by_status ?? {}).length === 0 && (
              <p className="text-sm text-[var(--text-muted)]">No data yet.</p>
            )}
          </div>
        </div>

        <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-6 space-y-4">
          <h2 className="font-semibold text-[var(--text-primary)]">Top paths</h2>
          <div className="space-y-2">
            {stats?.page_views.top_paths.map((item) => (
              <div key={item.path} className="flex items-center justify-between text-sm">
                <code className="truncate text-xs font-mono text-[var(--text-secondary)] max-w-[200px]">{item.path}</code>
                <span className="font-mono font-medium text-[var(--text-primary)]">{item.views}</span>
              </div>
            ))}
            {(!stats?.page_views.top_paths || stats.page_views.top_paths.length === 0) && (
              <p className="text-sm text-[var(--text-muted)]">No data yet.</p>
            )}
          </div>
        </div>

        <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-6 space-y-4">
          <h2 className="font-semibold text-[var(--text-primary)]">Top referrers</h2>
          <div className="space-y-2">
            {stats?.page_views.top_referrers.map((item) => (
              <div key={item.referrer} className="flex items-center justify-between text-sm">
                <span className="truncate text-xs text-[var(--text-secondary)] max-w-[200px]" title={item.referrer}>{item.referrer}</span>
                <span className="font-mono font-medium text-[var(--text-primary)]">{item.views}</span>
              </div>
            ))}
            {(!stats?.page_views.top_referrers || stats.page_views.top_referrers.length === 0) && (
              <p className="text-sm text-[var(--text-muted)]">No data yet.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
