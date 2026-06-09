import { useState } from 'react'
import { LoaderCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Wordmark } from '@/components/common/Wordmark'

function GoogleIcon({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
        fill="#4285F4"
      />
      <path
        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-1 .67-2.28 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
        fill="#34A853"
      />
      <path
        d="M5.84 14.09c-.22-.67-.35-1.39-.35-2.09s.13-1.42.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"
        fill="#FBBC05"
      />
      <path
        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
        fill="#EA4335"
      />
    </svg>
  )
}

export function LoginPage() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [sent, setSent] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [googleLoading, setGoogleLoading] = useState(false)

  const handleGoogleLogin = async () => {
    setGoogleLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/v1/auth/login')
      const body = await response.json()
      if (body.data?.url) {
        window.location.href = body.data.url
        return
      }
      setError('Failed to start Google sign in. Please try again.')
    } catch {
      setError('Failed to connect to the server. Please check your connection.')
    } finally {
      setGoogleLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setSent(false)

    try {
      const response = await fetch(`/api/v1/auth/magic-link?email=${encodeURIComponent(email)}`)
      
      if (response.ok) {
        setSent(true)
      } else {
        const data = await response.json()
        setError(data.message || 'Something went wrong. Please try again.')
      }
    } catch (err) {
      setError('Failed to connect to the server. Please check your connection.')
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
            {/* Wordmark + heading */}
            <div className="text-center mb-8">
              <Wordmark className="mx-auto mb-6" />
              <h1 className="text-display text-3xl text-[var(--text-primary)]">Welcome back</h1>
              <p className="mt-2 text-sm text-[var(--text-secondary)]">Sign in to your account</p>
            </div>

            {/* Google OAuth button */}
            <Button
              variant="outline"
              className="w-full justify-center gap-3"
              onClick={handleGoogleLogin}
              disabled={googleLoading}
            >
              {googleLoading ? (
                <LoaderCircle className="h-5 w-5 animate-spin" />
              ) : (
                <GoogleIcon className="h-5 w-5" />
              )}
              Continue with Google
            </Button>

            {/* Divider */}
            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t border-[var(--border-subtle)]" />
              </div>
              <div className="relative flex justify-center text-xs">
                <span className="bg-[var(--bg-card)] px-2 text-[var(--text-muted)]">
                  or continue with email
                </span>
              </div>
            </div>

            {/* Magic link form */}
            <form onSubmit={handleSubmit}>
              <Input
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="h-10"
              />
              <Button type="submit" variant="default" className="w-full mt-3 h-10" disabled={loading}>
                {loading && <LoaderCircle className="h-4 w-4 animate-spin" />}
                {loading ? 'Sending...' : 'Send magic link'}
              </Button>
            </form>

            {/* Success state */}
            {sent && (
              <p className="mt-4 text-sm text-center text-brand font-medium">
                ✓ Check your inbox for the magic link
              </p>
            )}

            {/* Error state */}
            {error && (
              <p className="mt-4 text-sm text-center text-[var(--destructive)] font-medium">
                {error}
              </p>
            )}
          </div>
          <p className="mt-6 text-center text-xs text-[var(--text-muted)]">
            No password needed. Magic links expire in 15 minutes.
          </p>
        </div>
      </div>
    </section>
  )
}
