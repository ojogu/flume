import { Navbar } from '@/components/common/Navbar'
import { Footer } from '@/components/common/Footer'
import { BotComingSoon } from '@/components/bot/BotComingSoon'

export function BotBlockedPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1">
        <BotComingSoon />
      </main>
      <Footer />
    </div>
  )
}
