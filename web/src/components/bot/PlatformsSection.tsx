import { MessageCircle } from 'lucide-react'

export function PlatformsSection() {
  return (
    <section className="py-20 sm:py-24">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-display text-3xl sm:text-4xl text-[var(--text-primary)]">
            No new app. No account. Just chat.
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="rounded-lg bg-[var(--bg-card)] p-8 shadow-md border border-[var(--border-subtle)] flex flex-col">
            <h3 className="text-xl font-semibold text-[var(--text-primary)] mb-3">
              Telegram
            </h3>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed flex-1 mb-6">
              Full support. Send files, links, and voice notes. Get results right in your chat.
            </p>
            <a
              href="https://t.me/getflume_bot"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center rounded-lg h-9 px-4 gap-1.5 bg-[var(--primary)] text-[var(--primary-foreground)] hover:bg-[var(--brand-hover)] transition-colors self-start"
            >
              <MessageCircle className="h-4 w-4" />
              Open on Telegram
            </a>
          </div>

          <div className="rounded-lg bg-[var(--bg-card)] p-8 shadow-md border border-[var(--border-subtle)] flex flex-col">
            <h3 className="text-xl font-semibold text-[var(--text-primary)] mb-3">
              WhatsApp
            </h3>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed flex-1 mb-6">
              Send links and voice notes. Flume handles the rest.
            </p>
            <a
              href="https://wa.me/000000000"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center rounded-lg h-9 px-4 gap-1.5 border border-[var(--border-strong)] text-[var(--text-primary)] hover:bg-[var(--bg-subtle)] transition-colors self-start"
            >
              <MessageCircle className="h-4 w-4" />
              Open on WhatsApp
            </a>
            <p className="mt-2 text-xs text-[var(--text-muted)]">
              WhatsApp support coming soon
            </p>
          </div>
        </div>
      </div>
      {/* DUMMY LINK: replace with real WhatsApp number before launch */}
    </section>
  )
}
