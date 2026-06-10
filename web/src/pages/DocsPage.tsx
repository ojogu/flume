import { Link } from 'react-router-dom'
import { ArrowRight, BookOpen } from 'lucide-react'
import { buttonVariants } from '@/components/ui/button'
import { Navbar } from '@/components/common/Navbar'
import { Footer } from '@/components/common/Footer'
import { cn } from '@/lib/utils'

export function DocsPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1">
        <section className="relative overflow-hidden py-20 sm:py-28 lg:py-32">
          <div className="gradient-hero absolute inset-0 -z-10" />

          <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
            <div className="mx-auto max-w-3xl text-center">
              <p className="text-label text-brand mb-4">Documentation</p>

              <h1 className="text-display text-4xl sm:text-5xl lg:text-[3.75rem] text-[var(--text-primary)]">
                API Reference
              </h1>

              <p className="mt-6 text-lg text-[var(--text-secondary)] leading-relaxed">
                Everything you need to integrate Flume's video processing API into your application.
              </p>

              <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-3">
                <Link
                  to="/dashboard"
                  className={cn(buttonVariants({ variant: 'default', size: 'lg' }), 'px-6 gap-2')}
                >
                  Get API Access
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </div>
            </div>
          </div>
        </section>

        <section className="py-20 sm:py-24">
          <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
            <div className="mx-auto max-w-2xl text-center">
              <p className="text-label text-brand mb-3">Coming soon</p>
              <h2 className="text-display text-3xl sm:text-4xl text-[var(--text-primary)]">
                We're writing the docs
              </h2>
              <p className="mt-4 text-lg text-[var(--text-secondary)]">
                Full API documentation, code examples, and integration guides are on the way.
                Sign in to get your API key and start building.
              </p>
              <div className="mt-8">
                <Link
                  to="/dashboard"
                  className={cn(buttonVariants({ variant: 'outline', size: 'default' }), 'px-6 gap-2')}
                >
                  <BookOpen className="h-4 w-4" />
                  Get API Access
                </Link>
              </div>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  )
}
