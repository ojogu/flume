import { MessageCircle } from 'lucide-react'

export function CTASection() {
  return (
    <section className="relative py-20 sm:py-24">
      <div
        className="absolute inset-0 -z-10"
        style={{
          background: 'radial-gradient(circle at 50% 100%, var(--brand-light) 0%, transparent 60%)'
        }}
      />

      <div className="mx-auto max-w-3xl px-4 text-center sm:px-6 lg:px-8">
        <h2 className="text-display text-3xl sm:text-4xl text-[var(--text-primary)]">
          Ready? Send your first video.
        </h2>

        <p className="mt-4 text-lg text-[var(--text-secondary)]">
          No sign-up. No install. Just open a chat and go.
        </p>

        <div className="mt-10 hidden sm:flex flex-col sm:flex-row items-center justify-center gap-4">
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

      {/* Sticky CTA bar — mobile only */}
      <div className="fixed bottom-0 left-0 right-0 z-50 border-t border-[var(--border-subtle)] bg-[var(--bg)]/95 backdrop-blur-md md:hidden">
        <div className="flex items-center gap-3 px-4 py-3">
          <a
            href="https://t.me/getflume_bot"
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 inline-flex items-center justify-center rounded-lg h-9 px-4 gap-1.5 bg-[var(--primary)] text-[var(--primary-foreground)] hover:bg-[var(--brand-hover)] transition-colors text-sm font-medium"
          >
            <MessageCircle className="h-4 w-4" />
            Open on Telegram
          </a>

          <a
            href="https://wa.me/000000000"
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 inline-flex items-center justify-center rounded-lg h-9 px-4 gap-1.5 border border-[var(--border-strong)] text-[var(--text-primary)] hover:bg-[var(--bg-subtle)] transition-colors text-sm font-medium"
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
