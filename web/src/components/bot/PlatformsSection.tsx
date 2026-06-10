import { buttonVariants } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

function TelegramIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" className={className} aria-hidden="true">
      <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z" />
    </svg>
  )
}

function WhatsAppIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" className={className} aria-hidden="true">
      <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413Z" />
    </svg>
  )
}

export function PlatformsSection() {
  return (
    <section className="py-20 sm:py-24">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">

        <div className="text-center mb-14">
          <p className="text-label text-brand mb-3">Available on</p>
          <h2 className="text-display text-3xl sm:text-4xl text-[var(--text-primary)]">
            No new app. No account. Just chat.
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {/* Telegram — fully available */}
          <div className="rounded-xl bg-[var(--bg-card)] border border-[var(--border-subtle)] hover:border-[var(--border-strong)] hover:shadow-sm transition-all duration-200 overflow-hidden flex flex-col">
            {/* Colored top accent */}
            <div className="h-1 w-full bg-[#229ED9]" />
            <div className="p-8 flex flex-col flex-1">
              <div className="flex items-center gap-3 mb-4">
                <div className="h-10 w-10 rounded-lg flex items-center justify-center bg-[#229ED9]/10 shrink-0">
                  <TelegramIcon className="h-5 w-5 text-[#229ED9]" />
                </div>
                <h3 className="text-xl font-semibold text-[var(--text-primary)]">Telegram</h3>
              </div>
              <p className="text-sm text-[var(--text-secondary)] leading-relaxed flex-1 mb-6">
                Full support. Send files, links, and voice notes. Get results right in your chat.
              </p>
              <a
                href="https://t.me/getflume_bot"
                target="_blank"
                rel="noopener noreferrer"
                className={cn(
                  buttonVariants({ variant: 'default', size: 'sm' }),
                  'self-start gap-1.5 px-4'
                )}
              >
                <TelegramIcon className="h-3.5 w-3.5" />
                Open on Telegram
              </a>
            </div>
          </div>

          {/* WhatsApp — coming soon */}
          <div className="rounded-xl bg-[var(--bg-card)] border border-[var(--border-subtle)] transition-all duration-200 overflow-hidden flex flex-col opacity-75">
            {/* Colored top accent */}
            <div className="h-1 w-full bg-[#25D366]" />
            <div className="p-8 flex flex-col flex-1">
              <div className="flex items-center gap-3 mb-4">
                <div className="h-10 w-10 rounded-lg flex items-center justify-center bg-[#25D366]/10 shrink-0">
                  <WhatsAppIcon className="h-5 w-5 text-[#25D366]" />
                </div>
                <div className="flex items-center gap-2.5">
                  <h3 className="text-xl font-semibold text-[var(--text-primary)]">WhatsApp</h3>
                  <Badge variant="secondary" className="text-[10px] px-2">Coming soon</Badge>
                </div>
              </div>
              <p className="text-sm text-[var(--text-secondary)] leading-relaxed flex-1 mb-6">
                Send links and voice notes. Flume handles the rest. WhatsApp support is on the way.
              </p>
              <a
                href="https://wa.me/000000000"
                target="_blank"
                rel="noopener noreferrer"
                className={cn(
                  buttonVariants({ variant: 'outline', size: 'sm' }),
                  'self-start gap-1.5 px-4 pointer-events-none opacity-50'
                )}
                aria-disabled="true"
                tabIndex={-1}
              >
                <WhatsAppIcon className="h-3.5 w-3.5" />
                Open on WhatsApp
              </a>
            </div>
          </div>
        </div>
        {/* DUMMY LINK: replace with real WhatsApp number before launch */}
      </div>
    </section>
  )
}
