import { Navbar } from '@/components/common/Navbar'
import { Footer } from '@/components/common/Footer'
import { HeroSection } from '@/components/landing/HeroSection'
import { FeaturesSection } from '@/components/landing/FeaturesSection'
import { HowItWorksSection } from '@/components/landing/HowItWorksSection'
import { WebSection } from '@/components/landing/WebSection'
import { PricingSection } from '@/components/landing/PricingSection'
import { ThreeSurfacesSection } from '@/components/landing/ThreeSurfacesSection'
import { CTASection } from '@/components/landing/CTASection'

export function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1">
        <HeroSection />
        <FeaturesSection />
        <HowItWorksSection />
        <WebSection />
        <PricingSection />
        <ThreeSurfacesSection />
        <CTASection />
      </main>
      <Footer />
    </div>
  )
}