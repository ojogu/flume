import { useEffect, useState } from 'react'
import { Plus, Edit2, Trash2, Globe, LoaderCircle } from 'lucide-react'
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
import { Textarea } from '@/components/ui/textarea'
import { Checkbox } from '@/components/ui/checkbox'
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
import { 
  getPlatforms, 
  createPlatform, 
  updatePlatform, 
  deletePlatform, 
  Platform, 
  CreatePlatformRequest 
} from '@/lib/platforms'

const CONTENT_TYPES = ['single', 'playlist', 'vod']

export function PlatformsPage() {
  const [platforms, setPlatforms] = useState<Platform[]>([])
  const [loading, setLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  
  // Interaction State
  const [showDialog, setShowDialog] = useState(false)
  const [editingPlatform, setEditingPlatform] = useState<Platform | null>(null)
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [platformToDelete, setPlatformToDelete] = useState<Platform | null>(null)

  // Form State
  const [formData, setFormData] = useState<CreatePlatformRequest>({
    name: '',
    slug: '',
    url: '',
    is_active: true,
    content_types: ['single'],
    requires_login: false,
    supports_live: false,
    description: '',
    limitations: '',
    logo_url: '',
    sort_order: 0
  })

  const fetchPlatforms = async () => {
    try {
      const data = await getPlatforms()
      setPlatforms(data.platforms)
    } catch (err) {
      toast.error('Failed to load platforms')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchPlatforms()
  }, [])

  const resetForm = () => {
    setFormData({
      name: '',
      slug: '',
      url: '',
      is_active: true,
      content_types: ['single'],
      requires_login: false,
      supports_live: false,
      description: '',
      limitations: '',
      logo_url: '',
      sort_order: 0
    })
    setEditingPlatform(null)
  }

  const handleOpenCreate = () => {
    resetForm()
    setShowDialog(true)
  }

  const handleOpenEdit = (platform: Platform) => {
    setEditingPlatform(platform)
    setFormData({
      name: platform.name,
      slug: platform.slug,
      url: platform.url,
      is_active: platform.is_active,
      content_types: platform.content_types,
      requires_login: platform.requires_login,
      supports_live: platform.supports_live,
      description: platform.description || '',
      limitations: platform.limitations || '',
      logo_url: platform.logo_url || '',
      sort_order: platform.sort_order
    })
    setShowDialog(true)
  }

  const handleSave = async () => {
    if (!formData.name || !formData.slug || !formData.url) {
      toast.error('Please fill in all required fields')
      return
    }

    setIsSaving(true)
    try {
      if (editingPlatform) {
        await updatePlatform(editingPlatform.id, formData)
        toast.success('Platform updated successfully')
      } else {
        await createPlatform(formData)
        toast.success('Platform created successfully')
      }
      fetchPlatforms()
      setShowDialog(false)
    } catch (err: any) {
      toast.error(err.message || 'Failed to save platform')
    } finally {
      setIsSaving(false)
    }
  }

  const handleDelete = async () => {
    if (!platformToDelete) return
    try {
      await deletePlatform(platformToDelete.id)
      setPlatforms(prev => prev.filter(p => p.id !== platformToDelete.id))
      toast.success('Platform deleted')
    } catch (err: any) {
      toast.error('Failed to delete platform')
    } finally {
      setShowDeleteDialog(false)
      setPlatformToDelete(null)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-display text-3xl text-[var(--text-primary)]">Supported Platforms</h1>
          <p className="text-label text-[var(--text-muted)] mt-1 uppercase tracking-widest">Platform catalog and ingestion policy</p>
        </div>
        <Button onClick={handleOpenCreate} className="gap-2">
          <Plus className="h-4 w-4" />
          Add Platform
        </Button>
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
              <TableHead className="w-20 text-right font-mono text-[10px] uppercase tracking-widest text-[var(--text-muted)]">Actions</TableHead>
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
                  <TableCell className="text-right"><Skeleton className="h-8 w-16 ml-auto" /></TableCell>
                </TableRow>
              ))
            ) : platforms.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="h-64 text-center">
                  <div className="flex flex-col items-center justify-center space-y-3">
                    <Globe className="h-10 w-10 text-[var(--text-muted)] opacity-20" />
                    <p className="text-lg font-semibold text-[var(--text-primary)]">No platforms configured</p>
                    <p className="text-sm text-[var(--text-secondary)]">Add your first platform to get started</p>
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
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-1">
                      <Button 
                        variant="ghost" 
                        size="icon-sm" 
                        onClick={() => handleOpenEdit(platform)}
                        className="text-[var(--text-muted)] hover:text-brand hover:bg-brand/10 transition-colors"
                      >
                        <Edit2 className="h-3.5 w-3.5" />
                      </Button>
                      <Button 
                        variant="ghost" 
                        size="icon-sm" 
                        onClick={() => { setPlatformToDelete(platform); setShowDeleteDialog(true); }}
                        className="text-[var(--text-muted)] hover:text-destructive hover:bg-destructive/10 transition-colors"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Create/Edit Dialog */}
      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent className="sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle className="text-display text-2xl">
              {editingPlatform ? 'Update Platform' : 'Register Platform'}
            </DialogTitle>
            <DialogDescription className="text-sm">
              Configure how Flume interacts with this media source.
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 py-6 border-y border-[var(--border-subtle)] my-2">
            <div className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-widest px-1">Identity</label>
                <Input 
                  placeholder="Display Name (e.g. YouTube)" 
                  value={formData.name}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({...formData, name: e.target.value})}
                  className="bg-[var(--bg-subtle)]"
                />
                <Input 
                  placeholder="slug (e.g. youtube)" 
                  value={formData.slug}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                    const val = e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, '')
                    setFormData({...formData, slug: val})
                  }}
                  disabled={!!editingPlatform}
                  className="font-mono text-xs bg-[var(--bg-subtle)]"
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-widest px-1">Base URL</label>
                <Input 
                  placeholder="https://youtube.com" 
                  value={formData.url}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({...formData, url: e.target.value})}
                  className="bg-[var(--bg-subtle)]"
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-widest px-1">Listing Priority</label>
                <Input 
                  type="number"
                  placeholder="Sort order (0-99)"
                  value={formData.sort_order}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({...formData, sort_order: parseInt(e.target.value) || 0})}
                  className="bg-[var(--bg-subtle)]"
                />
              </div>
            </div>

            <div className="space-y-6">
              <div className="space-y-3">
                <label className="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-widest px-1 block">Behavioral Flags</label>
                <div className="space-y-3 bg-[var(--bg-subtle)] p-4 rounded-xl border border-[var(--border-subtle)]">
                  <div className="flex items-center gap-3">
                    <Checkbox 
                      id="is_active" 
                      checked={formData.is_active} 
                      onCheckedChange={(checked: boolean | 'indeterminate') => setFormData({...formData, is_active: !!checked})}
                    />
                    <label htmlFor="is_active" className="text-xs font-semibold cursor-pointer select-none">Platform Enabled</label>
                  </div>
                  <div className="flex items-center gap-3">
                    <Checkbox 
                      id="requires_login" 
                      checked={formData.requires_login} 
                      onCheckedChange={(checked: boolean | 'indeterminate') => setFormData({...formData, requires_login: !!checked})}
                    />
                    <label htmlFor="requires_login" className="text-xs font-semibold cursor-pointer select-none">Authentication Required</label>
                  </div>
                  <div className="flex items-center gap-3">
                    <Checkbox 
                      id="supports_live" 
                      checked={formData.supports_live} 
                      onCheckedChange={(checked: boolean | 'indeterminate') => setFormData({...formData, supports_live: !!checked})}
                    />
                    <label htmlFor="supports_live" className="text-xs font-semibold cursor-pointer select-none">Supports Live Streams</label>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <label className="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-widest px-1 block">Content Support</label>
                <div className="flex flex-wrap gap-x-6 gap-y-2 px-1">
                  {CONTENT_TYPES.map(type => (
                    <div key={type} className="flex items-center gap-2">
                      <Checkbox 
                        id={`type-${type}`}
                        checked={formData.content_types?.includes(type)}
                        onCheckedChange={(checked: boolean | 'indeterminate') => {
                          const current = formData.content_types || []
                          const updated = checked 
                            ? [...current, type]
                            : current.filter(t => t !== type)
                          setFormData({...formData, content_types: updated})
                        }}
                      />
                      <label htmlFor={`type-${type}`} className="text-[10px] font-mono uppercase font-bold text-[var(--text-secondary)] cursor-pointer select-none">{type}</label>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="md:col-span-2 space-y-4">
              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-widest px-1">Internal Description</label>
                <Textarea 
                  placeholder="Describe the platform integration..."
                  value={formData.description || ''}
                  onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setFormData({...formData, description: e.target.value})}
                  className="h-20 bg-[var(--bg-subtle)] resize-none"
                />
              </div>
            </div>
          </div>

          <DialogFooter className="gap-3">
            <Button variant="outline" onClick={() => setShowDialog(false)}>Cancel</Button>
            <Button onClick={handleSave} disabled={isSaving} className="min-w-[140px]">
              {isSaving ? <LoaderCircle className="h-4 w-4 animate-spin" /> : editingPlatform ? 'Save Changes' : 'Create Platform'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="text-display text-2xl">Delete Platform</AlertDialogTitle>
            <AlertDialogDescription className="text-sm">
              Permanently remove <span className="font-bold text-[var(--text-primary)]">{platformToDelete?.name}</span>? 
              This action cannot be undone and may cause issues with historical job records.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90 border-none">
              Delete Forever
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
