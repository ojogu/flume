import type { JobStatus, JobStepStatus } from '@/lib/jobs'
import { formatDuration } from '@/lib/utils'

export function formatJobStatus(status: JobStatus) {
  switch (status) {
    case 'partial_success':
      return 'Partial success'
    default:
      return status.charAt(0).toUpperCase() + status.slice(1)
  }
}

export function formatStepStatus(status: JobStepStatus) {
  if (status === 'complete' || status === 'completed') return 'Complete'
  return status.charAt(0).toUpperCase() + status.slice(1)
}

export function isCompletedStepStatus(status: JobStepStatus) {
  return status === 'complete' || status === 'completed'
}

export function formatSourceType(value: string) {
  const sentence = value.replace(/[_-]+/g, ' ').toLowerCase()
  return sentence.charAt(0).toUpperCase() + sentence.slice(1)
}

export function formatOperation(value: string) {
  return formatSourceType(value)
}

export function formatAbsoluteTime(value: string) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value

  return date.toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  })
}

export function formatUTCTime(value: string) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value

  return date.toLocaleTimeString('en-US', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    timeZone: 'UTC',
  }) + ' UTC'
}

export function formatStepDuration(startedAt: string | null, completedAt: string | null) {
  if (!startedAt || !completedAt) return null

  return formatDuration(new Date(completedAt).getTime() - new Date(startedAt).getTime())
}
