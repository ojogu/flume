import { Link } from 'react-router-dom'
import { Wordmark } from './Wordmark'

const productLinks = [
  { href: '/api', label: 'FlumeAPI', internal: true },
  { href: '/bot', label: 'Flume Bot', internal: true },
  { href: '/pricing', label: 'Pricing', internal: true },
]

const resourceLinks = [
  { href: '/docs', label: 'Docs', internal: false },
  { href: '#github', label: 'GitHub', internal: false },
]

const communityLinks = [
  { href: 'https://t.me/getflume_bot', label: 'Telegram', internal: false, external: true },
  { href: 'https://wa.me/000000000', label: 'WhatsApp', internal: false, external: true }, // DUMMY LINK: replace with real WhatsApp number before launch
]

function FooterLink({ href, label, internal, external }: { href: string; label: string; internal?: boolean; external?: boolean }) {
  const className = "text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
  if (internal) {
    return <Link to={href} className={className}>{label}</Link>
  }
  return (
    <a
      href={href}
      className={className}
      {...(external ? { target: '_blank', rel: 'noopener noreferrer' } : {})}
    >
      {label}
    </a>
  )
}

export function Footer() {
  return (
    <footer className="border-t border-[var(--border-subtle)] bg-[var(--bg)]">
      <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6 lg:px-8">

        {/* Main footer grid */}
        <div className="grid grid-cols-2 gap-8 sm:grid-cols-4 mb-10">
          {/* Brand column */}
          <div className="col-span-2 sm:col-span-1">
            <Link to="/" className="inline-block mb-3">
              <Wordmark />
            </Link>
            <p className="text-sm text-[var(--text-muted)] leading-relaxed max-w-[180px]">
              Media processing for developers and everyone else.
            </p>
          </div>

          {/* Product */}
          <div>
            <p className="text-label text-[var(--text-muted)] mb-3">Product</p>
            <ul className="flex flex-col gap-2.5">
              {productLinks.map((link) => (
                <li key={link.href + link.label}>
                  <FooterLink {...link} />
                </li>
              ))}
            </ul>
          </div>

          {/* Resources */}
          <div>
            <p className="text-label text-[var(--text-muted)] mb-3">Resources</p>
            <ul className="flex flex-col gap-2.5">
              {resourceLinks.map((link) => (
                <li key={link.href + link.label}>
                  <FooterLink {...link} />
                </li>
              ))}
            </ul>
          </div>

          {/* Community */}
          <div>
            <p className="text-label text-[var(--text-muted)] mb-3">Community</p>
            <ul className="flex flex-col gap-2.5">
              {communityLinks.map((link) => (
                <li key={link.href + link.label}>
                  <FooterLink {...link} external />
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="border-t border-[var(--border-subtle)] pt-6 flex flex-col sm:flex-row items-center justify-between gap-3">
          <p className="text-xs text-[var(--text-muted)]">
            © 2026 Flume. All rights reserved.
          </p>
          <p className="text-xs text-[var(--text-muted)]">
            Built for developers who ship fast.
          </p>
        </div>
      </div>
    </footer>
  )
}
