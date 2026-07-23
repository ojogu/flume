import { useState } from 'react'
import { Plus, Webhook, Trash2, AlertCircle, Check, Copy, Play, Loader2, Info, Pencil } from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { Checkbox } from '@/components/ui/checkbox'
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from '@/components/ui/accordion'
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogFooter, 
  DialogHeader, 
  DialogTitle 
} from '@/components/ui/dialog'
import { 
  listWebhooks, 
  createWebhook, 
  updateWebhook,
  deleteWebhook, 
  testWebhook, 
  listWebhookDeliveries,
  WebhookSubscription 
} from '@/lib/webhooks'
import { formatRelativeTime, cn } from '@/lib/utils'
import { useApiStore } from '@/stores/apiStore'

const EVENT_CATALOG = [
  { type: 'job.created', description: 'Job was created and queued for processing', group: 'Job events' },
  { type: 'job.processing', description: 'Worker picked up the job for execution', group: 'Job events' },
  { type: 'job.completed', description: 'Job finished successfully — all pipeline steps passed', group: 'Job events' },
  { type: 'job.failed', description: 'Job could not complete', group: 'Job events' },
  { type: 'step.started', description: 'Pipeline step began execution', group: 'Step events' },
  { type: 'step.completed', description: 'Pipeline step finished successfully', group: 'Step events' },
  { type: 'step.failed', description: 'Pipeline step failed', group: 'Step events' },
]

const JOB_EVENTS = EVENT_CATALOG.filter(e => e.group === 'Job events')
const STEP_EVENTS = EVENT_CATALOG.filter(e => e.group === 'Step events')

export function WebhooksPage() {
  const { activeApiKey } = useApiStore()
  const queryClient = useQueryClient()
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [editingWebhook, setEditingWebhook] = useState<WebhookSubscription | null>(null)
  const [url, setUrl] = useState('')
  const [createdSecret, setCreatedSecret] = useState<string | null>(null)

  const { data: webhooks, isLoading, isError } = useQuery({
    queryKey: ['webhooks', activeApiKey],
    queryFn: () => listWebhooks(activeApiKey || undefined),
  })

  const createMutation = useMutation({
    mutationFn: createWebhook,
    onSuccess: (data) => {
      setCreatedSecret(data.secret || null)
      queryClient.invalidateQueries({ queryKey: ['webhooks'] })
      toast.success('Webhook created')
    },
    onError: (err: any) => toast.error(err.message || 'Failed to create webhook')
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, ...req }: { id: string; url?: string; events?: string[] }) => updateWebhook(id, req),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['webhooks'] })
      toast.success('Webhook updated')
      setShowEditModal(false)
      setEditingWebhook(null)
    },
    onError: (err: any) => toast.error(err.message || 'Failed to update webhook')
  })

  const deleteMutation = useMutation({
    mutationFn: deleteWebhook,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['webhooks'] })
      toast.success('Webhook deleted')
    }
  })

  const handleCreate = (events: string[]) => {
    if (!url || !activeApiKey) return
    createMutation.mutate({ api_key_id: activeApiKey, url, events })
  }

  const handleEdit = (events: string[]) => {
    if (!editingWebhook) return
    updateMutation.mutate({ id: editingWebhook.id, url: editingWebhook.url, events })
  }

  const handleReset = () => {
    setShowCreateModal(false)
    setUrl('')
    setCreatedSecret(null)
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-display text-3xl text-[var(--text-primary)]">Webhooks</h1>
          <p className="text-[var(--text-secondary)] mt-1">Listen for Flume events in real-time.</p>
        </div>
        <Button onClick={() => setShowCreateModal(true)} className="gap-2" disabled={!activeApiKey}>
          <Plus className="h-4 w-4" />
          Add endpoint
        </Button>
      </div>

      <div className="space-y-4">
        {isLoading ? (
          Array.from({ length: 2 }).map((_, i) => (
            <Skeleton key={i} className="h-32 w-full rounded-xl" />
          ))
        ) : isError ? (
          <div className="p-12 border border-dashed rounded-xl text-center bg-destructive/5 border-destructive/20">
            <AlertCircle className="h-8 w-8 text-destructive mx-auto mb-4 opacity-50" />
            <p className="text-destructive font-medium">Failed to load webhooks</p>
          </div>
        ) : webhooks?.length === 0 ? (
          <div className="p-16 border border-dashed border-[var(--border-subtle)] rounded-xl text-center bg-[var(--bg-subtle)]/30">
            <Webhook className="h-10 w-10 text-[var(--text-muted)] mx-auto mb-4 opacity-20" />
            <h3 className="text-lg font-semibold text-[var(--text-primary)]">
              {activeApiKey ? 'No endpoints configured' : 'Select an API key'}
            </h3>
            <p className="text-[var(--text-secondary)] mt-1 mb-6 text-sm max-w-sm mx-auto">
              {activeApiKey
                ? 'Register a URL to receive processing updates, job completion notifications, and more directly in your system.'
                : 'Select an API key above to view and manage its webhooks.'}
            </p>
            {activeApiKey && <Button variant="outline" onClick={() => setShowCreateModal(true)}>Register your first webhook</Button>}
          </div>
        ) : (
          webhooks?.map(webhook => (
            <WebhookCard 
              key={webhook.id} 
              webhook={webhook} 
              onDelete={() => deleteMutation.mutate(webhook.id)}
              onEdit={() => { setEditingWebhook(webhook); setShowEditModal(true) }}
            />
          ))
        )}
      </div>

      <CreateWebhookDialog 
        open={showCreateModal} 
        onOpenChange={(open: boolean) => !open && handleReset()}
        url={url} setUrl={setUrl}
        onSave={handleCreate}
        loading={createMutation.isPending}
        secret={createdSecret}
      />

      {editingWebhook && (
        <EditWebhookDialog
          open={showEditModal}
          onOpenChange={(open: boolean) => { if (!open) { setShowEditModal(false); setEditingWebhook(null) } }}
          webhook={editingWebhook}
          onSave={handleEdit}
          loading={updateMutation.isPending}
        />
      )}
    </div>
  )
}

