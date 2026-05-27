export function PricingSection() {
  const tiers = [
    {
      name: 'Free',
      price: '$0',
      priceSuffix: '',
      features: ['100 jobs/month', '500MB storage', 'Community support'],
      cta: 'Get Started',
      href: '#api-access',
    },
    {
      name: 'Pro',
      price: '$29',
      priceSuffix: '/mo',
      features: ['5,000 jobs/month', '50GB storage', 'Email support', 'Webhook callbacks'],
      cta: 'Start Building',
      href: '#api-access',
    },
    {
      name: 'Enterprise',
      price: 'Custom',
      priceSuffix: '',
      features: ['Unlimited jobs', 'Custom storage', 'SLA', 'Dedicated support'],
      cta: 'Contact Us',
      href: '#api-access',
    },
  ]

  return (
    <section id="pricing" className="py-20 sm:py-24">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-display text-3xl sm:text-4xl text-[var(--text-primary)]">
            Simple, usage-based pricing
          </h2>
          <p className="mt-4 text-lg text-[var(--text-secondary)]">
            Start free. Scale as you grow.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {tiers.map((tier) => (
            <div
              key={tier.name}
              className="rounded-lg bg-[var(--bg-card)] p-8 shadow-md border border-[var(--border-subtle)] flex flex-col"
            >
              <h3 className="text-xl font-semibold text-[var(--text-primary)]">
                {tier.name}
              </h3>

              <div className="mt-4">
                <span className="text-4xl font-bold text-[var(--text-primary)]">
                  {tier.price}
                </span>
                {tier.priceSuffix && (
                  <span className="text-sm text-[var(--text-muted)] ml-1">
                    {tier.priceSuffix}
                  </span>
                )}
              </div>

              {/* [PLACEHOLDER] — update pricing and feature limits before launch */}
              <ul className="mt-6 flex-1 space-y-2">
                {tier.features.map((feature) => (
                  <li
                    key={feature}
                    className="text-sm text-[var(--text-secondary)]"
                  >
                    {feature}
                  </li>
                ))}
              </ul>

              <a
                href={tier.href}
                className="mt-8 inline-flex items-center justify-center rounded-lg h-9 px-4 text-sm font-medium bg-[var(--primary)] text-[var(--primary-foreground)] hover:bg-[var(--brand-hover)] transition-colors"
              >
                {tier.cta}
              </a>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
