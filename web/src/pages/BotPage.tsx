import { Navbar } from '@/components/common/Navbar'
import { Footer } from '@/components/common/Footer'
import { BotHeroSection } from '@/components/bot/BotHeroSection'
import { DemoPlaceholderSection } from '@/components/bot/DemoPlaceholderSection'
import { HowItWorksSection } from '@/components/bot/HowItWorksSection'
import { CapabilitiesSection } from '@/components/bot/CapabilitiesSection'
import { PlatformsSection } from '@/components/bot/PlatformsSection'
import { CTASection } from '@/components/bot/CTASection'

export function BotPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1 pb-20 md:pb-0">
        <BotHeroSection />
        <DemoPlaceholderSection />
        <HowItWorksSection />
        <CapabilitiesSection />
        <PlatformsSection />
        <CTASection />
      </main>
      <Footer />
    </div>
  )
}
