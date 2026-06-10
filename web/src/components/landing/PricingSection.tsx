import { Check } from 'lucide-react'
import { Link } from 'react-router-dom'
import { buttonVariants } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

const tiers = [
  {
    name: 'Free',
    price: '$0',
    priceSuffix: '',
    description: 'Get started and explore the API',
    features: ['100 jobs/month', '500MB storage', 'Community support'],
    cta: 'Get Started',
    href: '/login',
    highlighted: false,
  },
  {
    name: 'Pro',
    price: '$29',
    priceSuffix: '/mo',
    description: 'For teams shipping production apps',
    features: ['5,000 jobs/month', '50GB storage', 'Email support', 'Webhook callbacks'],
    cta: 'Start Building',
    href: '/login',
    highlighted: true,
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    priceSuffix: '',
    description: 'Large-scale workloads with SLA guarantees',
    features: ['Unlimited jobs', 'Custom storage', 'SLA guarantee', 'Dedicated support'],
    cta: 'Contact Us',
    href: '#api-access',
    highlighted: false,
  },
]

export function PricingSection() {
  return (
    <section id="pricing" className="py-20 sm:py-24">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">

        <div className="text-center mb-14">
          <p className="text-label text-brand mb-3">Pricing</p>
          <h2 className="text-display text-3xl sm:text-4xl text-[var(--text-primary)]">
            Simple, usage-based pricing
          </h2>
          <p className="mt-4 text-lg text-[var(--text-secondary)]">
            Start free. Scale as you grow.
          </p>
        </div>

        {/* [PLACEHOLDER] — update pricing and feature limits before launch */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 max-w-5xl mx-auto items-start">
          {tiers.map((tier) => (
            <div
              key={tier.name}
              className={cn(
                'relative rounded-xl bg-[var(--bg-card)] p-8 flex flex-col border transition-all duration-200',
                tier.highlighted
                  ? 'border-[var(--brand)] ring-1 ring-[var(--brand)] shadow-lg scale-[1.02]'
                  : 'border-[var(--border-subtle)] hover:border-[var(--border-strong)] hover:shadow-sm'
              )}
            >
              {tier.highlighted && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <Badge variant="default" className="px-3 py-0.5 text-xs font-semibold">
                    Recommended
                  </Badge>
                </div>
              )}

              <div className="mb-6">
                <h3 className="text-lg font-semibold text-[var(--text-primary)]">
                  {tier.name}
                </h3>
                <p className="text-sm text-[var(--text-secondary)] mt-1">
                  {tier.description}
                </p>
              </div>

              <div className="mb-6">
                <span className="text-4xl font-bold text-[var(--text-primary)]">
                  {tier.price}
                </span>
                {tier.priceSuffix && (
                  <span className="text-sm text-[var(--text-muted)] ml-1">
                    {tier.priceSuffix}
                  </span>
                )}
              </div>

              <ul className="flex-1 space-y-3 mb-8">
                {tier.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-2.5">
                    <Check className="h-4 w-4 text-brand mt-0.5 shrink-0" />
                    <span className="text-sm text-[var(--text-secondary)]">{feature}</span>
                  </li>
                ))}
              </ul>

              {tier.href.startsWith('/') ? (
                <Link
                  to={tier.href}
                  className={cn(
                    buttonVariants({
                      variant: tier.highlighted ? 'default' : 'outline',
                      size: 'default',
                    }),
                    'w-full justify-center px-4'
                  )}
                >
                  {tier.cta}
                </Link>
              ) : (
                <a
                  href={tier.href}
                  className={cn(
                    buttonVariants({
                      variant: tier.highlighted ? 'default' : 'outline',
                      size: 'default',
                    }),
                    'w-full justify-center px-4'
                  )}
                >
                  {tier.cta}
                </a>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
