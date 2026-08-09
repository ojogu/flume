import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import {
  ChevronLeft,
  ChevronRight,
  Clock3,
  Loader2,
  Send,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  getWebhook,
  listWebhookDeliveries,
  testWebhook,
  updateWebhook,
  WebhookDelivery,
  WebhookSubscription,
} from '@/lib/webhooks'
import { formatRelativeTime, cn } from '@/lib/utils'

const PAGE_SIZE = 20

export function WebhookDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [page, setPage] = useState(0)
  const [pendingStatusId, setPendingStatusId] = useState<string | null>(null)
  const [expandedDeliveryId, setExpandedDeliveryId] = useState<string | null>(null)

  const queryClient = useQueryClient()

  const { data: webhook, isLoading: webhookLoading, error: webhookError } = useQuery({
    queryKey: ['webhook', id],
    queryFn: () => getWebhook(id!),
    enabled: !!id,
  })

  const { data: deliveriesData, isLoading: deliveriesLoading, refetch: refetchDeliveries } = useQuery({
    queryKey: ['webhook-deliveries', id, page],
    queryFn: () => listWebhookDeliveries(id!, { limit: PAGE_SIZE, offset: page * PAGE_SIZE }),
    enabled: !!id,
  })

  const statusMutation = useMutation({
    mutationFn: ({ id, is_active }: { id: string; is_active: boolean }) => updateWebhook(id, { is_active }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['webhook', id] })
      toast.success(variables.is_active ? 'Endpoint enabled' : 'Endpoint disabled')
    },
    onError: (err: any) => toast.error(err.message || 'Failed to update endpoint status'),
    onSettled: () => setPendingStatusId(null),
  })

  const testMutation = useMutation({
    mutationFn: (webhookId: string) => testWebhook(webhookId),
    onSuccess: (result) => {
      toast.success(result.success ? 'Test event sent' : 'Test event failed')
      refetchDeliveries()
    },
    onError: (err: any) => toast.error(err.message || 'Failed to send test event'),
  })

  const handleStatusChange = (webhook: WebhookSubscription, is_active: boolean) => {
    setPendingStatusId(webhook.id)
    statusMutation.mutate({ id: webhook.id, is_active })
  }

  const totalPages = deliveriesData ? Math.ceil(deliveriesData.total / PAGE_SIZE) : 0

  if (webhookLoading) {
    return (
      <div className="max-w-4xl space-y-8 animate-pulse">
        <div className="flex items-center gap-4">
          <Skeleton className="h-5 w-24" />
        </div>
        <div className="space-y-4">
          <Skeleton className="h-10 w-64" />
          <Skeleton className="h-5 w-48" />
        </div>
        <div className="space-y-6 pt-8">
          <Skeleton className="h-16 w-full rounded-xl" />
          <Skeleton className="h-64 w-full rounded-xl" />
        </div>
      </div>
    )
  }

  if (webhookError || !webhook) {
    return (
      <div className="max-w-4xl text-center py-20">
        <h2 className="text-display text-2xl text-[var(--text-primary)]">Webhook not found</h2>
        <p className="mt-2 text-[var(--text-secondary)]">
          This webhook may have been deleted or you do not have access to it.
        </p>
        <Link
          to="/dashboard/webhooks"
          className="mt-6 inline-flex items-center gap-1.5 text-sm font-medium text-brand hover:underline"
        >
          <ChevronLeft className="h-4 w-4" />
          Back to webhooks
        </Link>
      </div>
    )
  }

  return (
    <div className="max-w-4xl space-y-8">
      <div className="space-y-4">
        <Link
          to="/dashboard/webhooks"
          className="inline-flex items-center gap-1.5 text-sm font-medium text-[var(--text-secondary)] hover:text-brand transition-colors"
        >
          <ChevronLeft className="h-4 w-4" />
          Back to webhooks
        </Link>

        <div className="flex flex-wrap items-start justify-between gap-6">
          <div className="space-y-1">
            <div className="flex flex-wrap items-center gap-3">
              <code className="max-w-full truncate text-xl font-semibold text-[var(--text-primary)] sm:max-w-xl font-mono">
                {webhook.url}
              </code>
              <Badge
                variant={webhook.is_active ? 'default' : 'secondary'}
                className="gap-1.5 px-2 text-xs"
              >
                <span
                  className={cn(
                    'h-1.5 w-1.5 rounded-full',
                    webhook.is_active ? 'bg-primary-foreground/80' : 'bg-[var(--text-muted)]'
                  )}
                />
                {webhook.is_active ? 'Active' : 'Disabled'}
              </Badge>
            </div>
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-[var(--text-muted)]">
              <span>{webhook.api_key_name ? `API key: ${webhook.api_key_name}` : 'API key scope'}</span>
              <span>Added {formatRelativeTime(webhook.created_at)}</span>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <div className="flex h-11 items-center gap-2 rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-subtle)] px-3">
              <Switch
                id={`webhook-status-${webhook.id}`}
                checked={webhook.is_active}
                onCheckedChange={(checked) => handleStatusChange(webhook, checked)}
                disabled={pendingStatusId === webhook.id || statusMutation.isPending}
                aria-label={`${webhook.is_active ? 'Disable' : 'Enable'} endpoint`}
              />
              <Label
                htmlFor={`webhook-status-${webhook.id}`}
                className="cursor-pointer text-xs font-medium text-[var(--text-secondary)]"
              >
                {pendingStatusId === webhook.id || statusMutation.isPending
                  ? 'Updating…'
                  : webhook.is_active
                    ? 'Enabled'
                    : 'Disabled'}
              </Label>
            </div>
            <Button
              variant="outline"
              size="sm"
              className="h-9 gap-2"
              onClick={() => testMutation.mutate(webhook.id)}
              disabled={testMutation.isPending}
              aria-busy={testMutation.isPending}
            >
              {testMutation.isPending ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <Send className="h-3.5 w-3.5" />
              )}
              {testMutation.isPending ? 'Sending…' : 'Send test event'}
            </Button>
          </div>
        </div>
      </div>

      <Separator className="bg-[var(--border-subtle)]" />

      <section>
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h2 className="text-base font-semibold text-[var(--text-primary)]">Subscribed events</h2>
            <p className="mt-1 text-sm text-[var(--text-muted)]">
              Pipeline updates this endpoint receives.
            </p>
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          {webhook.events.includes('*') ? (
            <span className="rounded-md border border-brand/20 bg-[var(--brand-light)] px-3 py-1.5 font-mono text-sm font-semibold text-brand">
              All events
            </span>
          ) : webhook.events.length ? (
            webhook.events.map((event) => (
              <span
                key={event}
                className="rounded-md border border-[var(--border-subtle)] bg-[var(--bg-subtle)] px-3 py-1.5 font-mono text-sm font-semibold text-[var(--text-secondary)]"
              >
                {event}
              </span>
            ))
          ) : (
            <span className="text-sm text-[var(--text-muted)]">No events selected</span>
          )}
        </div>
      </section>

      <Separator className="bg-[var(--border-subtle)]" />

      <section>
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h2 className="text-base font-semibold text-[var(--text-primary)]">Delivery history</h2>
            <p className="mt-1 text-sm text-[var(--text-muted)]">
              {deliveriesData
                ? `${deliveriesData.total} total delivery${deliveriesData.total === 1 ? '' : 's'}`
                : 'Recent delivery attempts.'}
            </p>
          </div>
          {deliveriesLoading && <Loader2 className="h-4 w-4 animate-spin text-[var(--text-muted)]" />}
        </div>

        {deliveriesData?.data.length === 0 ? (
          <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-[var(--border-subtle)] px-4 py-12 text-center">
            <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--brand-light)]">
              <Send className="h-5 w-5 text-brand" aria-hidden="true" />
            </div>
            <p className="text-sm font-medium text-[var(--text-primary)]">No deliveries yet</p>
            <p className="mt-1 text-xs text-[var(--text-muted)]">
              Delivery attempts will appear here after the next event.
            </p>
          </div>
        ) : (
          <>
            <div className="overflow-hidden rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)]">
              <Table>
                <TableHeader>
                  <TableRow className="hover:bg-transparent">
                    <TableHead className="w-[40%]">Event</TableHead>
                    <TableHead className="w-[15%]">Status</TableHead>
                    <TableHead className="w-[15%]">Response</TableHead>
                    <TableHead className="w-[20%]">Time</TableHead>
                    <TableHead className="w-[10%]"></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {deliveriesData?.data.map((delivery) => (
                    <DeliveryRow
                      key={delivery.id}
                      delivery={delivery}
                      isExpanded={expandedDeliveryId === delivery.id}
                      onToggle={() =>
                        setExpandedDeliveryId((prev) =>
                          prev === delivery.id ? null : delivery.id
                        )
                      }
                    />
                  ))}
                </TableBody>
              </Table>
            </div>

            {expandedDeliveryId && (
              <DeliveryDetails
                delivery={deliveriesData!.data.find((d) => d.id === expandedDeliveryId)!}
              />
            )}

            {totalPages > 1 && (
              <div className="mt-4 flex items-center justify-between">
                <p className="text-sm text-[var(--text-muted)]">
                  Page {page + 1} of {totalPages}
                </p>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setPage((p) => Math.max(0, p - 1))
                      setExpandedDeliveryId(null)
                    }}
                    disabled={page === 0}
                  >
                    <ChevronLeft className="h-4 w-4" />
                    Previous
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setPage((p) => p + 1)
                      setExpandedDeliveryId(null)
                    }}
                    disabled={page >= totalPages - 1}
                  >
                    Next
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            )}
          </>
        )}
      </section>
    </div>
  )
}

