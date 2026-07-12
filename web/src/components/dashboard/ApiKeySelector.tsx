import { Key } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { useApiStore } from '@/stores/apiStore'
import { listApiKeys } from '@/lib/api-keys'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'

export function ApiKeySelector() {
  const { activeApiKey, setActiveApiKey } = useApiStore()

  const { data, isLoading } = useQuery({
    queryKey: ['api-keys'],
    queryFn: listApiKeys,
  })

  const activeKeys = data?.keys?.filter(k => k.status === 'active') ?? []

  if (isLoading) {
    return (
      <div className="px-4 mb-6">
        <Skeleton className="h-9 w-full rounded-lg" />
      </div>
    )
  }

  return (
    <div className="px-4 mb-6">
      <div className="flex items-center gap-2 text-[var(--text-muted)] mb-1.5 px-1">
        <Key className="h-3 w-3" />
        <span className="text-[10px] font-bold uppercase tracking-wider">Filter by API Key</span>
      </div>
      <Select
        value={activeApiKey ?? '__all__'}
        onValueChange={(v) => setActiveApiKey(v === '__all__' ? null : v, null)}
      >
        <SelectTrigger className="w-full bg-[var(--bg-card)] border-[var(--border-subtle)] h-9 text-xs">
          <SelectValue placeholder="All Keys" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="__all__">All Keys</SelectItem>
          {activeKeys.map((key) => (
            <SelectItem key={key.id} value={key.id} className="text-xs">
              {key.name || key.key_prefix}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  )
}
