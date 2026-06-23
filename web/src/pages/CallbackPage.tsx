import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { LoaderCircle } from 'lucide-react'
import { useAuthStore } from '@/stores/authStore'
import { buttonVariants } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { API_BASE } from '@/lib/config'

export function CallbackPage() {
  const navigate = useNavigate()
  const { setTokens, setUser } = useAuthStore()
  const [status, setStatus] = useState<'loading' | 'error'>('loading')

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const accessToken = params.get('access-token')
    const refreshToken = params.get('refresh-token')
    const error = params.get('error')
    const onboarded = params.get('onboarded')

    if (error || !accessToken || !refreshToken) {
      setStatus('error')
      return
    }

    setTokens(accessToken, refreshToken)

    fetch(`${API_BASE}/auth/me`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    })
      .then((res) => res.json())
      .then((body) => {
        if (body.status === 'success' && body.data) {
          setUser(body.data)
        } else {
          setUser({
            id: '',
            email: JSON.parse(atob(accessToken.split('.')[1])).user.email,
            name: null,
            picture: null,
            onboarded: onboarded === 'true',
          })
        }
      })
      .catch(() => {
        setUser({
          id: '',
          email: JSON.parse(atob(accessToken.split('.')[1])).user.email,
          name: null,
          picture: null,
          onboarded: onboarded === 'true',
        })
      })
      .finally(() => {
        window.history.replaceState({}, '', '/callback')
        navigate('/dashboard', { replace: true })
      })
  }, [navigate, setTokens, setUser])

  if (status === 'error') {
    return (
      <section className="relative overflow-hidden py-20 sm:py-28 lg:py-32">
        <div className="gradient-hero absolute inset-0 -z-10" />
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-3xl text-center">
            <p className="text-label text-brand mb-3">Authentication</p>
            <h2 className="text-display text-3xl sm:text-4xl text-[var(--text-primary)]">
              Sign in failed
            </h2>
            <p className="mt-4 text-lg text-[var(--text-secondary)]">
              We couldn't complete the sign in. Please try again.
            </p>
            <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3">
              <a
                href="/login"
                className={cn(buttonVariants({ variant: 'default' }), 'px-6')}
              >
                Try again
              </a>
            </div>
          </div>
        </div>
      </section>
    )
  }

  return (
    <section className="relative overflow-hidden py-20 sm:py-28 lg:py-32">
      <div className="gradient-hero absolute inset-0 -z-10" />
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-3xl text-center">
          <LoaderCircle className="h-8 w-8 text-brand animate-spin mx-auto mb-6" />
          <p className="text-lg text-[var(--text-secondary)]">Completing sign in…</p>
        </div>
      </div>
    </section>
  )
}
