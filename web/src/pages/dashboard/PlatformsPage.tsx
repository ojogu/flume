import { useEffect, useState } from 'react'
import { Globe } from 'lucide-react'
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

const V1_BASE = import.meta.env.VITE_API_URL + '/v1'

interface Platform {
  id: string
  slug: string
  name: string
  url: string
  is_active: boolean
  content_types: string[]
  requires_login: boolean
  supports_live: boolean
  description: string | null
  limitations: string | null
  logo_url: string | null
  sort_order: number
}

export function PlatformsPage() {
  const [platforms, setPlatforms] = useState<Platform[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchPlatforms = async () => {
      try {
        const res = await fetch(`${V1_BASE}/utils/platforms`)
        const body = await res.json()
        if (body.status === 'success' && body.data) {
          setPlatforms(body.data.platforms)
        }
      } catch {
        // Silently fail — read-only page
      } finally {
        setLoading(false)
      }
    }
    fetchPlatforms()
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-display text-3xl text-[var(--text-primary)]">Supported Platforms</h1>
        <p className="text-label text-[var(--text-muted)] mt-1 uppercase tracking-widest">Platform catalog and ingestion policy</p>
      </div>

      <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="bg-[var(--bg-subtle)] hover:bg-[var(--bg-subtle)] border-none">
              <TableHead className="flex-1 font-mono text-[10px] uppercase tracking-widest text-[var(--text-muted)]">Name</TableHead>
              <TableHead className="w-32 font-mono text-[10px] uppercase tracking-widest text-[var(--text-muted)]">Slug</TableHead>
              <TableHead className="w-40 font-mono text-[10px] uppercase tracking-widest text-[var(--text-muted)]">Types</TableHead>
              <TableHead className="w-24 font-mono text-[10px] uppercase tracking-widest text-[var(--text-muted)]">Status</TableHead>
              <TableHead className="w-32 font-mono text-[10px] uppercase tracking-widest text-[var(--text-muted)]">Flags</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              Array.from({ length: 3 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton className="h-5 w-32" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-20" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                </TableRow>
              ))
            ) : platforms.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="h-64 text-center">
                  <div className="flex flex-col items-center justify-center space-y-3">
                    <Globe className="h-10 w-10 text-[var(--text-muted)] opacity-20" />
                    <p className="text-lg font-semibold text-[var(--text-primary)]">No platforms available</p>
                  </div>
                </TableCell>
              </TableRow>
            ) : (
              platforms.sort((a, b) => a.sort_order - b.sort_order).map((platform) => (
                <TableRow key={platform.id} className="group hover:bg-[var(--bg-subtle)]/50 transition-colors">
                  <TableCell>
                    <div className="flex flex-col">
                      <span className="font-bold text-[var(--text-primary)]">{platform.name}</span>
                      <span className="text-xs text-[var(--text-muted)] truncate max-w-[200px]">{platform.url}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <code className="text-[11px] font-mono text-[var(--text-secondary)] bg-[var(--bg-subtle)] px-1.5 py-0.5 rounded border border-[var(--border-subtle)]">
                      {platform.slug}
                    </code>
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-wrap gap-1">
                      {platform.content_types.map(type => (
                        <Badge key={type} variant="outline" className="text-[10px] h-4 uppercase px-1 tracking-tighter">{type}</Badge>
                      ))}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant={platform.is_active ? 'default' : 'secondary'} className="text-[9px] h-4 font-bold uppercase tracking-widest px-1.5">
                      {platform.is_active ? 'Active' : 'Off'}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-wrap gap-1">
                      {platform.requires_login && <Badge className="text-[9px] h-4 bg-orange-500/10 text-orange-600 border-none">Login</Badge>}
                      {platform.supports_live && <Badge className="text-[9px] h-4 bg-red-500/10 text-red-600 border-none">Live</Badge>}
                    </div>
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
