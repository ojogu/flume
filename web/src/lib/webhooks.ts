import { apiClient } from './api'

export interface WebhookSubscription {
  id: string
  api_key_id: string
  api_key_name?: string | null
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
 * List all webhook subscriptions for the user, optionally filtered by API key.
 */
export async function listWebhooks(api_key_id?: string): Promise<WebhookSubscription[]> {
  const query = api_key_id ? `?api_key_id=${api_key_id}` : ''
  const res = await apiClient<{ status: string; data: WebhookSubscription[] }>(`/webhooks${query}`)
  return res.data
}

/**
 * Create a new webhook subscription on a specific API key.
 */
export async function createWebhook(req: {
  api_key_id: string
  url: string
  events: string[]
}): Promise<WebhookSubscription> {
  const res = await apiClient<{ status: string; data: WebhookSubscription }>('/webhooks', {
    method: 'POST',
    body: JSON.stringify(req),
  })
  return res.data
}

/**
 * Update an existing webhook subscription.
 */
export async function updateWebhook(
  id: string,
  req: Partial<{ url: string; events: string[]; is_active: boolean }>
): Promise<WebhookSubscription> {
  const res = await apiClient<{ status: string; data: WebhookSubscription }>(`/webhooks/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(req),
  })
  return res.data
}

/**
 * Delete a webhook subscription.
 */
export async function deleteWebhook(id: string): Promise<void> {
  await apiClient<void>(`/webhooks/${id}`, {
    method: 'DELETE',
  })
}

/**
 * List delivery attempts for a specific subscription.
 */
export async function listWebhookDeliveries(id: string): Promise<WebhookDelivery[]> {
  const res = await apiClient<{ status: string; data: WebhookDelivery[] }>(`/webhooks/${id}/deliveries`)
  return res.data
}

/**
 * Trigger a synchronous test ping for a webhook.
 */
export async function testWebhook(id: string): Promise<WebhookTestResult> {
  const res = await apiClient<{ status: string; data: WebhookTestResult }>(`/webhooks/${id}/test`, {
    method: 'POST',
  })
  return res.data
}
