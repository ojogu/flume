export function TwoSurfacesSection() {
  return (
    <section id="surfaces" className="py-20 sm:py-24 bg-[var(--bg-subtle)]">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-display text-3xl sm:text-4xl text-[var(--text-primary)]">
            Two surfaces. One infrastructure.
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="rounded-lg bg-[var(--bg-card)] p-8 shadow-md border border-[var(--border-subtle)]">
            <h3 className="text-xl font-semibold text-[var(--text-primary)] mb-3">
              FlumeAPI <span className="text-[var(--text-muted)]">/api</span>
            </h3>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              For developers. Full programmatic access, async jobs, webhook callbacks, and storage built in.
            </p>
          </div>

          <div className="rounded-lg bg-[var(--bg-card)] p-8 shadow-md border border-[var(--border-subtle)]">
            <h3 className="text-xl font-semibold text-[var(--text-primary)] mb-3">
              Flume Bot <span className="text-[var(--text-muted)]">/bot</span>
            </h3>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
              For everyone else. Same processing power, delivered over Telegram and WhatsApp. No install required.
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
