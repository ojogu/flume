import { useEffect, useState, type ChangeEvent } from 'react'
import {
  AlertTriangle,
  Check,
  CheckCircle2,
  CircleX,
  Clock3,
  Copy,
  Loader2,
  Pencil,
  Plus,
  RefreshCw,
  Send,
  ShieldCheck,
  Trash2,
  Webhook,
  XCircle,
} from 'lucide-react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'
import { Checkbox } from '@/components/ui/checkbox'
import { Switch } from '@/components/ui/switch'
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from '@/components/ui/accordion'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import {
  listWebhooks,
  createWebhook,
  updateWebhook,
  deleteWebhook,
  testWebhook,
  listWebhookDeliveries,
  WebhookSubscription,
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

const JOB_EVENTS = EVENT_CATALOG.filter((event) => event.group === 'Job events')
const STEP_EVENTS = EVENT_CATALOG.filter((event) => event.group === 'Step events')

type EndpointFormProps = {
  id: string
  url: string
  onChange: (event: ChangeEvent<HTMLInputElement>) => void
}

export function WebhooksPage() {
  const { activeApiKey } = useApiStore()
  const queryClient = useQueryClient()
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [editingWebhook, setEditingWebhook] = useState<WebhookSubscription | null>(null)
  const [deletingWebhook, setDeletingWebhook] = useState<WebhookSubscription | null>(null)
  const [pendingStatusId, setPendingStatusId] = useState<string | null>(null)
  const [url, setUrl] = useState('')
  const [createdSecret, setCreatedSecret] = useState<string | null>(null)

  const { data: webhooks, isLoading, isError, refetch } = useQuery({
    queryKey: ['webhooks', activeApiKey],
    queryFn: () => listWebhooks(activeApiKey || undefined),
  })

  const createMutation = useMutation({
    mutationFn: createWebhook,
    onSuccess: (data) => {
      setCreatedSecret(data.secret || null)
      queryClient.invalidateQueries({ queryKey: ['webhooks'] })
      toast.success('Endpoint added')
    },
    onError: (err: any) => toast.error(err.message || 'Failed to create webhook endpoint'),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, ...req }: { id: string; url?: string; events?: string[] }) => updateWebhook(id, req),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['webhooks'] })
      toast.success('Webhook endpoint updated')
      setShowEditModal(false)
      setEditingWebhook(null)
    },
    onError: (err: any) => toast.error(err.message || 'Failed to update webhook endpoint'),
  })

  const statusMutation = useMutation({
    mutationFn: ({ id, is_active }: { id: string; is_active: boolean }) => updateWebhook(id, { is_active }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['webhooks'] })
      toast.success(variables.is_active ? 'Endpoint enabled' : 'Endpoint disabled')
    },
    onError: (err: any) => toast.error(err.message || 'Failed to update endpoint status'),
    onSettled: () => setPendingStatusId(null),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteWebhook,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['webhooks'] })
      toast.success('Webhook endpoint deleted')
      setDeletingWebhook(null)
    },
    onError: (err: any) => toast.error(err.message || 'Failed to delete webhook endpoint'),
  })

  const handleCreate = (events: string[]) => {
    if (!url || !activeApiKey) return
    createMutation.mutate({ api_key_id: activeApiKey, url, events })
  }

  const handleEdit = (data: { url: string; events: string[] }) => {
    if (!editingWebhook) return
    updateMutation.mutate({ id: editingWebhook.id, url: data.url, events: data.events })
  }

  const handleReset = () => {
    setShowCreateModal(false)
    setUrl('')
    setCreatedSecret(null)
  }

  const handleStatusChange = (webhook: WebhookSubscription, is_active: boolean) => {
    setPendingStatusId(webhook.id)
    statusMutation.mutate({ id: webhook.id, is_active })
  }

  const handleConfirmDelete = () => {
    if (deletingWebhook) deleteMutation.mutate(deletingWebhook.id)
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
        <div className="space-y-2">
          <p className="text-label text-brand">Webhook delivery</p>
          <h1 className="text-display text-4xl text-[var(--text-primary)]">Webhooks</h1>
          <p className="max-w-2xl text-sm leading-relaxed text-[var(--text-secondary)]">
            Deliver Flume events to your systems as jobs move through the pipeline.
          </p>
        </div>
        <Button onClick={() => setShowCreateModal(true)} size="lg" className="gap-2 self-start sm:self-auto" disabled={!activeApiKey}>
          <Plus className="h-4 w-4" />
          Add endpoint
        </Button>
      </div>

      <div className="space-y-4">
        {isLoading ? (
          Array.from({ length: 2 }).map((_, index) => <WebhookCardSkeleton key={index} />)
        ) : isError ? (
          <div className="flex flex-col items-center justify-center rounded-xl border border-destructive/20 bg-destructive/5 px-6 py-12 text-center">
            <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-xl border border-destructive/20 bg-destructive/10">
              <CircleX className="h-5 w-5 text-destructive" aria-hidden="true" />
            </div>
            <p className="font-semibold text-[var(--text-primary)]">Webhook endpoints could not be loaded</p>
            <p className="mt-1 max-w-sm text-sm leading-relaxed text-[var(--text-secondary)]">
              Check your connection and try again. Your existing endpoints are unchanged.
            </p>
            <Button variant="outline" size="sm" className="mt-5 gap-2" onClick={() => refetch()}>
              <RefreshCw className="h-3.5 w-3.5" />
              Try again
            </Button>
          </div>
        ) : webhooks?.length === 0 ? (
          <div className="rounded-xl border border-dashed border-[var(--border-subtle)] bg-[var(--bg-subtle)]/30 px-6 py-12 text-center sm:px-12">
            <div className="mx-auto mb-5 flex h-12 w-12 items-center justify-center rounded-xl bg-[var(--brand-light)]">
              <Webhook className="h-6 w-6 text-brand" aria-hidden="true" />
            </div>
            <h2 className="text-xl font-semibold text-[var(--text-primary)]">
              {activeApiKey ? 'No endpoints configured' : 'Select an API key'}
            </h2>
            <p className="mx-auto mt-2 max-w-md text-sm leading-relaxed text-[var(--text-secondary)]">
              {activeApiKey
                ? 'Register an endpoint to receive job and pipeline updates directly in your system.'
                : 'Select an API key above to view and manage its webhook endpoints.'}
            </p>
            {activeApiKey && (
              <Button className="mt-6 gap-2" onClick={() => setShowCreateModal(true)}>
                <Plus className="h-4 w-4" />
                Add your first endpoint
              </Button>
            )}
          </div>
        ) : (
          webhooks?.map((webhook) => (
            <WebhookCard
              key={webhook.id}
              webhook={webhook}
              isStatusPending={pendingStatusId === webhook.id}
              onToggle={(is_active) => handleStatusChange(webhook, is_active)}
              onDelete={() => setDeletingWebhook(webhook)}
              onEdit={() => {
                setEditingWebhook(webhook)
                setShowEditModal(true)
              }}
            />
          ))
        )}
      </div>

      <CreateWebhookDialog
        open={showCreateModal}
        onOpenChange={(open: boolean) => !open && handleReset()}
        url={url}
        setUrl={setUrl}
        onSave={handleCreate}
        loading={createMutation.isPending}
        secret={createdSecret}
      />

      {editingWebhook && (
        <EditWebhookDialog
          open={showEditModal}
          onOpenChange={(open: boolean) => {
            if (!open) {
              setShowEditModal(false)
              setEditingWebhook(null)
            }
          }}
          webhook={editingWebhook}
          onSave={handleEdit}
          loading={updateMutation.isPending}
        />
      )}

      <AlertDialog open={!!deletingWebhook} onOpenChange={(open) => !open && setDeletingWebhook(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="text-display text-2xl">Delete endpoint?</AlertDialogTitle>
            <AlertDialogDescription>
              This permanently stops deliveries to{' '}
              <code className="break-all font-mono text-[var(--text-primary)]">{deletingWebhook?.url}</code>.
              Delivery history will no longer be available.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={deleteMutation.isPending}>Keep endpoint</AlertDialogCancel>
            <AlertDialogAction onClick={handleConfirmDelete} disabled={deleteMutation.isPending} className="gap-2">
              {deleteMutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
              Delete endpoint
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}

function WebhookCardSkeleton() {
  return (
    <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-5 sm:p-6">
      <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
        <div className="flex min-w-0 flex-1 gap-3">
          <Skeleton className="h-10 w-10 shrink-0 rounded-xl" />
          <div className="min-w-0 flex-1 space-y-3">
            <Skeleton className="h-5 w-3/4 max-w-md" />
            <Skeleton className="h-3.5 w-48" />
            <div className="flex gap-2">
              <Skeleton className="h-6 w-24 rounded-md" />
              <Skeleton className="h-6 w-28 rounded-md" />
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          <Skeleton className="h-9 w-32 rounded-lg" />
          <Skeleton className="h-9 w-9 rounded-lg" />
          <Skeleton className="h-9 w-9 rounded-lg" />
        </div>
      </div>
    </div>
  )
}

function WebhookCard({
  webhook,
  isStatusPending,
  onToggle,
  onDelete,
  onEdit,
}: {
  webhook: WebhookSubscription
  isStatusPending: boolean
  onToggle: (is_active: boolean) => void
  onDelete: () => void
  onEdit: () => void
}) {
  const [testing, setTesting] = useState(false)
  const [testResult, setTestResult] = useState<{ success: boolean; code: number | null; body: string } | null>(null)

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
    <div className="group overflow-hidden rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)]">
      <div className="p-5 sm:p-6">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div className="flex min-w-0 flex-1 gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[var(--brand-light)]">
              <Webhook className="h-5 w-5 text-brand" aria-hidden="true" />
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <code className="min-w-0 max-w-full truncate text-sm font-semibold text-[var(--text-primary)] sm:max-w-xl">
                  {webhook.url}
                </code>
                <Badge variant={webhook.is_active ? 'default' : 'secondary'} className="gap-1.5 px-2 text-xs">
                  <span className={cn('h-1.5 w-1.5 rounded-full', webhook.is_active ? 'bg-primary-foreground/80' : 'bg-[var(--text-muted)]')} />
                  {webhook.is_active ? 'Active' : 'Disabled'}
                </Badge>
              </div>
              <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-[var(--text-muted)]">
                <span>{webhook.api_key_name ? `API key: ${webhook.api_key_name}` : 'API key scope'}</span>
                <span>Added {formatRelativeTime(webhook.created_at)}</span>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2 lg:justify-end">
            <div className="flex min-h-11 items-center gap-2 rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-subtle)] px-3">
              <Switch
                id={`webhook-status-${webhook.id}`}
                checked={webhook.is_active}
                onCheckedChange={onToggle}
                disabled={isStatusPending}
                aria-label={`${webhook.is_active ? 'Disable' : 'Enable'} ${webhook.url}`}
              />
              <Label htmlFor={`webhook-status-${webhook.id}`} className="cursor-pointer text-xs font-medium text-[var(--text-secondary)]">
                {isStatusPending ? 'Updating…' : webhook.is_active ? 'Enabled' : 'Disabled'}
              </Label>
            </div>
            <Button
              variant="outline"
              size="sm"
              className="h-9 gap-2"
              onClick={handleTest}
              disabled={testing}
              aria-busy={testing}
            >
              {testing ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Send className="h-3.5 w-3.5" />}
              {testing ? 'Sending…' : 'Send test event'}
            </Button>
            <Tooltip>
              <TooltipTrigger
                render={
                  <Button variant="ghost" size="icon" className="size-11 text-[var(--text-muted)] hover:bg-[var(--bg-subtle)] hover:text-[var(--text-primary)]" onClick={onEdit} aria-label="Edit endpoint">
                    <Pencil className="h-4 w-4" />
                  </Button>
                }
              />
              <TooltipContent>Edit endpoint</TooltipContent>
            </Tooltip>
            <Tooltip>
              <TooltipTrigger
                render={
                  <Button variant="ghost" size="icon" className="size-11 text-[var(--text-muted)] hover:bg-destructive/10 hover:text-destructive" onClick={onDelete} aria-label="Delete endpoint">
                    <Trash2 className="h-4 w-4" />
                  </Button>
                }
              />
              <TooltipContent>Delete endpoint</TooltipContent>
            </Tooltip>
          </div>
        </div>

        <div className="mt-6 border-t border-[var(--border-subtle)] pt-4">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <p className="text-xs font-semibold text-[var(--text-primary)]">Subscribed events</p>
              <p className="mt-1 text-xs text-[var(--text-muted)]">Choose which pipeline updates this endpoint receives.</p>
            </div>
            <div className="flex flex-wrap gap-1.5 sm:justify-end">
              {webhook.events.includes('*') ? (
                <span className="rounded-md border border-brand/20 bg-[var(--brand-light)] px-2 py-1 font-mono text-xs font-semibold text-brand">
                  All events
                </span>
              ) : webhook.events.length ? (
                webhook.events.map((event) => (
                  <span key={event} className="rounded-md border border-[var(--border-subtle)] bg-[var(--bg-subtle)] px-2 py-1 font-mono text-xs font-semibold text-[var(--text-secondary)]">
                    {event}
                  </span>
                ))
              ) : (
                <span className="text-xs text-[var(--text-muted)]">No events selected</span>
              )}
            </div>
          </div>
        </div>

        {testResult && (
          <div
            className={cn(
              'mt-5 flex gap-3 rounded-lg border p-4',
              testResult.success ? 'border-brand/20 bg-[var(--brand-light)] text-brand' : 'border-destructive/20 bg-destructive/5 text-destructive'
            )}
            role="status"
            aria-live="polite"
          >
            <div className="shrink-0 pt-0.5">
              {testResult.success ? <CheckCircle2 className="h-5 w-5" /> : <XCircle className="h-5 w-5" />}
            </div>
            <div className="min-w-0">
              <p className="text-sm font-semibold">
                {testResult.success ? 'Connection succeeded' : 'Connection failed'}
                <span className="font-normal text-[var(--text-secondary)]"> · HTTP {testResult.code || 'Timeout'}</span>
              </p>
              <p className="mt-1 break-all font-mono text-xs leading-relaxed text-[var(--text-secondary)]">{testResult.body}</p>
            </div>
          </div>
        )}
      </div>

      <Accordion>
        <AccordionItem value="logs" className="border-t border-[var(--border-subtle)]">
          <AccordionTrigger className="h-auto px-5 py-3 text-sm font-medium text-[var(--text-secondary)] hover:bg-[var(--bg-subtle)]/50 hover:text-[var(--text-primary)] hover:no-underline sm:px-6">
            <span className="flex items-center gap-2">
              <Clock3 className="h-4 w-4 text-[var(--text-muted)]" aria-hidden="true" />
              Recent deliveries
            </span>
          </AccordionTrigger>
          <AccordionContent className="px-5 pb-5 pt-2 sm:px-6 sm:pb-6">
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

  if (isLoading) {
    return (
      <div className="space-y-2">
        <Skeleton className="h-16 w-full rounded-lg" />
        <Skeleton className="h-16 w-full rounded-lg" />
      </div>
    )
  }

  if (!logs?.length) {
    return (
      <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-[var(--border-subtle)] px-4 py-8 text-center">
        <Send className="mb-3 h-5 w-5 text-[var(--text-muted)]" aria-hidden="true" />
        <p className="text-sm font-medium text-[var(--text-primary)]">No deliveries yet</p>
        <p className="mt-1 text-xs text-[var(--text-muted)]">Delivery attempts will appear here after the next event.</p>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {logs.map((log) => {
        const isDelivered = log.status === 'delivered'
        const isFailed = log.status === 'failed' || log.status === 'exhausted' || Boolean(log.response_code && log.response_code >= 300)
        const statusVariant = isDelivered ? 'default' : isFailed ? 'destructive' : 'secondary'

        return (
          <div key={log.id} className="grid gap-3 border-b border-[var(--border-subtle)] py-3 first:pt-0 last:border-b-0 last:pb-0 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-center">
            <div className="flex min-w-0 items-start gap-3">
              <span className={cn('mt-1.5 h-2 w-2 shrink-0 rounded-full', isDelivered ? 'bg-brand' : isFailed ? 'bg-destructive' : 'bg-[var(--text-muted)]')} aria-hidden="true" />
              <div className="min-w-0">
                <p className="truncate font-mono text-sm font-semibold text-[var(--text-primary)]">{log.event_type}</p>
                <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-[var(--text-muted)]">
                  <span>{formatRelativeTime(log.created_at)}</span>
                  <span>{log.attempts} {log.attempts === 1 ? 'attempt' : 'attempts'}</span>
                  {log.completed_at && <span>Completed {formatRelativeTime(log.completed_at)}</span>}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-3 pl-5 sm:pl-0">
              <span className={cn('font-mono text-sm font-semibold', isDelivered ? 'text-brand' : isFailed ? 'text-destructive' : 'text-[var(--text-secondary)]')}>
                {log.response_code || '—'}
              </span>
              <Badge variant={statusVariant} className="text-xs capitalize">
                {log.status}
              </Badge>
            </div>
          </div>
        )
      })}
    </div>
  )
}

function EventSelector({ selectedEvents, onChange }: { selectedEvents: string[]; onChange: (events: string[]) => void }) {
  const allEvents = selectedEvents.includes('*')

  const toggleAll = () => onChange(allEvents ? [] : ['*'])

  const toggleEvent = (type: string) => {
    if (allEvents) return
    if (selectedEvents.includes(type)) {
      onChange(selectedEvents.filter((event) => event !== type))
    } else {
      onChange([...selectedEvents, type])
    }
  }

  return (
    <div className="space-y-4">
      <Label htmlFor="all-events" className="cursor-pointer items-start gap-3 rounded-lg px-2 py-2 text-sm text-[var(--text-primary)] hover:bg-[var(--bg-card)]">
        <Checkbox id="all-events" checked={allEvents} onCheckedChange={toggleAll} className="mt-0.5" />
        <span>
          <span className="block font-medium">Receive all events</span>
          <span className="mt-1 block text-xs font-normal leading-relaxed text-[var(--text-secondary)]">Recommended for keeping your integration in sync.</span>
        </span>
      </Label>

      {!allEvents && (
        <div className="space-y-5 pl-1">
          <EventGroup title="Job events" events={JOB_EVENTS} selectedEvents={selectedEvents} onToggle={toggleEvent} />
          <EventGroup title="Step events" events={STEP_EVENTS} selectedEvents={selectedEvents} onToggle={toggleEvent} />
        </div>
      )}
    </div>
  )
}

function EventGroup({
  title,
  events,
  selectedEvents,
  onToggle,
}: {
  title: string
  events: typeof EVENT_CATALOG
  selectedEvents: string[]
  onToggle: (type: string) => void
}) {
  return (
    <div>
      <p className="mb-2 text-xs font-semibold text-[var(--text-secondary)]">{title}</p>
      <div className="space-y-1">
        {events.map((event) => {
          const inputId = `event-${event.type.replace('.', '-')}`
          return (
            <Label key={event.type} htmlFor={inputId} className="cursor-pointer items-start gap-3 rounded-lg px-2 py-2 text-left hover:bg-[var(--bg-card)]">
              <Checkbox id={inputId} checked={selectedEvents.includes(event.type)} onCheckedChange={() => onToggle(event.type)} className="mt-0.5" />
              <span>
                <span className="block font-mono text-sm font-semibold text-[var(--text-primary)]">{event.type}</span>
                <span className="mt-0.5 block text-xs font-normal leading-relaxed text-[var(--text-secondary)]">{event.description}</span>
              </span>
            </Label>
          )
        })}
      </div>
    </div>
  )
}

function EndpointUrlField({ id, url, onChange }: EndpointFormProps) {
  const hintId = `${id}-hint`

  return (
    <div className="space-y-2">
      <Label htmlFor={id} className="text-[var(--text-primary)]">Endpoint URL</Label>
      <p id={hintId} className="text-xs leading-relaxed text-[var(--text-secondary)]">Use an HTTPS URL that can accept POST requests.</p>
      <Input
        id={id}
        aria-describedby={hintId}
        placeholder="https://api.yourdomain.com/webhooks/flume"
        value={url}
        onChange={onChange}
        className="h-10 bg-[var(--bg-subtle)] font-mono text-sm"
        autoFocus
      />
    </div>
  )
}

type CreateWebhookDialogProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  url: string
  setUrl: (url: string) => void
  onSave: (events: string[]) => void
  loading: boolean
  secret: string | null
}

function CreateWebhookDialog({ open, onOpenChange, url, setUrl, onSave, loading, secret }: CreateWebhookDialogProps) {
  const [copied, setCopied] = useState(false)
  const [selectedEvents, setSelectedEvents] = useState<string[]>(['*'])
  const [acknowledged, setAcknowledged] = useState(false)

  useEffect(() => {
    setAcknowledged(false)
    setCopied(false)
  }, [secret])

  useEffect(() => {
    if (open && !secret) setSelectedEvents(['*'])
  }, [open, secret])

  if (secret) {
    return (
      <Dialog
        open={open}
        disablePointerDismissal={!acknowledged}
        onOpenChange={(value: boolean, details: { reason: string }) => {
          if (!acknowledged && (details.reason === 'escapeKey' || details.reason === 'outsidePress')) return
          onOpenChange(value)
        }}
      >
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--brand-light)]">
              <ShieldCheck className="h-5 w-5 text-brand" aria-hidden="true" />
            </div>
            <DialogTitle className="text-display text-2xl">Webhook secret</DialogTitle>
            <DialogDescription>
              This secret signs Flume events. Store it securely; it will not be shown again.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-5 py-2">
            <div className="relative">
              <code className="block rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-subtle)] p-4 pr-14 font-mono text-xs leading-relaxed break-all text-[var(--text-primary)]" aria-label="Webhook signing secret">
                {secret}
              </code>
              <Tooltip>
                <TooltipTrigger
                  render={
                    <Button
                      variant="ghost"
                      size="icon"
                      className="absolute right-2 top-1/2 size-10 -translate-y-1/2 text-[var(--text-muted)] hover:text-brand"
                      onClick={() => {
                        void navigator.clipboard.writeText(secret)
                        setCopied(true)
                        setTimeout(() => setCopied(false), 2000)
                      }}
                      aria-label={copied ? 'Secret copied' : 'Copy secret'}
                    >
                      {copied ? <Check className="h-4 w-4 text-brand" /> : <Copy className="h-4 w-4" />}
                    </Button>
                  }
                />
                <TooltipContent>{copied ? 'Copied' : 'Copy secret'}</TooltipContent>
              </Tooltip>
            </div>

            <div className="flex items-start gap-3 rounded-lg border border-destructive/20 bg-destructive/5 p-4 text-destructive">
              <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
              <p className="text-sm leading-relaxed">
                Once this dialog closes, the secret cannot be recovered. Save it in a secure place before continuing.
              </p>
            </div>

            <Label htmlFor="webhook-secret-ack" className="cursor-pointer items-start gap-3 text-sm leading-relaxed text-[var(--text-secondary)]">
              <Checkbox id="webhook-secret-ack" checked={acknowledged} onCheckedChange={setAcknowledged} className="mt-0.5" />
              I have saved this secret in a secure place
            </Label>

            <DialogFooter>
              <Button className="w-full" disabled={!acknowledged} onClick={() => onOpenChange(false)}>Done</Button>
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
          <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--brand-light)]">
            <Webhook className="h-5 w-5 text-brand" aria-hidden="true" />
          </div>
          <DialogTitle className="text-display text-2xl">Add endpoint</DialogTitle>
          <DialogDescription>Choose where Flume should send event notifications.</DialogDescription>
        </DialogHeader>
        <div className="space-y-6 py-2">
          <EndpointUrlField id="create-endpoint-url" url={url} onChange={(event) => setUrl(event.target.value)} />
          <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-subtle)] p-4">
            <div className="mb-3">
              <p className="font-semibold text-[var(--text-primary)]">Event scope</p>
              <p className="mt-1 text-xs leading-relaxed text-[var(--text-secondary)]">Select all events or subscribe to a specific set.</p>
            </div>
            <EventSelector selectedEvents={selectedEvents} onChange={setSelectedEvents} />
          </div>
        </div>
        <DialogFooter className="gap-2 sm:gap-0">
          <Button variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
          <Button
            onClick={() => onSave(selectedEvents)}
            disabled={loading || !url || (!selectedEvents.includes('*') && selectedEvents.length === 0)}
            className="min-w-[128px] gap-2"
          >
            {loading && <Loader2 className="h-4 w-4 animate-spin" />}
            Add endpoint
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

