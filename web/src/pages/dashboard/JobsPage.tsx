import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Copy, Check, ExternalLink } from 'lucide-react'
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
import { getJobs, Job } from '@/lib/jobs'
import { formatRelativeTime, formatDuration } from '@/lib/utils'

export function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(true)
  const [copiedId, setCopiedId] = useState<string | null>(null)

  useEffect(() => {
    getJobs().then((data) => {
      setJobs(data)
      setLoading(false)
    })
  }, [])

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopiedId(text)
    setTimeout(() => setCopiedId(null), 2000)
  }

  const getStatusVariant = (status: Job['status']) => {
    switch (status) {
      case 'completed': return 'default'
      case 'failed': return 'destructive'
      case 'processing': return 'secondary'
      case 'pending': return 'outline'
      default: return 'outline'
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-display text-3xl text-[var(--text-primary)]">Jobs</h1>
      </div>

      <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="bg-[var(--bg-subtle)] hover:bg-[var(--bg-subtle)]">
              <TableHead className="w-[120px]">Status</TableHead>
              <TableHead>Job ID</TableHead>
              <TableHead>Operation</TableHead>
              <TableHead>Created</TableHead>
              <TableHead className="text-right">Duration</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton className="h-5 w-20" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-32" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-40" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                  <TableCell className="text-right"><Skeleton className="h-4 w-16 ml-auto" /></TableCell>
                </TableRow>
              ))
            ) : jobs.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="h-32 text-center text-[var(--text-muted)]">
                  No jobs found.
                </TableCell>
              </TableRow>
            ) : (
              jobs.map((job) => (
                <TableRow key={job.id} className="group">
                  <TableCell>
                    <Badge variant={getStatusVariant(job.status)} className="capitalize">
                      {job.status}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <code className="text-xs font-mono text-[var(--text-secondary)] bg-[var(--bg-subtle)] px-1.5 py-0.5 rounded">
                        {job.id.substring(0, 8)}...
                      </code>
                      <button
                        onClick={(e) => {
                          e.preventDefault()
                          copyToClipboard(job.id)
                        }}
                        className="text-[var(--text-muted)] hover:text-brand transition-colors p-1"
                        title="Copy full ID"
                      >
                        {copiedId === job.id ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                      </button>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Link 
                      to={`/dashboard/jobs/${job.id}`}
                      className="text-sm font-medium text-[var(--text-primary)] hover:text-brand flex items-center gap-1.5"
                    >
                      {job.operation}
                      <ExternalLink className="h-3 w-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                    </Link>
                  </TableCell>
                  <TableCell className="text-sm text-[var(--text-secondary)]">
                    {formatRelativeTime(job.created_at)}
                  </TableCell>
                  <TableCell className="text-right text-sm font-mono text-[var(--text-secondary)]">
                    {formatDuration(job.duration_ms)}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