function WebhookCard({ webhook, onDelete, onEdit }: { webhook: WebhookSubscription, onDelete: () => void, onEdit: () => void }) {
  const [testing, setTesting] = useState(false)
  const [testResult, setTestResult] = useState<{success: boolean, code: number | null, body: string} | null>(null)

  const handleTest = async () => {
    setTesting(true)
    setTestResult(null)
    try {
      const res = await testWebhook(webhook.id)
      setTestResult({ success: res.success, code: res.status_code, body: res.response_body })
    } catch (err: any) {
      setTestResult({ success: false, code: null, body: err.message || 'Network error' })
    } finally {
      setTesting(false)
    }
  }

  return (
    <div className="group rounded-xl bg-[var(--bg-card)] border border-[var(--border-subtle)] overflow-hidden transition-all duration-200 hover:border-[var(--border-strong)]">
      <div className="p-6">
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-3 mb-3">
              <code className="text-sm font-semibold text-[var(--text-primary)] truncate block max-w-md lg:max-w-xl">
                {webhook.url}
              </code>
              <Badge variant={webhook.is_active ? 'default' : 'secondary'} className="text-[10px] px-2 py-0 h-4 uppercase font-bold tracking-wider">
                {webhook.is_active ? 'Active' : 'Disabled'}
              </Badge>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {webhook.events.includes('*') ? (
                <span className="text-[10px] font-mono font-bold bg-brand/5 text-brand px-2 py-0.5 rounded border border-brand/20">
                  All events
                </span>
              ) : webhook.events.map(e => (
                <span key={e} className="text-[10px] font-mono font-bold bg-[var(--bg-subtle)] text-[var(--text-secondary)] px-2 py-0.5 rounded border border-[var(--border-subtle)]">
                  {e}
                </span>
              ))}
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Button 
              variant="outline" 
              size="sm" 
              className="h-8 gap-2 text-[10px] uppercase font-bold"
              onClick={handleTest}
              disabled={testing}
            >
              {testing ? <Loader2 className="h-3 w-3 animate-spin" /> : <Play className="h-3 w-3 fill-current" />}
              Test Connection
            </Button>
            <Button 
              variant="ghost" 
              size="icon-sm" 
              className="text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-subtle)]"
              onClick={onEdit}
            >
              <Pencil className="h-4 w-4" />
            </Button>
            <Button 
              variant="ghost" 
              size="icon-sm" 
              className="text-[var(--text-muted)] hover:text-destructive hover:bg-destructive/10"
              onClick={onDelete}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {testResult && (
          <div className={cn(
            "mt-5 p-4 rounded-lg border flex gap-3 animate-in fade-in slide-in-from-top-2",
            testResult.success 
              ? "bg-green-500/5 border-green-500/20 text-green-600 dark:text-green-400" 
              : "bg-destructive/5 border-destructive/20 text-destructive"
          )}>
            <div className={cn(
              "h-5 w-5 rounded-full flex items-center justify-center shrink-0 border border-current mt-0.5",
              testResult.success ? "bg-green-500/10" : "bg-destructive/10"
            )}>
              {testResult.success ? <Check className="h-3 w-3" /> : <AlertCircle className="h-3 w-3" />}
            </div>
            <div className="min-w-0">
              <p className="text-[10px] font-bold uppercase tracking-wider mb-1">
                {testResult.success ? 'Success' : 'Test Failed'} — Status {testResult.code || 'Timeout'}
              </p>
              <p className="text-xs font-mono break-all opacity-80 leading-relaxed">{testResult.body}</p>
            </div>
          </div>
        )}
      </div>

      <Accordion>
        <AccordionItem value="logs" className="border-t border-[var(--border-subtle)]">
          <AccordionTrigger className="px-6 py-3 h-auto text-[10px] uppercase font-bold tracking-widest text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-subtle)]/50 border-none hover:no-underline">
            Recent deliveries
          </AccordionTrigger>
          <AccordionContent className="px-6 pb-6 pt-2">
            <DeliveryLogs subscriptionId={webhook.id} />
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  )
}