function EditWebhookDialog({
  open,
  onOpenChange,
  webhook,
  onSave,
  loading,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  webhook: WebhookSubscription
  onSave: (data: { url: string; events: string[] }) => void
  loading: boolean
}) {
  const [selectedEvents, setSelectedEvents] = useState<string[]>(webhook.events)
  const [url, setUrl] = useState(webhook.url)

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--brand-light)]">
            <Pencil className="h-5 w-5 text-brand" aria-hidden="true" />
          </div>
          <DialogTitle className="text-display text-2xl">Edit endpoint</DialogTitle>
          <DialogDescription>Update the destination URL or event subscriptions.</DialogDescription>
        </DialogHeader>
        <div className="space-y-6 py-2">
          <EndpointUrlField id="edit-endpoint-url" url={url} onChange={(event) => setUrl(event.target.value)} />
          <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-subtle)] p-4">
            <div className="mb-3">
              <p className="font-semibold text-[var(--text-primary)]">Event scope</p>
              <p className="mt-1 text-xs leading-relaxed text-[var(--text-secondary)]">Select all events or subscribe to a specific set.</p>
            </div>
            <EventSelector selectedEvents={selectedEvents} onChange={setSelectedEvents} />
          </div>
        </div>
        <DialogFooter className="gap-2 sm:gap-0">
          <Button variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
          <Button
            onClick={() => onSave({ url, events: selectedEvents })}
            disabled={loading || !url || (!selectedEvents.includes('*') && selectedEvents.length === 0)}
            className="min-w-[128px] gap-2"
          >
            {loading && <Loader2 className="h-4 w-4 animate-spin" />}
            Save changes
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
