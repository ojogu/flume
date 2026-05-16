import { ArrowRight, MessageCircle } from 'lucide-react'

export function HeroSection() {
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
          Process any video. Send a link, get a result.
        </h1>
        
        <p className="mt-6 text-lg text-[var(--text-secondary)] max-w-2xl mx-auto">
          FlumeAPI gives developers a powerful video processing API. 
          Flume brings it to Telegram and WhatsApp — no app install required.
        </p>
        
        <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
          <a
            href="#api-access"
            className="inline-flex items-center justify-center rounded-lg h-9 px-4 gap-1.5 bg-[var(--primary)] text-[var(--primary-foreground)] hover:bg-[var(--brand-hover)] transition-colors"
          >
            Start Building
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