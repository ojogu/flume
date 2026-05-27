import { Check } from 'lucide-react'
import { buttonVariants } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

// [PLACEHOLDER] — update prices, features, and CTAs before launch
const tiers = [
  {
    name: 'Free',
    monthly: { price: '$0', suffix: '' },
    annual: { price: '$0', suffix: '' },
    annualSub: null as string | null,
    description: 'Get started and explore the API',
    features: ['100 jobs / month', '500 MB storage', 'API access', 'Community support'],
    cta: 'Get Started',
    href: '#api-access',
    highlighted: false,
  },
  {
    name: 'Pro',
    monthly: { price: '$29', suffix: '/mo' },
    annual: { price: '$23', suffix: '/mo' },
    annualSub: 'billed $276 / yr',
    description: 'For teams shipping production apps',
    features: [
      '5,000 jobs / month',
      '50 GB storage',
      'API access',
      'Webhook callbacks',
      'Email support',
    ],
    cta: 'Start Building',
    href: '#api-access',
    highlighted: true,
  },
  {
    name: 'Enterprise',
    monthly: { price: 'Custom', suffix: '' },
    annual: { price: 'Custom', suffix: '' },
    annualSub: null as string | null,
    description: 'Large-scale workloads with SLA guarantees',
    features: ['Unlimited jobs', 'Custom storage', 'SLA guarantee', 'Dedicated support'],
    cta: 'Contact Us',
    href: 'mailto:hello@flume.dev',
    highlighted: false,
  },
]

interface PricingHeroProps {
  billingPeriod: 'monthly' | 'annual'
  onBillingPeriodChange: (period: 'monthly' | 'annual') => void
}

export function PricingHero({ billingPeriod, onBillingPeriodChange }: PricingHeroProps) {
  return (
    <section className="relative py-20 sm:py-28 overflow-hidden">
      <div className="gradient-hero absolute inset-0 -z-10" />
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">

        {/* Section header */}
        <div className="text-center mb-12">
          <p className="text-label text-brand mb-3">Pricing</p>
          <h1 className="text-display text-4xl sm:text-5xl text-[var(--text-primary)] mb-4">
            Simple, usage-based pricing
          </h1>
          <p className="text-lg text-[var(--text-secondary)] max-w-xl mx-auto">
            Start free. Scale as you grow. No surprises.
          </p>
        </div>

        {/* Billing toggle */}
        <div className="flex items-center justify-center mb-12">
          <div className="inline-flex items-center rounded-full bg-[var(--bg-subtle)] p-1 border border-[var(--border-subtle)]">
            <button
              onClick={() => onBillingPeriodChange('monthly')}
              aria-pressed={billingPeriod === 'monthly'}
              className={cn(
                'px-5 py-1.5 rounded-full text-sm font-medium transition-all duration-200',
                billingPeriod === 'monthly'
                  ? 'bg-[var(--bg-card)] text-[var(--text-primary)] shadow-sm'
                  : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
              )}
            >
              Monthly
            </button>
            <button
              onClick={() => onBillingPeriodChange('annual')}
              aria-pressed={billingPeriod === 'annual'}
              className={cn(
                'flex items-center gap-2 px-5 py-1.5 rounded-full text-sm font-medium transition-all duration-200',
                billingPeriod === 'annual'
                  ? 'bg-[var(--bg-card)] text-[var(--text-primary)] shadow-sm'
                  : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
              )}
            >
              Annual
              <Badge variant="default" className="text-[10px] px-1.5 py-0 leading-4">
                Save 20%
              </Badge>
            </button>
          </div>
        </div>

        {/* Tier cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 max-w-5xl mx-auto items-start">
          {tiers.map((tier) => {
            const pricing = tier[billingPeriod]
            return (
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
                  <h3 className="text-lg font-semibold text-[var(--text-primary)]">{tier.name}</h3>
                  <p className="text-sm text-[var(--text-secondary)] mt-1">{tier.description}</p>
                </div>

                <div className="mb-1">
                  <span className="text-4xl font-bold text-[var(--text-primary)]">
                    {pricing.price}
                  </span>
                  {pricing.suffix && (
                    <span className="text-sm text-[var(--text-muted)] ml-1">{pricing.suffix}</span>
                  )}
                </div>
                <div className="h-5 mb-5">
                  {billingPeriod === 'annual' && tier.annualSub && (
                    <p className="text-xs text-[var(--text-muted)]">{tier.annualSub}</p>
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
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
