import { apiClient } from '@/lib/api'

export type ApiKeyStatus = 'active' | 'revoked'

export interface ApiKey {
  id: string           // UUID
  name: string
  key_prefix: string   // e.g. "flm_a1b2c3d4"
  status: ApiKeyStatus
  expires_at: string | null   // ISO timestamp
  last_used_at: string | null // ISO timestamp
  created_at: string | null   // ISO timestamp
}

export interface ApiKeyCreated extends ApiKey {
  full_key: string    // shown ONCE — never re-fetchable
}

export interface ApiKeyListResponse {
  keys: ApiKey[]
  total: number
}

export interface CreateApiKeyRequest {
  name: string
  expires_at?: string | null  // ISO timestamp
}

// All endpoints are under /internal/keys (JWT-protected on backend)
export async function listApiKeys(): Promise<ApiKeyListResponse> {
  const res = await apiClient<{ status: string; data: ApiKeyListResponse }>('/keys')
  return res.data
}

export async function createApiKey(req: CreateApiKeyRequest): Promise<ApiKeyCreated> {
  const res = await apiClient<{ status: string; data: ApiKeyCreated; message: string }>('/keys', {
    method: 'POST',
    body: JSON.stringify(req),
  })
  return res.data
}

export async function revokeApiKey(id: string): Promise<ApiKey> {
  const res = await apiClient<{ status: string; data: ApiKey; message: string }>(`/keys/${id}`, {
    method: 'DELETE',
  })
  return res.data
}
