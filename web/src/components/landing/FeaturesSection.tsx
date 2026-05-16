import { Download, Cpu, Clock, Cloud } from 'lucide-react'

const features = [
  {
    icon: Download,
    title: 'Social Video Download',
    description: 'Grab video from any major platform with a single link',
  },
  {
    icon: Cpu,
    title: 'FFmpeg Processing',
    description: 'Trim, compress, convert, and transform video with full FFmpeg power',
  },
  {
    icon: Clock,
    title: 'Async Job Queue',
    description: 'Long-running jobs run in the background. Poll or get notified when done',
  },
  {
    icon: Cloud,
    title: 'S3/R2 Storage',
    description: 'Processed files stored securely and served fast via R2 or S3',
  },
]

export function FeaturesSection() {
  return (
    <section id="features" className="py-20 sm:py-24 bg-[var(--bg-subtle)]">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-display text-3xl sm:text-4xl text-[var(--text-primary)]">
            Everything you need to process video at scale
          </h2>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="rounded-lg bg-[var(--bg-card)] p-6 shadow-md border border-[var(--border-subtle)]"
            >
              <div className="mb-4 inline-flex h-10 w-10 items-center justify-center rounded-lg bg-[var(--brand-light)]">
                <feature.icon className="h-5 w-5 text-[var(--brand)]" />
              </div>
              <h3 className="font-semibold text-[var(--text-primary)] mb-2">
                {feature.title}
              </h3>
              <p className="text-sm text-[var(--text-secondary)]">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}