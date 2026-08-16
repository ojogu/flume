import { Mail } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { PRICING_COMING_SOON_MESSAGE } from '@/lib/pricing'

export function PricingComingSoon() {
  return (
    <section className="relative py-20 sm:py-28 overflow-hidden">
      <div className="gradient-hero absolute inset-0 -z-10" />
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-label text-brand mb-3">Pricing</p>
          <h1 className="text-display text-4xl sm:text-5xl text-[var(--text-primary)] mb-4">
            Pricing is coming soon
          </h1>
          <p className="text-lg text-[var(--text-secondary)] max-w-xl mx-auto">
            {PRICING_COMING_SOON_MESSAGE} We're still working out plans and
            feature limits — check back soon.
          </p>
          <div className="mt-8">
            <a href="mailto:support@ojogulabs.xyz">
              <Button variant="outline" size="lg" className="gap-2">
                <Mail className="h-4 w-4" />
                Contact us
              </Button>
            </a>
          </div>
        </div>
      </div>
    </section>
  )
}