function DeliveryRow({
  delivery,
  isExpanded,
  onToggle,
}: {
  delivery: WebhookDelivery
  isExpanded: boolean
  onToggle: () => void
}) {
  const isDelivered = delivery.status === 'delivered'
  const isFailed =
    delivery.status === 'failed' ||
    delivery.status === 'exhausted' ||
    Boolean(delivery.response_code && delivery.response_code >= 300)
  const statusVariant = isDelivered ? 'default' : isFailed ? 'destructive' : 'secondary'

  return (
    <>
      <TableRow className="cursor-pointer hover:bg-[var(--bg-subtle)]/50" onClick={onToggle}>
        <TableCell className="font-mono text-sm font-semibold text-[var(--text-primary)]">
          {delivery.event_type}
        </TableCell>
        <TableCell>
          <Badge variant={statusVariant} className="text-xs capitalize">
            {delivery.status}
          </Badge>
        </TableCell>
        <TableCell>
          <span
            className={cn(
              'font-mono text-sm font-semibold',
              isDelivered
                ? 'text-brand'
                : isFailed
                  ? 'text-destructive'
                  : 'text-[var(--text-secondary)]'
            )}
          >
            {delivery.response_code || '—'}
          </span>
        </TableCell>
        <TableCell>
          <div className="flex items-center gap-1.5 text-sm text-[var(--text-muted)]">
            <Clock3 className="h-3.5 w-3.5" aria-hidden="true" />
            {formatRelativeTime(delivery.created_at)}
          </div>
        </TableCell>
        <TableCell>
          <div className="flex items-center justify-center">
            <ChevronRight
              className={cn(
                'h-4 w-4 text-[var(--text-muted)] transition-transform duration-200',
                isExpanded && 'rotate-90'
              )}
            />
          </div>
        </TableCell>
      </TableRow>
    </>
  )
}

