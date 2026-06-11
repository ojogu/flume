export type JobStatus = 'pending' | 'processing' | 'completed' | 'failed'
export type JobStepStatus = 'pending' | 'running' | 'completed' | 'failed'

export interface JobStep {
  id: string
  name: string
  status: JobStepStatus
  started_at: string | null  // ISO
  completed_at: string | null // ISO
  error?: {
    message: string
    stderr: string
  }
}

export interface Job {
  id: string
  status: JobStatus
  operation: string
  created_at: string  // ISO
  duration_ms: number | null
  steps: JobStep[]
}

const MOCK_JOBS: Job[] = [
  {
    id: 'job_4k2n8z9p1m',
    status: 'completed',
    operation: 'Video Compression',
    created_at: new Date(Date.now() - 3600000).toISOString(), // 1h ago
    duration_ms: 45200,
    steps: [
      { id: '1', name: 'Download source', status: 'completed', started_at: '2026-06-11T21:00:00Z', completed_at: '2026-06-11T21:00:10Z' },
      { id: '2', name: 'FFmpeg processing', status: 'completed', started_at: '2026-06-11T21:00:10Z', completed_at: '2026-06-11T21:00:40Z' },
      { id: '3', name: 'Upload result', status: 'completed', started_at: '2026-06-11T21:00:40Z', completed_at: '2026-06-11T21:00:45Z' },
    ]
  },
  {
    id: 'job_7x1v3q5r8w',
    status: 'failed',
    operation: 'Audio Extraction',
    created_at: new Date(Date.now() - 1800000).toISOString(), // 30m ago
    duration_ms: 12000,
    steps: [
      { id: '1', name: 'Download source', status: 'completed', started_at: '2026-06-11T21:30:00Z', completed_at: '2026-06-11T21:30:10Z' },
      { id: '2', name: 'Format analysis', status: 'failed', started_at: '2026-06-11T21:30:10Z', completed_at: '2026-06-11T21:30:12Z', error: {
        message: 'Invalid media container',
        stderr: 'ffprobe version 6.0 Copyright (c) 2007-2023 the FFmpeg developers\n[mov,mp4,m4a,3gp,3g2,mj2 @ 0x559e8f6f8c00] moov atom not found\n/tmp/input.mp4: Invalid data found when processing input'
      }},
    ]
  },
  {
    id: 'job_1z9x2c3v4b',
    status: 'processing',
    operation: 'Thumbnail Generation',
    created_at: new Date(Date.now() - 300000).toISOString(), // 5m ago
    duration_ms: null,
    steps: [
      { id: '1', name: 'Download source', status: 'completed', started_at: '2026-06-11T21:55:00Z', completed_at: '2026-06-11T21:55:05Z' },
      { id: '2', name: 'Scene detection', status: 'running', started_at: '2026-06-11T21:55:05Z', completed_at: null },
      { id: '3', name: 'Frame capture', status: 'pending', started_at: null, completed_at: null },
    ]
  }
]

export async function getJobs(): Promise<Job[]> {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 600))
  return MOCK_JOBS
}

export async function getJob(id: string): Promise<Job | null> {
  await new Promise(resolve => setTimeout(resolve, 400))
  return MOCK_JOBS.find(j => j.id === id) || null
}
