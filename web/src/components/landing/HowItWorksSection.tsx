import { Badge } from '@/components/ui/badge'

const steps = [
  {
    number: '01',
    title: 'Hit the API',
    description: 'Send a link or upload a file directly. REST API, simple auth, instant job creation.',
  },
  {
    number: '02',
    title: 'We process it',
    description: 'FFmpeg handles the heavy lifting — trim, compress, convert, extract audio, whatever you need.',
  },
  {
    number: '03',
    title: 'Get your result',
    description: 'Small files returned directly. Large files served via a fast CDN link.',
  },
]

export function HowItWorksSection() {
  return (
    <section id="how-it-works" className="py-20 sm:py-24">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-display text-3xl sm:text-4xl text-[var(--text-primary)]">
            Simple by design
          </h2>
        </div>
        
        <div className="flex flex-col md:flex-row gap-8 md:gap-12">
          {steps.map((step) => (
            <div
              key={step.number}
              className="flex-1 text-center"
            >
              <Badge
                variant="secondary"
                className="mb-4 text-sm font-semibold px-3 py-1 bg-[var(--brand-light)] text-[var(--brand)]"
              >
                {step.number}
              </Badge>
              <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">
                {step.title}
              </h3>
              <p className="text-sm text-[var(--text-secondary)]">
                {step.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}