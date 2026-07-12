import { API_BASE } from '@/lib/config'

export interface AdminLoginResponse {
  access_token: string
  refresh_token: string
  user: {
    id: string
    email: string
    name: string | null
    picture: string | null
    onboarded: boolean
    is_admin: boolean
  }
}

export async function adminLogin(email: string, password: string): Promise<AdminLoginResponse> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  const body = await res.json()
  if (body.status !== 'success' || !body.data) {
    throw new Error(body.message || 'Invalid credentials')
  }
  return body.data
}
