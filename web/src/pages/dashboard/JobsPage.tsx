import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Copy, Check, RefreshCcw, AlertCircle, Inbox, ArrowRight } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select'
import { getJobs, Job } from '@/lib/jobs'
import { formatRelativeTime, cn } from '@/lib/utils'
import { useApiStore } from '@/stores/apiStore'

export function JobsPage() {
  const { activeApiKey } = useApiStore()
  const [status, setStatus] = useState<string>('all')
  const [page, setPage] = useState(1)
  const [copiedId, setCopiedId] = useState<string | null>(null)

  const { data, isLoading, isError, error, isFetching } = useQuery({
    queryKey: ['jobs', activeApiKey, status, page],
    queryFn: () => getJobs({ 
      status: status === 'all' ? undefined : status, 
      page,
      per_page: 20 
    }),
    enabled: !!activeApiKey,
    refetchInterval: 5000, // Poll every 5s for active dashboard experience
  })

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopiedId(text)
    setTimeout(() => setCopiedId(null), 2000)
  }

  const getStatusVariant = (status: Job['status']) => {
    switch (status) {
      case 'succeeded': return 'default'
      case 'failed': return 'destructive'
      case 'processing': return 'secondary'
      case 'pending': return 'outline'
      case 'partial_success': return 'secondary'
      default: return 'outline'
    }
  }

  if (!activeApiKey) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-center">
        <div className="h-16 w-16 rounded-full bg-[var(--brand-light)] flex items-center justify-center mb-6">
          <AlertCircle className="h-8 w-8 text-brand" />
        </div>
        <h2 className="text-display text-2xl text-[var(--text-primary)] mb-2">No active API key</h2>
        <p className="text-[var(--text-secondary)] max-w-sm mb-8 leading-relaxed">
          Select an API key from the sidebar to view associated jobs. 
          If you don't have a key, create one in the settings.
        </p>
        <Link to="/dashboard/keys">
          <Button variant="default" className="gap-2">
            Manage API Keys
          </Button>
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <h1 className="text-display text-3xl text-[var(--text-primary)]">Jobs</h1>
          <div className={cn(
            "flex items-center gap-2 px-2.5 py-1 rounded-full text-[10px] font-medium tracking-wider uppercase transition-all duration-300",
            isFetching ? "bg-brand/10 text-brand" : "bg-black/5 dark:bg-white/5 text-[var(--text-muted)]"
          )}>
            <RefreshCcw className={cn("h-3 w-3", isFetching && "animate-spin")} />
            {isFetching ? 'Polling' : 'Live'}
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <Select value={status} onValueChange={(v: string) => { setStatus(v); setPage(1); }}>
            <SelectTrigger className="w-[160px] bg-[var(--bg-card)]">
              <SelectValue placeholder="All Statuses" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Statuses</SelectItem>
              <SelectItem value="pending">Pending</SelectItem>
              <SelectItem value="processing">Processing</SelectItem>
              <SelectItem value="succeeded">Succeeded</SelectItem>
              <SelectItem value="failed">Failed</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="bg-[var(--bg-subtle)] hover:bg-[var(--bg-subtle)] border-none">
              <TableHead className="w-[140px] font-mono text-[10px] uppercase tracking-widest text-[var(--text-muted)]">Status</TableHead>
              <TableHead className="font-mono text-[10px] uppercase tracking-widest text-[var(--text-muted)]">Job ID</TableHead>
              <TableHead className="font-mono text-[10px] uppercase tracking-widest text-[var(--text-muted)]">Source URI</TableHead>
              <TableHead className="font-mono text-[10px] uppercase tracking-widest text-[var(--text-muted)]">Created</TableHead>
              <TableHead className="text-right font-mono text-[10px] uppercase tracking-widest text-[var(--text-muted)]">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton className="h-5 w-24" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-32" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-48" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                  <TableCell className="text-right"><Skeleton className="h-4 w-16 ml-auto" /></TableCell>
                </TableRow>
              ))
            ) : isError ? (
              <TableRow>
                <TableCell colSpan={5} className="h-48 text-center">
                  <div className="flex flex-col items-center gap-2">
                    <AlertCircle className="h-8 w-8 text-destructive opacity-50 mb-2" />
                    <p className="text-sm font-medium text-destructive">Failed to load jobs</p>
                    <p className="text-xs text-[var(--text-muted)]">{(error as any)?.message || 'Check your connection and try again.'}</p>
                  </div>
                </TableCell>
              </TableRow>
            ) : !data?.jobs?.length ? (
              <TableRow>
                <TableCell colSpan={5} className="h-48 text-center">
                  <div className="flex flex-col items-center gap-2">
                    <Inbox className="h-8 w-8 text-[var(--text-muted)] opacity-20 mb-2" />
                    <p className="text-sm font-medium text-[var(--text-secondary)]">No jobs found</p>
                    <p className="text-xs text-[var(--text-muted)]">Jobs initiated via API with this key will appear here.</p>
                  </div>
                </TableCell>
              </TableRow>
            ) : (
              data.jobs.map((job) => (
                <TableRow key={job.id} className="group hover:bg-[var(--bg-subtle)]/50 transition-colors">
                  <TableCell>
                    <Badge variant={getStatusVariant(job.status)} className="capitalize text-[10px] px-2 py-0">
                      {job.status.replace('_', ' ')}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <code className="text-[11px] font-mono text-[var(--text-secondary)] bg-[var(--bg-subtle)] px-1.5 py-0.5 rounded border border-[var(--border-subtle)]">
                        {job.id.substring(0, 8)}
                      </code>
                      <button
                        onClick={(e) => {
                          e.preventDefault()
                          copyToClipboard(job.id)
                        }}
                        className="text-[var(--text-muted)] hover:text-brand transition-colors p-1"
                      >
                        {copiedId === job.id ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                      </button>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="max-w-[280px] truncate text-sm text-[var(--text-secondary)] font-medium" title={job.source_uri}>
                      {job.source_uri}
                    </div>
                  </TableCell>
                  <TableCell className="text-sm text-[var(--text-secondary)]">
                    {formatRelativeTime(job.created_at)}
                  </TableCell>
                  <TableCell className="text-right">
                    <Link 
                      to={`/dashboard/jobs/${job.id}`}
                      className="inline-flex items-center gap-1.5 text-xs font-semibold text-brand hover:underline transition-all"
                    >
                      Inspect
                      <ArrowRight className="h-3 w-3" />
                    </Link>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {data && data.total > 20 && (
        <div className="flex items-center justify-between py-2">
          <p className="text-[11px] font-medium text-[var(--text-muted)] uppercase tracking-wider">
            Page {data.page} of {Math.ceil(data.total / 20)}
          </p>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              className="h-8 px-3 text-xs"
              disabled={page === 1}
              onClick={() => setPage(p => Math.max(1, p - 1))}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="h-8 px-3 text-xs"
              disabled={page * 20 >= data.total}
              onClick={() => setPage(p => p + 1)}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
