import { Navbar } from '@/components/common/Navbar'
import { Footer } from '@/components/common/Footer'
import { PricingComingSoon } from '@/components/pricing/PricingComingSoon'

export function PricingBlockedPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1">
        <PricingComingSoon />
      </main>
      <Footer />
    </div>
  )
}
