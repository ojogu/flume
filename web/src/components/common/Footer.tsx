import { Link } from 'react-router-dom'
import { Wordmark } from './Wordmark'

const footerLinks = [
  { href: '/api', label: 'API' },
  { href: '/bot', label: 'Bot' },
  { href: '#pricing', label: 'Pricing' },
  { href: '#docs', label: 'Docs' },
  { href: '#github', label: 'GitHub' },
  { href: 'https://t.me/getflume_bot', label: 'Telegram' },
  { href: 'https://wa.me/000000000', label: 'WhatsApp' }, // DUMMY LINK: replace with real WhatsApp number before launch
]

export function Footer() {
  return (
    <footer className="border-t border-[var(--border-subtle)] bg-[var(--bg)]">
      <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center gap-6">
          <Link to="/">
            <Wordmark />
          </Link>
          
          <p className="text-sm text-[var(--text-muted)] text-center">
            Video processing for developers and everyone else.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-6">
            {footerLinks.map((link) => (
              <a
                key={link.href + link.label}
                href={link.href}
                className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
              >
                {link.label}
              </a>
            ))}
          </div>

          <p className="text-xs text-[var(--text-muted)]">
            © 2026 Flume. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  )
}