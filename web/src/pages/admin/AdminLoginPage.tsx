import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { LoaderCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Wordmark } from '@/components/common/Wordmark'
import { useAuthStore } from '@/stores/authStore'
import { adminLogin } from '@/lib/admin'

export function AdminLoginPage() {
  const navigate = useNavigate()
  const { setTokens, setUser } = useAuthStore()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const data = await adminLogin(email, password)
      setTokens(data.access_token, data.refresh_token)
      setUser(data.user)
      navigate('/admin/platforms', { replace: true })
    } catch (err: any) {
      setError(err.message || 'Invalid credentials')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="relative overflow-hidden py-20 sm:py-28 lg:py-32">
      <div className="gradient-hero absolute inset-0 -z-10" />
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-sm">
          <div className="rounded-xl bg-[var(--bg-card)] p-8 border border-[var(--border-subtle)] shadow-sm">
            <div className="text-center mb-8">
              <Wordmark className="mx-auto mb-6" />
              <h1 className="text-display text-3xl text-[var(--text-primary)]">Admin Access</h1>
              <p className="mt-2 text-sm text-[var(--text-secondary)]">Sign in to the admin panel</p>
            </div>

            <form onSubmit={handleSubmit}>
              <Input
                type="email"
                placeholder="admin@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="h-10"
              />
              <Input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="h-10 mt-3"
              />
              <Button type="submit" variant="default" className="w-full mt-3 h-10" disabled={loading}>
                {loading && <LoaderCircle className="h-4 w-4 animate-spin" />}
                {loading ? 'Signing in...' : 'Sign in'}
              </Button>
            </form>

            {error && (
              <p className="mt-4 text-sm text-center text-[var(--destructive)] font-medium">
                {error}
              </p>
            )}
          </div>
          <p className="mt-6 text-center text-xs text-[var(--text-muted)]">
            <a href="/login" className="underline hover:text-[var(--text-secondary)]">Back to regular login</a>
          </p>
        </div>
      </div>
    </section>
  )
}
