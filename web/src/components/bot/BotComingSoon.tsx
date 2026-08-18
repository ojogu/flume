import { Mail } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { BOT_COMING_SOON_MESSAGE } from '@/lib/bot'

export function BotComingSoon() {
  return (
    <section className="relative py-20 sm:py-28 overflow-hidden">
      <div className="gradient-hero absolute inset-0 -z-10" />
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-label text-brand mb-3">Flume Bot</p>
          <h1 className="text-display text-4xl sm:text-5xl text-[var(--text-primary)] mb-4">
            Coming soon
          </h1>
          <p className="text-lg text-[var(--text-secondary)] max-w-xl mx-auto">
            {BOT_COMING_SOON_MESSAGE} Same processing power, delivered over
            messaging apps. Stay tuned.
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
