import { MessageCircle } from 'lucide-react'

export function BotHeroSection() {
  return (
    <section className="relative overflow-hidden py-20 sm:py-28 lg:py-32">
      <div
        className="absolute inset-0 -z-10"
        style={{
          background: 'radial-gradient(circle at 50% 0%, var(--brand-light) 0%, transparent 60%)'
        }}
      />

      <div className="mx-auto max-w-4xl px-4 text-center sm:px-6 lg:px-8">
        <h1 className="text-display text-4xl sm:text-5xl lg:text-6xl text-[var(--text-primary)]">
          Edit video without the app.
        </h1>

        <p className="mt-6 text-lg text-[var(--text-secondary)] max-w-2xl mx-auto">
          Send a video. Say what you want. Get it back in seconds. Works on Telegram and WhatsApp.
        </p>

        <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
          <a
            href="https://t.me/getflume_bot"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center rounded-lg h-9 px-4 gap-1.5 bg-[var(--primary)] text-[var(--primary-foreground)] hover:bg-[var(--brand-hover)] transition-colors"
          >
            <MessageCircle className="h-4 w-4" />
            Open on Telegram
          </a>

          <a
            href="https://wa.me/000000000"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center rounded-lg h-9 px-4 gap-1.5 border border-[var(--border-strong)] text-[var(--text-primary)] hover:bg-[var(--bg-subtle)] transition-colors"
          >
            <MessageCircle className="h-4 w-4" />
            Open on WhatsApp
          </a>
        </div>
      </div>
      {/* DUMMY LINK: replace with real WhatsApp number before launch */}
    </section>
  )
}
