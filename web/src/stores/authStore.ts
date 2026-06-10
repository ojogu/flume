import { create } from 'zustand'

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
  hydrate: () => void
}

export const useAuthStore = create<AuthState>((set, get) => ({
  accessToken: null,
  refreshToken: null,
  user: null,

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
      fetch('/api/v1/auth/logout', {
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
    const accessToken = localStorage.getItem('accessToken')
    const refreshToken = localStorage.getItem('refreshToken')
    const raw = localStorage.getItem('user')
    const user = raw ? (JSON.parse(raw) as User) : null
    set({ accessToken, refreshToken, user })

    if (accessToken && !user) {
      try {
        const res = await fetch('/api/v1/auth/me', {
          headers: { Authorization: `Bearer ${accessToken}` },
        })
        const body = await res.json()
        if (body.status === 'success' && body.data) {
          get().setUser(body.data)
        }
      } catch {}
    }
  },
}))
