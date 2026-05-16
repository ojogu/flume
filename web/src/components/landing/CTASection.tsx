import { ArrowRight, MessageCircle } from 'lucide-react'

export function CTASection() {
  return (
    <section id="api-access" className="relative py-20 sm:py-24">
      <div 
        className="absolute inset-0 -z-10"
        style={{
          background: 'radial-gradient(circle at 50% 100%, var(--brand-light) 0%, transparent 60%)'
        }}
      />
      
      <div className="mx-auto max-w-3xl px-4 text-center sm:px-6 lg:px-8">
        <h2 className="text-display text-3xl sm:text-4xl text-[var(--text-primary)]">
          Start building today
        </h2>
        
        <p className="mt-4 text-lg text-[var(--text-secondary)]">
          API access for developers. Chat interface for everyone.
        </p>
        
        <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
          <a
            href="#docs"
            className="inline-flex items-center justify-center rounded-lg h-9 px-4 gap-1.5 bg-[var(--primary)] text-[var(--primary-foreground)] hover:bg-[var(--brand-hover)] transition-colors"
          >
            Get API Access
            <ArrowRight className="h-4 w-4" />
          </a>
          
          <a
            href="https://t.me/flumebot"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center rounded-lg h-9 px-4 gap-1.5 border border-[var(--border-strong)] text-[var(--text-primary)] hover:bg-[var(--bg-subtle)] transition-colors"
          >
            <MessageCircle className="h-4 w-4" />
            Try on Telegram
          </a>
        </div>
      </div>
    </section>
  )
}