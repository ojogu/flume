import { Link } from 'react-router-dom'
import { Wordmark } from './Wordmark'

const footerLinks = [
  { href: '#docs', label: 'Docs' },
  { href: '#api', label: 'API' },
  { href: 'https://t.me/flumebot', label: 'Telegram' },
  { href: 'https://wa.me/flume', label: 'WhatsApp' },
  { href: '#github', label: 'GitHub' },
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
            Video processing for developers and everyone else
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
            © {new Date().getFullYear()} Flume. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  )
}