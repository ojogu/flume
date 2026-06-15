import { Code2, Bot, ArrowRight } from 'lucide-react'
import { buttonVariants } from '@/components/ui/button'
import { cn } from '@/lib/utils'

const surfaces = [
  {
    icon: Code2,
    label: '/api',
    title: 'FlumeAPI',
    description: 'For developers. Full programmatic access, async jobs, webhook callbacks, and storage built in.',
    cta: 'View API Docs',
    href: '/docs',
    variant: 'default' as const,
  },
  {
    icon: Bot,
    label: '/bot',
    title: 'Flume Bot',
    description: 'For everyone else. Same processing power, delivered over Telegram and WhatsApp. No install required.',
    cta: 'Try the Bot',
    href: '/bot',
    variant: 'outline' as const,
  },
]

export function TwoSurfacesSection() {
  return (
    <section id="surfaces" className="py-20 sm:py-24 bg-[var(--bg-subtle)]">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">

        <div className="text-center mb-14">
          <p className="text-label text-brand mb-3">Two surfaces</p>
          <h2 className="text-display text-3xl sm:text-4xl text-[var(--text-primary)]">
            One infrastructure. Two ways to use it.
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {surfaces.map((surface) => (
            <div
              key={surface.title}
              className="group rounded-xl bg-[var(--bg-card)] p-8 border border-[var(--border-subtle)] hover:border-[var(--border-strong)] hover:shadow-sm transition-all duration-200 flex flex-col"
            >
              <div className="mb-5 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-[var(--brand-light)]">
                <surface.icon className="h-6 w-6 text-brand" />
              </div>

              <div className="flex items-baseline gap-2 mb-2">
                <h3 className="text-xl font-semibold text-[var(--text-primary)]">
                  {surface.title}
                </h3>
                <span className="text-sm text-[var(--text-muted)] font-mono">{surface.label}</span>
              </div>

              <p className="text-sm text-[var(--text-secondary)] leading-relaxed flex-1 mb-6">
                {surface.description}
              </p>

              <a
                href={surface.href}
                className={cn(
                  buttonVariants({ variant: surface.variant, size: 'sm' }),
                  'self-start gap-1.5 px-4'
                )}
              >
                {surface.cta}
                <ArrowRight className="h-3.5 w-3.5" />
              </a>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
