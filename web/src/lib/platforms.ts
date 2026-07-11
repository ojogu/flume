import { apiClient } from './api'

export interface Platform {
  id: string
  slug: string           // unique identifier, e.g. "youtube"
  name: string           // display name, e.g. "YouTube"
  url: string            // base URL, e.g. "https://youtube.com"
  is_active: boolean     // whether the platform is enabled
  content_types: string[] // ["single", "playlist", "vod"]
  requires_login: boolean // does this platform need auth?
  supports_live: boolean  // can handle live streams?
  description: string | null
  limitations: string | null
  logo_url: string | null
  sort_order: number
  created_at: string | null
  updated_at: string | null
}

export interface CreatePlatformRequest {
  slug: string
  name: string
  url: string
  is_active?: boolean           // default true
  content_types?: string[]      // default ["single"]
  requires_login?: boolean      // default false
  supports_live?: boolean       // default false
  description?: string | null
  limitations?: string | null
  logo_url?: string | null
  sort_order?: number           // default 0
}

export type UpdatePlatformRequest = Partial<CreatePlatformRequest>

export interface PlatformListResponse {
  platforms: Platform[]
  total: number
}

/**
 * Fetch media platforms from the internal API.
 */
export async function getPlatforms(activeOnly: boolean = false): Promise<PlatformListResponse> {
  const endpoint = activeOnly ? '/platforms?active_only=true' : '/platforms'
  const res = await apiClient<{ status: string; data: PlatformListResponse }>(endpoint)
  return res.data
}

/**
 * Create a new supported media platform.
 */
export async function createPlatform(data: CreatePlatformRequest): Promise<Platform> {
  const res = await apiClient<{ status: string; data: Platform }>('/platforms', {
    method: 'POST',
    body: JSON.stringify(data),
  })
  return res.data
}

/**
 * Update configuration for an existing platform.
 */
export async function updatePlatform(id: string, data: UpdatePlatformRequest): Promise<Platform> {
  const res = await apiClient<{ status: string; data: Platform }>(`/platforms/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  })
  return res.data
}

/**
 * Permanently remove a platform from the catalog.
 */
export async function deletePlatform(id: string): Promise<void> {
  await apiClient<{ status: string; message: string }>(`/platforms/${id}`, {
    method: 'DELETE',
  })
}
