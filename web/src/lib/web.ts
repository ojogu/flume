import { API_BASE } from '@/lib/config'
import { apiClient } from '@/lib/api'

const V1_BASE = API_BASE.replace('/internal', '/v1')

export const MONTHLY_LIMIT_ANONYMOUS = 5
export const MONTHLY_LIMIT_AUTHENTICATED = 20

export interface CreateJobPayload {
  source: {
    type: 'video' | 'audio'
    uri: string
    format?: string
  }
  pipeline: Array<{
    operation: string
    params: Record<string, unknown>
  }>
  outputs?: Array<{
    type: string
    params?: Record<string, unknown>
  }>
}

export interface JobResponse {
  id: string
  status: string
  source_uri: string | null
  source_type: string
  origin: string
  pipeline_steps: unknown[] | null
  error: string | null
  created_at: string | null
  source_metadata?: Record<string, unknown> | null
}

export interface JobDetailResponse extends JobResponse {
  steps: Array<{
    id: string
    step_index: number
    operation: string
    status: string
    error: string | null
    started_at: string | null
    completed_at: string | null
  }>
  source_metadata: Record<string, unknown> | null
  completed_at: string | null
}

export class ApiError extends Error {
  statusCode: number
  errorCode?: string

  constructor(message: string, statusCode: number, errorCode?: string) {
    super(message)
    this.name = 'ApiError'
    this.statusCode = statusCode
    this.errorCode = errorCode
  }
}

async function v1Fetch<T>(
  endpoint: string,
  apiKey: string,
  options: RequestInit = {},
): Promise<T> {
  const res = await fetch(`${V1_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': apiKey,
      ...options.headers,
    },
  })

  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new ApiError(
      body?.message ?? `Request failed (${res.status})`,
      res.status,
      body?.error_code,
    )
  }

  const body = await res.json()
  return body.data ?? body
}

export async function submitJob(apiKey: string, payload: CreateJobPayload): Promise<JobResponse> {
  return v1Fetch<JobResponse>('/job', apiKey, {
    method: 'POST',
    body: JSON.stringify(payload),
    headers: { 'X-Flume-Origin': 'web' },
  })
}

export async function submitJobAuth(payload: CreateJobPayload): Promise<JobResponse> {
  const res = await apiClient<{ status: string; data: JobResponse }>('/jobs', {
    method: 'POST',
    body: JSON.stringify(payload),
    headers: { 'X-Flume-Origin': 'web' },
  })
  return res.data
}

export async function getJob(apiKey: string, jobId: string): Promise<JobDetailResponse> {
  return v1Fetch<JobDetailResponse>(`/job/${jobId}`, apiKey)
}

export async function getDownloadUrl(apiKey: string, jobId: string): Promise<string> {
  const res = await v1Fetch<{ url: string }>(`/job/${jobId}/download?redirect=false`, apiKey)
  return res.url
}

export async function presignUpload(
  apiKey: string,
  filename: string,
  contentType: string,
  fileSize: number,
): Promise<{ upload_id: string; presigned_url: string; object_key: string; expires_at: string }> {
  return v1Fetch('/uploads/presign', apiKey, {
    method: 'POST',
    body: JSON.stringify({
      original_filename: filename,
      content_type: contentType,
      file_size: fileSize,
    }),
  })
}

export async function completeUpload(apiKey: string, uploadId: string): Promise<unknown> {
  return v1Fetch(`/uploads/${uploadId}/complete`, apiKey, {
    method: 'POST',
  })
}

export async function uploadFile(
  apiKey: string,
  file: File,
  onProgress?: (pct: number) => void,
): Promise<string> {
  const { upload_id, presigned_url } = await presignUpload(
    apiKey,
    file.name,
    file.type,
    file.size,
  )

  await new Promise<void>((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    xhr.open('PUT', presigned_url)
    xhr.setRequestHeader('Content-Type', file.type)
    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable && onProgress) {
        onProgress(Math.round((e.loaded / e.total) * 100))
      }
    }
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve()
      } else {
        reject(new Error(`Upload failed (HTTP ${xhr.status})`))
      }
    }
    xhr.onerror = () => reject(new Error('Upload blocked — network error or CORS rejection'))
    xhr.send(file)
  })

  await completeUpload(apiKey, upload_id)
  return `uploads/${upload_id}`
}
