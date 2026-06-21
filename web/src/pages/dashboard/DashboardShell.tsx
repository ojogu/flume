import { useEffect } from 'react'
import { Link, Outlet, useNavigate, useLocation } from 'react-router-dom'
import { Activity, BookOpen, Key, LogOut, Menu, User as UserIcon } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'
import { Wordmark } from '@/components/common/Wordmark'
import { useAuthStore } from '@/stores/authStore'
import { cn } from '@/lib/utils'

const DASHBOARD_NAV = [
  { href: '/dashboard/jobs', label: 'Jobs', icon: Activity, internal: true },
  { href: '/dashboard/keys', label: 'API Keys', icon: Key, internal: true },
  { href: '/docs', label: 'Docs', icon: BookOpen, internal: false },
]

export function DashboardShell() {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout, accessToken, hydrate } = useAuthStore()

  useEffect(() => {
    hydrate()
  }, [hydrate])

  useEffect(() => {
    if (!accessToken) {
      navigate('/login', { replace: true })
    }
  }, [accessToken, navigate])

  if (!accessToken) return null

  const NavItems = ({ className, onItemClick }: { className?: string, onItemClick?: () => void }) => (
    <nav className={cn("flex flex-col gap-1", className)}>
      {DASHBOARD_NAV.map((item) => {
        const Icon = item.icon
        const isActive = location.pathname.startsWith(item.href)
        const linkClass = cn(
          "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
          isActive 
            ? "bg-brand/10 text-brand" 
            : "text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-subtle)]"
        )
        return item.internal ? (
          <Link
            key={item.href}
            to={item.href}
            onClick={onItemClick}
            className={linkClass}
          >
            <Icon className="h-4 w-4" />
            {item.label}
          </Link>
        ) : (
          <a
            key={item.href}
            href={item.href}
            onClick={onItemClick}
            className={linkClass}
          >
            <Icon className="h-4 w-4" />
            {item.label}
          </a>
        )
      })}
    </nav>
  )

  return (
    <div className="flex min-h-screen bg-[var(--background)]">
      {/* Desktop Sidebar */}
      <aside className="hidden md:flex flex-col w-64 border-r border-[var(--border-subtle)] bg-[var(--bg-card)] sticky top-0 h-screen">
        <div className="p-6">
          <Link to="/">
            <Wordmark className="h-7" />
          </Link>
        </div>

        <div className="flex-1 px-4">
          <p className="text-label text-[var(--text-muted)] mb-4 px-2 tracking-widest">Development</p>
          <NavItems />
        </div>

        <div className="p-4 border-t border-[var(--border-subtle)]">
          <div className="flex items-center gap-3 px-2 mb-4">
            <div className="h-8 w-8 rounded-full bg-[var(--brand-light)] flex items-center justify-center shrink-0">
              <UserIcon className="h-4 w-4 text-brand" />
            </div>
            <div className="min-w-0">
              <p className="text-sm font-medium text-[var(--text-primary)] truncate">
                {user?.email ?? 'Developer'}
              </p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            className="w-full justify-start gap-3 text-[var(--text-secondary)] hover:text-destructive hover:bg-destructive/10"
            onClick={() => {
              logout()
              navigate('/')
            }}
          >
            <LogOut className="h-4 w-4" />
            Sign out
          </Button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile Header */}
        <header className="md:hidden flex h-16 items-center justify-between px-4 border-b border-[var(--border-subtle)] bg-[var(--bg-card)] sticky top-0 z-40">
          <Link to="/">
            <Wordmark className="h-6" />
          </Link>
          
          <Sheet>
            <SheetTrigger render={
              <Button variant="ghost" size="icon">
                <Menu className="h-5 w-5" />
              </Button>
            }>
            </SheetTrigger>
            <SheetContent side="left" className="w-64 p-0">
              <div className="flex flex-col h-full bg-[var(--bg-card)]">
                <div className="p-6">
                  <Wordmark className="h-7" />
                </div>
                <div className="flex-1 px-4">
                  <p className="text-label text-[var(--text-muted)] mb-4 px-2 tracking-widest">Development</p>
                  <NavItems onItemClick={() => {}} />
                </div>
                <div className="p-4 border-t border-[var(--border-subtle)]">
                   <Button
                    variant="ghost"
                    size="sm"
                    className="w-full justify-start gap-3 text-[var(--text-secondary)]"
                    onClick={() => {
                      logout()
                      navigate('/')
                    }}
                  >
                    <LogOut className="h-4 w-4" />
                    Sign out
                  </Button>
                </div>
              </div>
            </SheetContent>
          </Sheet>
        </header>

        <main className="flex-1 p-4 sm:p-6 lg:p-8">
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
