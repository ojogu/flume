import { useRouteError } from 'react-router-dom'
import { RefreshCw, Mail } from 'lucide-react'
import { cn } from '@/lib/utils'
import { buttonVariants, Button } from '@/components/ui/button'
import { Wordmark } from '@/components/common/Wordmark'

export function ErrorPage() {
  const error = useRouteError()
  console.error('Caught by ErrorPage:', error)

  return (
    <div className="min-h-screen flex flex-col">
      <main className="relative overflow-hidden flex-1 grid place-items-center px-4 py-20">
        <div className="gradient-hero absolute inset-0 -z-10" />
        <div className="text-center">
          <Wordmark className="mx-auto mb-14 h-8 w-auto" />

          <p className="text-display text-[8rem] sm:text-[12rem] leading-none text-[var(--brand-mid)] select-none">
            500
          </p>

          <p className="text-label text-brand mb-3 mt-8">Error 500</p>

          <h1 className="text-display text-3xl sm:text-4xl text-[var(--text-primary)] mb-4">
            Something went wrong
          </h1>

          <p className="text-lg text-[var(--text-secondary)] leading-relaxed max-w-md mx-auto mb-10">
            There's a blockage in the pipeline. Try again?
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <Button
              variant="default"
              size="lg"
              className="px-6 gap-2"
              onClick={() => window.location.reload()}
            >
              <RefreshCw className="h-4 w-4" />
              Try again
            </Button>
            <a
              href="mailto:support@flume.ai"
              className={cn(buttonVariants({ variant: 'outline', size: 'lg' }), 'px-6 gap-2')}
            >
              <Mail className="h-4 w-4" />
              Contact support
            </a>
          </div>
        </div>
      </main>
    </div>
  )
}