function DeliveryDetails({ delivery }: { delivery: WebhookDelivery }) {
  return (
    <div className="mt-2 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-subtle)] p-4">
      <div className="space-y-4">
        <div>
          <p className="mb-2 text-xs font-semibold text-[var(--text-primary)]">Payload</p>
          <pre className="max-h-64 overflow-auto rounded-lg bg-[var(--bg-card)] p-4 text-xs font-mono leading-relaxed text-[var(--text-secondary)]">
            {JSON.stringify(delivery.payload, null, 2)}
          </pre>
        </div>
        {delivery.response_body && (
          <div>
            <p className="mb-2 text-xs font-semibold text-[var(--text-primary)]">Response body</p>
            <pre className="max-h-32 overflow-auto rounded-lg bg-[var(--bg-card)] p-4 text-xs font-mono leading-relaxed text-[var(--text-secondary)]">
              {delivery.response_body}
            </pre>
          </div>
        )}
        <div className="flex flex-wrap gap-x-6 gap-y-2 text-xs text-[var(--text-muted)]">
          <span>
            <span className="font-medium text-[var(--text-secondary)]">{delivery.attempts}</span>{' '}
            {delivery.attempts === 1 ? 'attempt' : 'attempts'}
          </span>
          {delivery.next_retry_at && (
            <span>
              Next retry:{' '}
              <span className="font-medium text-[var(--text-secondary)]">
                {formatRelativeTime(delivery.next_retry_at)}
              </span>
            </span>
          )}
          {delivery.completed_at && (
            <span>
              Completed:{' '}
              <span className="font-medium text-[var(--text-secondary)]">
                {formatRelativeTime(delivery.completed_at)}
              </span>
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
