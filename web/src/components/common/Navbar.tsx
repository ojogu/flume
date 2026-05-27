import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Menu, Sun, Moon } from 'lucide-react'
import { Button, buttonVariants } from '@/components/ui/button'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'
import { Wordmark } from './Wordmark'
import { useTheme } from '@/hooks/useTheme'
import { cn } from '@/lib/utils'

const navLinks = [
  { href: '/api', label: 'API', internal: true },
  { href: '/bot', label: 'Bot', internal: true },
  { href: '#pricing', label: 'Pricing', internal: false },
  { href: '#docs', label: 'Docs', internal: false },
]

export function Navbar() {
  const { resolvedTheme, toggleTheme } = useTheme()
  const [mobileOpen, setMobileOpen] = useState(false)

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

          <a
            href="#api-access"
            className={cn(
              buttonVariants({ variant: 'default', size: 'default' }),
              'hidden md:inline-flex px-4'
            )}
          >
            Get API Access
          </a>

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
                <div className="mt-4 px-1">
                  <a
                    href="#api-access"
                    onClick={() => setMobileOpen(false)}
                    className={cn(buttonVariants({ variant: 'default' }), 'w-full justify-center px-4')}
                  >
                    Get API Access
                  </a>
                </div>
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  )
}
