import { useState } from 'react'
import { Navbar } from '@/components/common/Navbar'
import { Footer } from '@/components/common/Footer'
import { PricingHero } from '@/components/pricing/PricingHero'
import { ComparisonTable } from '@/components/pricing/ComparisonTable'
import { PricingFAQ } from '@/components/pricing/PricingFAQ'

export function PricingPage() {
  const [billingPeriod, setBillingPeriod] = useState<'monthly' | 'annual'>('monthly')

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1">
        <PricingHero
          billingPeriod={billingPeriod}
          onBillingPeriodChange={setBillingPeriod}
        />
        <ComparisonTable billingPeriod={billingPeriod} />
        <PricingFAQ />
      </main>
      <Footer />
    </div>
  )
}
