import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Menu, Sun, Moon, LogIn } from 'lucide-react'
import { Button, buttonVariants } from '@/components/ui/button'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'
import { Wordmark } from './Wordmark'
import { useTheme } from '@/hooks/useTheme'
import { useAuthStore } from '@/stores/authStore'
import { cn } from '@/lib/utils'

const navLinks = [
  { href: '/api', label: 'API', internal: true },
  { href: '/bot', label: 'Bot', internal: true },
  { href: '/pricing', label: 'Pricing', internal: true },
  { href: '#docs', label: 'Docs', internal: false },
]

export function Navbar() {
  const { resolvedTheme, toggleTheme } = useTheme()
  const [mobileOpen, setMobileOpen] = useState(false)
  const { accessToken, user, logout, hydrate } = useAuthStore()
  const isAuthenticated = !!accessToken

  useEffect(() => {
    hydrate()
  }, [hydrate])

  return (
    <header className="sticky top-0 z-50 w-full border-b border-[var(--border-subtle)] bg-[var(--bg)]/80 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">

        {/* Logo */}
        <Link to="/" className="flex items-center gap-2 shrink-0">
          <Wordmark variant={resolvedTheme} />
        </Link>

        {/* Desktop nav */}
        <nav className="hidden md:flex items-center gap-8">
          {navLinks.map((link) =>
            link.internal ? (
              <Link
                key={link.href}
                to={link.href}
                className="text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
              >
                {link.label}
              </Link>
            ) : (
              <a
                key={link.href}
                href={link.href}
                className="text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
              >
                {link.label}
              </a>
            )
          )}
        </nav>

        {/* Actions */}
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleTheme}
            aria-label={resolvedTheme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {resolvedTheme === 'dark' ? (
              <Sun className="h-4 w-4" />
            ) : (
              <Moon className="h-4 w-4" />
            )}
          </Button>

          {isAuthenticated ? (
            <div className="hidden md:flex items-center gap-3">
              {user?.picture ? (
                <img
                  src={user.picture}
                  alt={user.name ?? ''}
                  className="h-8 w-8 rounded-full"
                />
              ) : (
                <div className="h-8 w-8 rounded-full bg-[var(--brand-light)] flex items-center justify-center">
                  <span className="text-xs font-semibold text-brand">
                    {user?.name?.charAt(0) ?? '?'}
                  </span>
                </div>
              )}
              <button
                onClick={logout}
                className={cn(buttonVariants({ variant: 'ghost', size: 'sm' }), 'text-[var(--text-secondary)]')}
              >
                Sign out
              </button>
            </div>
          ) : (
            <Link
              to="/login"
              className={cn(
                buttonVariants({ variant: 'default', size: 'default' }),
                'hidden md:inline-flex px-4 gap-2'
              )}
            >
              <LogIn className="h-4 w-4" />
              Sign in
            </Link>
          )}

          {/* Mobile menu */}
          <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
            <SheetTrigger
              render={
                <Button
                  variant="ghost"
                  size="icon"
                  className="md:hidden"
                  aria-label="Open navigation menu"
                />
              }
            >
              <Menu className="h-5 w-5" />
            </SheetTrigger>
            <SheetContent side="right" className="w-72">
              <div className="flex flex-col gap-1 mt-8">
                <div className="mb-4 px-2">
                  <Wordmark variant={resolvedTheme} className="h-7" />
                </div>
                {navLinks.map((link) =>
                  link.internal ? (
                    <Link
                      key={link.href}
                      to={link.href}
                      onClick={() => setMobileOpen(false)}
                      className="rounded-lg px-3 py-2.5 text-base font-medium text-[var(--text-primary)] hover:bg-[var(--bg-subtle)] transition-colors"
                    >
                      {link.label}
                    </Link>
                  ) : (
                    <a
                      key={link.href}
                      href={link.href}
                      onClick={() => setMobileOpen(false)}
                      className="rounded-lg px-3 py-2.5 text-base font-medium text-[var(--text-primary)] hover:bg-[var(--bg-subtle)] transition-colors"
                    >
                      {link.label}
                    </a>
                  )
                )}
                <div className="mt-4 px-1 flex flex-col gap-2">
                  {isAuthenticated ? (
                    <button
                      onClick={() => { logout(); setMobileOpen(false) }}
                      className={cn(buttonVariants({ variant: 'outline' }), 'w-full justify-center px-4')}
                    >
                      Sign out
                    </button>
                  ) : (
                    <Link
                      to="/login"
                      onClick={() => setMobileOpen(false)}
                      className={cn(buttonVariants({ variant: 'default' }), 'w-full justify-center px-4 gap-2')}
                    >
                      <LogIn className="h-4 w-4" />
                      Sign in
                    </Link>
                  )}
                </div>
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  )
}
