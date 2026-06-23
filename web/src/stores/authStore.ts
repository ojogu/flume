import { create } from 'zustand'
import { API_BASE } from '@/lib/config'

export interface User {
  id: string
  email: string
  name: string | null
  picture: string | null
  onboarded: boolean
}

interface AuthState {
  accessToken: string | null
  refreshToken: string | null
  user: User | null
  setTokens: (access: string, refresh: string) => void
  setUser: (user: User) => void
  logout: () => void
  hydrate: () => Promise<void>
}

function loadFromStorage() {
  const accessToken = localStorage.getItem('accessToken')
  const refreshToken = localStorage.getItem('refreshToken')
  const raw = localStorage.getItem('user')
  const user = raw ? (JSON.parse(raw) as User) : null
  return { accessToken, refreshToken, user }
}

export const useAuthStore = create<AuthState>((set, get) => ({
  ...loadFromStorage(),

  setTokens: (accessToken: string, refreshToken: string) => {
    localStorage.setItem('accessToken', accessToken)
    localStorage.setItem('refreshToken', refreshToken)
    set({ accessToken, refreshToken })
  },

  setUser: (user: User) => {
    localStorage.setItem('user', JSON.stringify(user))
    set({ user })
  },

  logout: () => {
    const { refreshToken } = get()
    if (refreshToken) {
      fetch(`${API_BASE}/auth/logout`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${refreshToken}` },
      }).catch(() => {})
    }
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('user')
    set({ accessToken: null, refreshToken: null, user: null })
  },

  hydrate: async () => {
    const { accessToken, refreshToken, user } = loadFromStorage()
    set({ accessToken, refreshToken, user })

    if (!accessToken) return

    const tryFetchUser = async (token: string) => {
      const res = await fetch(`${API_BASE}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) return null
      const body = await res.json()
      if (body.status === 'success' && body.data) return body.data as User
      return null
    }

    let userData = await tryFetchUser(accessToken)

    if (!userData && refreshToken) {
      const refreshRes = await fetch(`${API_BASE}/auth/refresh-token`, {
        headers: { Authorization: `Bearer ${refreshToken}` },
      })
      if (refreshRes.ok) {
        const body = await refreshRes.json()
        if (body.status === 'success' && body.data) {
          get().setTokens(body.data.access_token, body.data.refresh_token)
          userData = await tryFetchUser(body.data.access_token)
        }
      }
    }

    if (userData) {
      get().setUser(userData)
    } else if (!user) {
      get().logout()
    }
  },
}))
