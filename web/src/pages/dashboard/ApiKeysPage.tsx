import { useEffect, useState } from 'react'
import { Copy, Check, Trash2, AlertTriangle, LoaderCircle, Plus } from 'lucide-react'
import { toast } from 'sonner'
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogFooter, 
  DialogHeader, 
  DialogTitle 
} from '@/components/ui/dialog'
import { 
  AlertDialog, 
  AlertDialogAction, 
  AlertDialogCancel, 
  AlertDialogContent, 
  AlertDialogDescription, 
  AlertDialogFooter, 
  AlertDialogHeader, 
  AlertDialogTitle 
} from '@/components/ui/alert-dialog'
import { listApiKeys, createApiKey, revokeApiKey, ApiKey, ApiKeyCreated } from '@/lib/api-keys'
import { formatRelativeTime, cn } from '@/lib/utils'
import { useApiStore } from '@/stores/apiStore'

export function ApiKeysPage() {
  const { activeApiKey, setActiveApiKey } = useApiStore()
  const [keys, setKeys] = useState<ApiKey[]>([])
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [revokingId, setRevokingId] = useState<string | null>(null)
  
  // Create Modal State
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newKeyName, setNewKeyName] = useState('')
  const [createdKey, setCreatedKey] = useState<ApiKeyCreated | null>(null)
  const [keyCopied, setKeyCopied] = useState(false)
  const [acknowledged, setAcknowledged] = useState(false)

  const fetchKeys = async () => {
    try {
      const data = await listApiKeys()
      setKeys(data.keys)
    } catch (err) {
      console.error('Failed to fetch keys', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchKeys()
  }, [])

  const handleCreateKey = async () => {
    if (!newKeyName.trim()) return
    setCreating(true)
    try {
      const key = await createApiKey({ name: newKeyName })
      setCreatedKey(key)
      fetchKeys()
    } catch (err) {
      console.error('Failed to create key', err)
    } finally {
      setCreating(false)
    }
  }

  const handleRevokeKey = async () => {
    if (!revokingId) return
    const id = revokingId
    try {
      await revokeApiKey(id)
      setKeys((prev) => prev.filter((k) => k.id !== id))
    } catch (err) {
      toast.error('An error occurred')
    } finally {
      setRevokingId(null)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    setKeyCopied(true)
    setTimeout(() => setKeyCopied(false), 2000)
  }

  const resetCreateState = () => {
    setShowCreateModal(false)
    setNewKeyName('')
    setCreatedKey(null)
    setAcknowledged(false)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-display text-3xl text-[var(--text-primary)]">API Keys</h1>
        <Button 
          onClick={() => setShowCreateModal(true)}
          className="gap-2"
        >
          <Plus className="h-4 w-4" />
          Create new key
        </Button>
      </div>

      <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="bg-[var(--bg-subtle)] hover:bg-[var(--bg-subtle)]">
              <TableHead>Label</TableHead>
              <TableHead>Prefix</TableHead>
              <TableHead>Last Used</TableHead>
              <TableHead>Created</TableHead>
              <TableHead className="text-right">Action</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              Array.from({ length: 3 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton className="h-4 w-32" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-20" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-20" /></TableCell>
                  <TableCell className="text-right"><Skeleton className="h-8 w-8 ml-auto rounded-lg" /></TableCell>
                </TableRow>
              ))
            ) : keys.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="h-32 text-center text-[var(--text-muted)]">
                  No API keys found. Create one to get started.
                </TableCell>
              </TableRow>
            ) : (
              keys.map((key) => (
                <TableRow key={key.id} className={cn(key.status === 'revoked' && "opacity-50")}>
                  <TableCell className="font-semibold text-[var(--text-primary)]">
                    {key.name}
                  </TableCell>
                  <TableCell>
                    <code className="text-xs font-mono text-[var(--text-secondary)] bg-[var(--bg-subtle)] px-1.5 py-0.5 rounded">
                      {key.key_prefix}
                    </code>
                  </TableCell>
                  <TableCell className="text-sm text-[var(--text-secondary)]">
                    {key.last_used_at ? formatRelativeTime(key.last_used_at) : 'Never'}
                  </TableCell>
                  <TableCell className="text-sm text-[var(--text-secondary)]">
                    {key.created_at ? formatRelativeTime(key.created_at) : '--'}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-2">
                      {key.status === 'active' && activeApiKey !== key.id && (
                        <Button
                          variant="outline"
                          size="sm"
                          className="h-7 text-[10px] uppercase font-bold"
                          onClick={() => setActiveApiKey(key.id, key.name)}
                        >
                          Activate
                        </Button>
                      )}
                      {key.status === 'active' && activeApiKey === key.id && (
                        <Badge className="bg-brand/20 text-brand border-none hover:bg-brand/20 text-[10px] uppercase font-bold tracking-wider h-7">Active</Badge>
                      )}
                      {key.status === 'active' ? (
                        <Button
                          variant="ghost"
                          size="icon-sm"
                          onClick={() => setRevokingId(key.id)}
                          className="text-[var(--text-muted)] hover:text-destructive hover:bg-destructive/10"
                          title="Revoke key"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      ) : (
                        <Badge variant="secondary">Revoked</Badge>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Create Key Modal */}
      <Dialog open={showCreateModal} onOpenChange={() => {
        if (!createdKey || acknowledged) resetCreateState()
      }}>
        <DialogContent className={cn(createdKey && "sm:max-w-md")}>
          <DialogHeader>
            <DialogTitle>
              {createdKey ? 'API Key Created' : 'Create new API key'}
            </DialogTitle>
            <DialogDescription>
              {createdKey 
                ? 'Copy this key now. For your security, it will not be shown again.' 
                : 'Give your key a label to help you identify it later.'}
            </DialogDescription>
          </DialogHeader>

          {!createdKey ? (
            <div className="space-y-6 py-4">
              <div className="space-y-2">
                <p className="text-label text-[var(--text-muted)] px-1 tracking-wider">Label</p>
                <Input 
                  placeholder="e.g. Production Web App" 
                  value={newKeyName}
                  onChange={(e) => setNewKeyName(e.target.value)}
                  autoFocus
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && newKeyName.trim()) handleCreateKey()
                  }}
                />
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setShowCreateModal(false)}>Cancel</Button>
                <Button 
                  onClick={handleCreateKey} 
                  disabled={!newKeyName.trim() || creating}
                  className="min-w-[100px]"
                >
                  {creating ? <LoaderCircle className="h-4 w-4 animate-spin" /> : 'Create key'}
                </Button>
              </DialogFooter>
            </div>
          ) : (
            <div className="space-y-6 py-4">
              <div className="relative">
                <div className="flex items-center gap-2 p-4 bg-black/5 dark:bg-black/40 rounded-lg border border-[var(--border-subtle)] font-mono text-xs break-all pr-12 text-[var(--text-primary)] leading-relaxed">
                  {createdKey.full_key}
                </div>
                <Button
                  variant="ghost"
                  size="icon-sm"
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-[var(--text-muted)] hover:text-brand"
                  onClick={() => copyToClipboard(createdKey.full_key)}
                >
                  {keyCopied ? <Check className="h-4 w-4 text-brand" /> : <Copy className="h-4 w-4" />}
                </Button>
              </div>

              <div className="flex items-start gap-3 p-4 bg-orange-500/10 border border-orange-500/20 rounded-xl text-orange-600 dark:text-orange-400">
                <AlertTriangle className="h-5 w-5 shrink-0 mt-0.5" />
                <p className="text-xs font-medium leading-relaxed">
                  Once you close this window, you will never be able to see this key again. Please store it securely in a password manager.
                </p>
              </div>

              <div className="flex items-center gap-3 bg-[var(--bg-subtle)] p-3 rounded-lg border border-[var(--border-subtle)]">
                <input 
                  type="checkbox" 
                  id="acknowledge" 
                  className="rounded border-[var(--border-subtle)] text-brand focus:ring-brand"
                  checked={acknowledged}
                  onChange={(e) => setAcknowledged(e.target.checked)}
                />
                <label htmlFor="acknowledge" className="text-sm text-[var(--text-secondary)] font-medium cursor-pointer select-none">
                  I have saved this key in a secure place
                </label>
              </div>

              <DialogFooter>
                <Button 
                  className="w-full" 
                  disabled={!acknowledged}
                  onClick={resetCreateState}
                >
                  Done
                </Button>
              </DialogFooter>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Revoke Confirmation */}
      <AlertDialog open={!!revokingId} onOpenChange={(open) => !open && setRevokingId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Revoke API Key</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure? This action cannot be undone. Any applications using this API key will immediately stop working and receive 401 Unauthorized errors.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleRevokeKey}>
              Revoke Key
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
