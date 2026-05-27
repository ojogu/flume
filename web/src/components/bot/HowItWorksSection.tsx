import { Badge } from '@/components/ui/badge'

const steps = [
  {
    number: '01',
    title: 'Send your video',
    description: 'Drop a video file or paste a link. Works with videos from Instagram, TikTok, YouTube, and more.',
  },
  {
    number: '02',
    title: 'Say what you want',
    description: 'Tell Flume what to do in plain English. Trim it, compress it, extract the audio — just say it.',
  },
  {
    number: '03',
    title: 'Get it back',
    description: 'Your video comes back ready to save and share. No waiting around, no complicated exports.',
  },
]

export function HowItWorksSection() {
  return (
    <section className="py-20 sm:py-24">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-display text-3xl sm:text-4xl text-[var(--text-primary)]">
            Three steps. That's it.
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