function DeliveryLogs({ subscriptionId }: { subscriptionId: string }) {
  const { data: logs, isLoading } = useQuery({
    queryKey: ['webhook-logs', subscriptionId],
    queryFn: () => listWebhookDeliveries(subscriptionId),
  })

  if (isLoading) return (
    <div className="space-y-2">
      <Skeleton className="h-10 w-full" />
      <Skeleton className="h-10 w-full" />
    </div>
  )
  
  if (!logs?.length) return (
    <div className="py-8 text-center border border-dashed border-[var(--border-subtle)] rounded-lg">
      <p className="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider">No recent activity</p>
    </div>
  )

  return (
    <div className="space-y-2">
      {logs.map(log => (
        <div key={log.id} className="flex items-center justify-between p-3 bg-[var(--bg-subtle)] rounded-lg text-xs border border-[var(--border-subtle)]">
          <div className="flex items-center gap-3">
            <div className={cn(
              "h-2 w-2 rounded-full",
              log.status === 'delivered' ? "bg-brand" : "bg-destructive"
            )} />
            <span className="font-mono font-bold text-[var(--text-primary)]">{log.event_type}</span>
            <span className="text-[10px] text-[var(--text-muted)] font-medium">{formatRelativeTime(log.created_at)}</span>
          </div>
          <div className="flex items-center gap-4">
            <span className={cn(
              "font-mono font-bold",
              log.response_code && log.response_code < 300 ? "text-brand" : "text-destructive"
            )}>{log.response_code || '---'}</span>
            <Badge variant="outline" className="text-[9px] uppercase tracking-tighter font-bold h-4">
              {log.status}
            </Badge>
          </div>
        </div>
      ))}
    </div>
  )
}

