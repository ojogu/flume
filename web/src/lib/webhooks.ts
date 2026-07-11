import { v1ApiClient } from './api'

export interface WebhookSubscription {
  id: string
  url: string
  events: string[]
  is_active: boolean
  created_at: string
  updated_at: string
  secret?: string // Only returned on creation
}

export interface WebhookDelivery {
  id: string
  subscription_id: string
  event_type: string
  payload: any
  status: 'pending' | 'delivered' | 'failed' | 'exhausted'
  response_code: number | null
  response_body: string | null
  attempts: number
  next_retry_at: string | null
  created_at: string
  completed_at: string | null
}

export interface WebhookTestResult {
  success: boolean
  status_code: number | null
  response_body: string
}

/**
 * List all webhook subscriptions for the active API key.
 */
export async function listWebhooks(): Promise<WebhookSubscription[]> {
  return v1ApiClient<WebhookSubscription[]>('/webhooks')
}

/**
 * Create a new webhook subscription.
 */
export async function createWebhook(req: { url: string; events: string[] }): Promise<WebhookSubscription> {
  return v1ApiClient<WebhookSubscription>('/webhooks', {
    method: 'POST',
    body: JSON.stringify(req),
  })
}

/**
 * Update an existing webhook subscription.
 */
export async function updateWebhook(id: string, req: Partial<{ url: string; events: string[]; is_active: boolean }>): Promise<WebhookSubscription> {
  return v1ApiClient<WebhookSubscription>(`/webhooks/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(req),
  })
}

/**
 * Delete a webhook subscription.
 */
export async function deleteWebhook(id: string): Promise<void> {
  // DELETE /v1/webhooks/{id} returns 204 No Content
  await v1ApiClient<void>(`/webhooks/${id}`, {
    method: 'DELETE',
  })
}

/**
 * List delivery attempts for a specific subscription.
 */
export async function listWebhookDeliveries(id: string): Promise<WebhookDelivery[]> {
  return v1ApiClient<WebhookDelivery[]>(`/webhooks/${id}/deliveries`)
}

/**
 * Trigger a synchronous test ping for a webhook.
 */
export async function testWebhook(id: string): Promise<WebhookTestResult> {
  return v1ApiClient<WebhookTestResult>(`/webhooks/${id}/test`, {
    method: 'POST',
  })
}
