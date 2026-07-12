import { Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'

export function DashboardNotFoundPage() {
  return (
    <div className="flex flex-col items-center justify-center py-24 text-center">
      <p className="text-display text-[6rem] leading-none text-[var(--brand-mid)] select-none mb-4">
        404
      </p>
      <p className="text-label text-brand mb-2">Error 404</p>
      <h1 className="text-display text-2xl text-[var(--text-primary)] mb-2">
        Page not found
      </h1>
      <p className="text-sm text-[var(--text-secondary)] max-w-sm mb-8">
        Nothing flowing at this address.
      </p>
      <Link to="/dashboard/jobs">
        <Button variant="default" size="sm" className="gap-2">
          <ArrowLeft className="h-3.5 w-3.5" />
          Back to Jobs
        </Button>
      </Link>
    </div>
  )
}
