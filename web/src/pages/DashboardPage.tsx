import { useNavigate } from 'react-router-dom'
import { Button, buttonVariants } from '@/components/ui/button'
import { Wordmark } from '@/components/common/Wordmark'
import { useAuthStore } from '@/stores/authStore'
import { cn } from '@/lib/utils'

export function DashboardPage() {
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()

  return (
    <section className="relative overflow-hidden py-20 sm:py-28 lg:py-32">
      <div className="gradient-hero absolute inset-0 -z-10" />
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-3xl text-center">
          <Wordmark className="mx-auto mb-8" />
          <h1 className="text-display text-4xl sm:text-5xl text-[var(--text-primary)]">
            Welcome to Flume
          </h1>
          {user ? (
            <p className="mt-4 text-lg text-[var(--text-secondary)]">
              Signed in as{' '}
              <span className="font-semibold text-[var(--text-primary)]">{user.email}</span>
            </p>
          ) : (
            <p className="mt-4 text-lg text-[var(--text-muted)]">
              You're not signed in.
            </p>
          )}

          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-3">
            {user ? (
              <Button
                variant="outline"
                size="lg"
                onClick={() => {
                  logout()
                  navigate('/')
                }}
                className="px-8"
              >
                Sign out
              </Button>
            ) : (
              <a
                href="/login"
                className={cn(buttonVariants({ variant: 'default', size: 'lg' }), 'px-8')}
              >
                Sign in
              </a>
            )}
          </div>
        </div>
      </div>
    </section>
  )
}
