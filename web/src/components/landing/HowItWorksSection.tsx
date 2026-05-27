import React from 'react'

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

        <div className="text-center mb-14">
          <p className="text-label text-brand mb-3">How it works</p>
          <h2 className="text-display text-3xl sm:text-4xl text-[var(--text-primary)]">
            Simple by design
          </h2>
        </div>

        <div className="flex flex-col md:flex-row items-start gap-8 md:gap-0">
          {steps.map((step, index) => (
            <React.Fragment key={step.number}>
              <div className="flex-1 flex flex-col items-center text-center px-4 md:px-6">
                {/* Step circle */}
                <div className="h-12 w-12 rounded-full bg-[var(--brand-light)] border-2 border-[var(--brand-mid)] flex items-center justify-center mb-5 shrink-0">
                  <span className="text-sm font-bold text-brand">{step.number}</span>
                </div>
                <h3 className="text-base font-semibold text-[var(--text-primary)] mb-2">
                  {step.title}
                </h3>
                <p className="text-sm text-[var(--text-secondary)] leading-relaxed max-w-[220px]">
                  {step.description}
                </p>
              </div>

              {/* Connector between steps — desktop only */}
              {index < steps.length - 1 && (
                <div className="hidden md:block shrink-0 w-12 lg:w-16 pt-6">
                  <div className="border-t-2 border-dashed border-[var(--brand-mid)] w-full" />
                </div>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>
    </section>
  )
}
