import { useAuthStore } from '@/stores/authStore'

const BASE_URL = '/internal'

interface ApiError {
  status: string
  message: string
  error_code?: string
}

class ApiClientError extends Error {
  statusCode: number
  errorCode?: string

  constructor(message: string, statusCode: number, errorCode?: string) {
    super(message)
    this.name = 'ApiClientError'
    this.statusCode = statusCode
    this.errorCode = errorCode
  }
}

async function refreshTokens(): Promise<{ access_token: string; refresh_token: string } | null> {
  const store = useAuthStore.getState()
  const refreshToken = store.refreshToken
  if (!refreshToken) return null

  const res = await fetch(`${BASE_URL}/auth/refresh-token`, {
    headers: { Authorization: `Bearer ${refreshToken}` },
  })

  if (!res.ok) return null

  const body = await res.json()
  if (body.status !== 'success' || !body.data) return null

  store.setTokens(body.data.access_token, body.data.refresh_token)
  return body.data
}

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T> {
  const store = useAuthStore.getState()
  const headers = new Headers(options.headers)

  if (store.accessToken) {
    headers.set('Authorization', `Bearer ${store.accessToken}`)
  }

  if (!headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  let res = await fetch(`${BASE_URL}${endpoint}`, { ...options, headers })

  if (res.status === 401 && store.refreshToken) {
    const tokens = await refreshTokens()
    if (tokens) {
      headers.set('Authorization', `Bearer ${tokens.access_token}`)
      res = await fetch(`${BASE_URL}${endpoint}`, { ...options, headers })
    } else {
      store.logout()
      window.location.href = '/'
      throw new ApiClientError('Session expired', 401, 'session_expired')
    }
  }

  if (!res.ok) {
    let errorData: ApiError
    try {
      errorData = (await res.json()) as ApiError
    } catch {
      errorData = { status: 'error', message: res.statusText }
    }
    throw new ApiClientError(errorData.message, res.status, errorData.error_code)
  }

  return res.json() as Promise<T>
}
