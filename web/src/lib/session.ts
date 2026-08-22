import { API_BASE } from '@/lib/config'

const V1_BASE = API_BASE.replace('/internal', '/v1')

const STORAGE_KEY = 'flume_web_session'

export interface SessionData {
  apiKey: string
  expiresAt: string
  jobsRemaining: number
}

export async function createSession(): Promise<SessionData> {
  const res = await fetch(`${V1_BASE}/web/session`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  })

  if (!res.ok) {
    throw new Error('Failed to create session')
  }

  const body = await res.json()
  const data: SessionData = {
    apiKey: body.data.api_key,
    expiresAt: body.data.expires_at,
    jobsRemaining: body.data.jobs_remaining,
  }

  localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
  return data
}

export async function refreshSession(apiKey: string): Promise<SessionData | null> {
  try {
    const res = await fetch(`${V1_BASE}/web/session`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': apiKey,
      },
    })
    if (!res.ok) return null
    const body = await res.json()
    const data: SessionData = {
      apiKey: body.data.api_key,
      expiresAt: body.data.expires_at,
      jobsRemaining: body.data.jobs_remaining,
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
    return data
  } catch {
    return null
  }
}

export function getSession(): SessionData | null {
  const raw = localStorage.getItem(STORAGE_KEY)
  if (!raw) return null

  try {
    const data: SessionData = JSON.parse(raw)
    if (new Date(data.expiresAt) < new Date()) {
      localStorage.removeItem(STORAGE_KEY)
      return null
    }
    return data
  } catch {
    localStorage.removeItem(STORAGE_KEY)
    return null
  }
}

export function clearSession(): void {
  localStorage.removeItem(STORAGE_KEY)
}

export async function getOrCreateSession(): Promise<SessionData> {
  const existing = getSession()
  if (existing) {
    const refreshed = await refreshSession(existing.apiKey)
    if (refreshed) return refreshed
    // If refresh failed (key expired/revoked), fall through to create.
    // Re-check localStorage hasn't already been cleared by refresh path.
    const stillValid = getSession()
    if (stillValid) return stillValid
  }
  return createSession()
}
