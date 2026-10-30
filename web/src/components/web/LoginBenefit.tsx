import { Link } from 'react-router-dom'
import { History, LogIn } from 'lucide-react'
import { buttonVariants } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { MONTHLY_LIMIT_ANONYMOUS, MONTHLY_LIMIT_AUTHENTICATED } from '@/lib/web'

export function LoginBenefit() {
  return (
    <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-6 space-y-4">
      <div className="flex items-start gap-3">
        <div className="mt-0.5 rounded-lg bg-[var(--bg-subtle)] p-2">
          <History className="h-5 w-5 text-brand" />
        </div>
        <div className="space-y-1">
          <h2 className="font-semibold text-[var(--text-primary)]">See all you've processed</h2>
          <p className="text-sm text-[var(--text-secondary)]">
            Your job history is saved — come back anytime to re-queue, re-download, or pick up
            in-progress work.
          </p>
        </div>
      </div>

      <ul className="space-y-1.5 text-sm text-[var(--text-secondary)]">
        <li className="flex gap-2">
          <span className="text-brand">•</span>
          <span>
            {MONTHLY_LIMIT_AUTHENTICATED} jobs a month instead of {MONTHLY_LIMIT_ANONYMOUS}
          </span>
        </li>
        <li className="flex gap-2">
          <span className="text-brand">•</span>
          <span>Started on your phone? Finish on your laptop</span>
        </li>
      </ul>

      <Link
        to="/login?returnTo=/web"
        className={cn(buttonVariants({ variant: 'default', size: 'sm' }), 'gap-2')}
      >
        <LogIn className="h-3.5 w-3.5" />
        Sign in
      </Link>
    </div>
  )
}
