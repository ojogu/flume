import { ArrowRight, BookOpen } from 'lucide-react'
import { buttonVariants } from '@/components/ui/button'
import { cn } from '@/lib/utils'

export function HeroSection() {
  return (
    <section className="relative overflow-hidden py-20 sm:py-28 lg:py-32">
      <div className="gradient-hero absolute inset-0 -z-10" />

      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-3xl text-center">
          <p className="text-label text-brand mb-4">Video Processing API</p>

          <h1 className="text-display text-4xl sm:text-5xl lg:text-[3.75rem] text-[var(--text-primary)]">
            Video processing infrastructure for developers.
          </h1>

          <p className="mt-6 text-lg text-[var(--text-secondary)] leading-relaxed">
            Send a link or file. Get a processed result. No FFmpeg setup, no infra headaches — just an API that works.
          </p>

          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-3">
            <a
              href="#api-access"
              className={cn(buttonVariants({ variant: 'default', size: 'lg' }), 'px-6 gap-2')}
            >
              Start Building
              <ArrowRight className="h-4 w-4" />
            </a>

            <a
              href="#docs"
              className={cn(buttonVariants({ variant: 'outline', size: 'lg' }), 'px-6 gap-2')}
            >
              <BookOpen className="h-4 w-4" />
              View Docs
            </a>
          </div>

          <p className="mt-8 text-sm text-[var(--text-muted)]">
            Also available on{' '}
            <a href="/bot" className="text-brand hover:underline underline-offset-4">Flume Bot</a>
            ,{' '}
            <a href="https://t.me/getflume_bot" target="_blank" rel="noopener noreferrer" className="text-brand hover:underline underline-offset-4">Telegram</a>
            , and{' '}
            <a href="https://wa.me/000000000" target="_blank" rel="noopener noreferrer" className="text-brand hover:underline underline-offset-4">WhatsApp</a>
            {/* DUMMY LINK: replace with real WhatsApp number before launch */}
            {' '}— no setup required.
          </p>
        </div>
      </div>
    </section>
  )
}
