import { apiClient } from './api'

export type JobStatus = 'pending' | 'processing' | 'succeeded' | 'partial_success' | 'failed' | 'dead' | 'cancelled'

export type JobStepStatus = 'pending' | 'running' | 'complete' | 'completed' | 'failed'

export interface JobStep {
  id: string
  job_id: string
  step_index: number
  operation: string
  input_artifact: any
  output_artifact: any
  output_url?: string | null
  error: string | null
  status: JobStepStatus
  started_at: string | null
  completed_at: string | null
  created_at: string
  updated_at: string
}

export interface Job {
  id: string
  api_key_id: string
  api_key_name?: string | null
  status: JobStatus
  source_uri: string
  source_type: string
  origin: string
  pipeline_steps: any[]
  outputs: any[]
  selection: any
  source_metadata: any
  error: string | null
  parent_job_id: string | null
  playlist_entry_index: number | null
  retry_count: number
  max_retries: number
  completed_at: string | null
  created_at: string
  updated_at: string
  steps?: JobStep[] // steps only in detail view
  // playlist parents only: totals for their child jobs (absent/null for normal jobs)
  child_count?: number | null
  children_done?: number | null
  children_failed?: number | null
}

/** A playlist parent is a folder: it has child jobs and no file of its own. */
export function isPlaylistParent(
  job: Pick<Job, 'child_count' | 'source_metadata'>,
): boolean {
  return (job.child_count ?? 0) > 0 || Boolean(job.source_metadata?.playlist)
}

type SourceMeta = Record<string, unknown> | null | undefined

/** Preview image for a job: the saved thumbnail, else the YouTube still for older rows. */
export function getSourceThumbnail(meta: SourceMeta): string | null {
  if (!meta || typeof meta !== 'object') return null
  const source = meta.source as Record<string, unknown> | undefined
  const thumbnail = source?.thumbnail as string | undefined
  if (thumbnail) return thumbnail
  const platform = source?.platform as string | undefined
  const videoId = source?.video_id as string | undefined
  if (platform === 'youtube' && videoId) {
    return `https://i.ytimg.com/vi/${videoId}/mqdefault.jpg`
  }
  return null
}

export function getSourceTitle(meta: SourceMeta): string | null {
  if (!meta || typeof meta !== 'object') return null
  const source = meta.source as Record<string, unknown> | undefined
  return (source?.title as string) || null
}

export interface JobsResponse {
  total: number
  page: number
  per_page: number
  jobs: Job[]
}

export interface GetJobsParams {
  status?: string
  origin?: string
  created_after?: string
  api_key_id?: string
  page?: number
  per_page?: number
  /** Hide playlist children; they are listed inside their parent folder. */
  top_level?: boolean
}

/**
 * Fetch jobs using the internal JWT-authenticated API.
 * Returns all jobs across the user's API keys, with optional filters.
 */
export async function getJobs(params: GetJobsParams = {}): Promise<JobsResponse> {
  const query = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      query.set(key, value.toString())
    }
  })

  const queryString = query.toString()
  const res = await apiClient<{ status: string; data: JobsResponse }>(`/jobs${queryString ? `?${queryString}` : ''}`)
  return res.data
}

/**
 * Fetch a single job by ID using the internal JWT-authenticated API.
 */
export async function getJob(id: string): Promise<Job> {
  const res = await apiClient<{ status: string; data: Job }>(`/jobs/${id}`)
  return res.data
}

/**
 * Fetch the videos inside a playlist job, in playlist order.
 */
export async function getJobChildren(
  id: string,
  page = 1,
  perPage = 20,
): Promise<JobsResponse> {
  const res = await apiClient<{ status: string; data: JobsResponse }>(
    `/jobs/${id}/children?page=${page}&per_page=${perPage}`,
  )
  return res.data
}

export async function retryJob(id: string): Promise<Job> {
  const res = await apiClient<{ status: string; data: Job }>(
    `/jobs/${id}/status`,
    { method: 'PATCH', body: JSON.stringify({ action: 'retry' }) }
  )
  return res.data
}

/**
 * Cancel a pending or processing job (a playlist's unfinished videos are cancelled with it).
 * Cancelling a job that already finished returns it unchanged.
 */
export async function cancelJob(id: string): Promise<Job> {
  const res = await apiClient<{ status: string; data: Job }>(
    `/jobs/${id}/status`,
    { method: 'PATCH', body: JSON.stringify({ action: 'cancel' }) }
  )
  return res.data
}

export type JobCounts = Record<JobStatus, number>

export async function getJobCounts(apiKeyId?: string): Promise<JobCounts> {
  const query = apiKeyId ? `?api_key_id=${apiKeyId}` : ''
  const res = await apiClient<{ status: string; data: JobCounts }>(`/jobs/counts${query}`)
  return res.data
}
