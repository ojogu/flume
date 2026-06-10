import { ArrowRight, MessageCircle } from 'lucide-react'
import { Link } from 'react-router-dom'
import { buttonVariants } from '@/components/ui/button'
import { cn } from '@/lib/utils'

export function CTASection() {
  return (
    <section id="api-access" className="relative py-20 sm:py-24">
      <div className="gradient-cta absolute inset-0 -z-10" />

      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-label text-brand mb-4">Get started</p>
          <h2 className="text-display text-3xl sm:text-4xl text-[var(--text-primary)]">
            Start building today.
          </h2>

          <p className="mt-4 text-lg text-[var(--text-secondary)]">
            API-first. Async-native. Built for scale.
          </p>

          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-3">
            <Link
              to="/login"
              className={cn(buttonVariants({ variant: 'default', size: 'lg' }), 'px-6 gap-2')}
            >
              Get API Access
              <ArrowRight className="h-4 w-4" />
            </Link>

            <a
              href="https://t.me/getflume_bot"
              target="_blank"
              rel="noopener noreferrer"
              className={cn(buttonVariants({ variant: 'outline', size: 'lg' }), 'px-6 gap-2')}
            >
              <MessageCircle className="h-4 w-4" />
              Try on Telegram
            </a>
          </div>
        </div>
      </div>
    </section>
  )
}
