import { useRouteError, Link } from 'react-router-dom'
import { RefreshCw, ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'

export function DashboardErrorPage() {
  const error = useRouteError()
  console.error('Dashboard error:', error)

  return (
    <div className="flex flex-col items-center justify-center py-24 text-center">
      <p className="text-display text-[6rem] leading-none text-[var(--brand-mid)] select-none mb-4">
        500
      </p>
      <p className="text-label text-brand mb-2">Error 500</p>
      <h1 className="text-display text-2xl text-[var(--text-primary)] mb-2">
        Something went wrong
      </h1>
      <p className="text-sm text-[var(--text-secondary)] max-w-sm mb-8">
        There's a blockage in the pipeline. Try again or head back to Jobs.
      </p>
      <div className="flex items-center gap-3">
        <Button
          variant="default"
          size="sm"
          className="gap-2"
          onClick={() => window.location.reload()}
        >
          <RefreshCw className="h-3.5 w-3.5" />
          Try again
        </Button>
        <Link to="/dashboard/jobs">
          <Button variant="outline" size="sm" className="gap-2">
            <ArrowLeft className="h-3.5 w-3.5" />
            Back to Jobs
          </Button>
        </Link>
      </div>
    </div>
  )
}