function EventSelector({ selectedEvents, onChange }: { selectedEvents: string[], onChange: (events: string[]) => void }) {
  const allEvents = selectedEvents.includes('*')

  const toggleAll = () => {
    onChange(allEvents ? [] : ['*'])
  }

  const toggleEvent = (type: string) => {
    if (allEvents) return
    if (selectedEvents.includes(type)) {
      onChange(selectedEvents.filter(e => e !== type))
    } else {
      onChange([...selectedEvents, type])
    }
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2.5">
        <Checkbox checked={allEvents} onCheckedChange={toggleAll} />
        <span className="text-sm font-medium text-[var(--text-primary)]">Receive all events</span>
      </div>

      {!allEvents && (
        <div className="space-y-4 pl-1">
          <div>
            <p className="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-widest mb-2">Job events</p>
            <div className="space-y-1">
              {JOB_EVENTS.map(event => (
                <label key={event.type} className="flex items-start gap-2.5 py-1 cursor-pointer group/item">
                  <Checkbox 
                    checked={selectedEvents.includes(event.type)} 
                    onCheckedChange={() => toggleEvent(event.type)}
                    className="mt-0.5"
                  />
                  <div>
                    <span className="text-sm font-mono font-bold text-[var(--text-primary)]">{event.type}</span>
                    <p className="text-xs text-[var(--text-secondary)] leading-relaxed">{event.description}</p>
                  </div>
                </label>
              ))}
            </div>
          </div>
          <div>
            <p className="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-widest mb-2">Step events</p>
            <div className="space-y-1">
              {STEP_EVENTS.map(event => (
                <label key={event.type} className="flex items-start gap-2.5 py-1 cursor-pointer group/item">
                  <Checkbox 
                    checked={selectedEvents.includes(event.type)} 
                    onCheckedChange={() => toggleEvent(event.type)}
                    className="mt-0.5"
                  />
                  <div>
                    <span className="text-sm font-mono font-bold text-[var(--text-primary)]">{event.type}</span>
                    <p className="text-xs text-[var(--text-secondary)] leading-relaxed">{event.description}</p>
                  </div>
                </label>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function CreateWebhookDialog({ open, onOpenChange, url, setUrl, onSave, loading, secret }: any) {
  const [copied, setCopied] = useState(false)
  const [selectedEvents, setSelectedEvents] = useState<string[]>(['*'])

  if (secret) {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="text-display text-2xl">Webhook Secret</DialogTitle>
            <DialogDescription className="text-sm">
              This secret is used to sign Flume events. Store it securely; it will not be shown again.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-6 py-4">
            <div className="relative">
              <div className="p-4 bg-black/5 dark:bg-black/40 rounded-lg font-mono text-[11px] break-all pr-12 text-[var(--text-primary)] border border-[var(--border-subtle)] leading-relaxed">
                {secret}
              </div>
              <Button
                variant="ghost"
                size="icon-sm"
                className="absolute right-2 top-1/2 -translate-y-1/2 text-[var(--text-muted)] hover:text-brand"
                onClick={() => {
                  navigator.clipboard.writeText(secret)
                  setCopied(true)
                  setTimeout(() => setCopied(false), 2000)
                }}
              >
                {copied ? <Check className="h-4 w-4 text-brand" /> : <Copy className="h-4 w-4" />}
              </Button>
            </div>
            
            <div className="flex items-start gap-3 p-4 bg-orange-500/10 border border-orange-500/20 rounded-xl">
              <Info className="h-4 w-4 text-orange-500 shrink-0 mt-0.5" />
              <p className="text-[11px] text-orange-600 dark:text-orange-400 font-semibold leading-relaxed">
                You must verify the <code className="font-mono">X-Signature-256</code> header in every request to ensure it came from Flume.
              </p>
            </div>
            
            <DialogFooter>
              <Button className="w-full" onClick={() => onOpenChange(false)}>I've saved this secret</Button>
            </DialogFooter>
          </div>
        </DialogContent>
      </Dialog>
    )
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="text-display text-2xl">Register Endpoint</DialogTitle>
          <DialogDescription className="text-sm">Add a URL to receive events from the Flume engine.</DialogDescription>
        </DialogHeader>
        <div className="space-y-6 py-4">
          <div className="space-y-2">
            <p className="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-widest px-1">Endpoint URL</p>
            <Input 
              placeholder="https://api.yourdomain.com/webhooks/flume" 
              value={url}
              onChange={e => setUrl(e.target.value)}
              className="bg-[var(--bg-subtle)]"
              autoFocus
            />
          </div>
          
          <div className="p-4 bg-[var(--bg-subtle)] rounded-xl border border-[var(--border-subtle)]">
            <p className="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-widest mb-3">Events</p>
            <EventSelector selectedEvents={selectedEvents} onChange={setSelectedEvents} />
          </div>
        </div>
        <DialogFooter className="gap-2 sm:gap-0">
          <Button variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
          <Button 
            onClick={() => onSave(selectedEvents)} 
            disabled={loading || !url || (!selectedEvents.includes('*') && selectedEvents.length === 0)} 
            className="min-w-[100px]"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Register'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

function EditWebhookDialog({ open, onOpenChange, webhook, onSave, loading }: { 
  open: boolean
  onOpenChange: (open: boolean) => void
  webhook: WebhookSubscription
  onSave: (events: string[]) => void
  loading: boolean
}) {
  const [selectedEvents, setSelectedEvents] = useState<string[]>(webhook.events)

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="text-display text-2xl">Edit Endpoint</DialogTitle>
          <DialogDescription className="text-sm">
            Update event subscriptions for <code className="font-mono text-[var(--text-primary)]">{webhook.url}</code>
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-6 py-4">
          <div className="p-4 bg-[var(--bg-subtle)] rounded-xl border border-[var(--border-subtle)]">
            <p className="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-widest mb-3">Events</p>
            <EventSelector selectedEvents={selectedEvents} onChange={setSelectedEvents} />
          </div>
        </div>
        <DialogFooter className="gap-2 sm:gap-0">
          <Button variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
          <Button 
            onClick={() => onSave(selectedEvents)} 
            disabled={loading || (!selectedEvents.includes('*') && selectedEvents.length === 0)} 
            className="min-w-[100px]"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Save'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
