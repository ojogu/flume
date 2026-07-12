import { apiClient } from './api'

export type JobStatus = 'pending' | 'processing' | 'succeeded' | 'partial_success' | 'failed'

export type JobStepStatus = 'pending' | 'running' | 'completed' | 'failed'

export interface JobStep {
  id: string
  job_id: string
  step_index: number
  operation: string
  input_artifact: any
  output_artifact: any
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
  pipeline_steps: any[]
  outputs: any[]
  selection: any
  source_metadata: any
  error: string | null
  parent_job_id: string | null
  playlist_entry_index: number | null
  completed_at: string | null
  created_at: string
  updated_at: string
  steps?: JobStep[] // steps only in detail view
}

export interface JobsResponse {
  total: number
  page: number
  per_page: number
  jobs: Job[]
}

export interface GetJobsParams {
  status?: string
  created_after?: string
  api_key_id?: string
  page?: number
  per_page?: number
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
