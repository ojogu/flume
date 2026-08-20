import { ArrowRight, BookOpen, Music, Download, Maximize2, Minimize2, Scissors, Plus } from 'lucide-react'
import { Link as RouterLink } from 'react-router-dom'
import { buttonVariants } from '@/components/ui/button'
import { cn } from '@/lib/utils'

const presets = [
  {
    icon: Download,
    title: 'Download',
    description: 'Save the source file as-is, no processing',
  },
  {
    icon: Music,
    title: 'Extract Audio',
    description: 'Pull audio from any video as MP3',
  },
  {
    icon: Scissors,
    title: 'Trim',
    description: 'Cut out the part you want',
  },
  {
    icon: Maximize2,
    title: 'Resize',
    description: 'Change dimensions for any platform',
  },
  {
    icon: Minimize2,
    title: 'Compress',
    description: 'Reduce file size while keeping quality',
  },
  {
    icon: Plus,
    title: 'And more',
    description: 'Join, transcode, watermark, subtitle, mute, and more.',
  },
]

export function WebSection() {
  return (
    <section id="web" className="py-20 sm:py-24 bg-[var(--bg-subtle)]">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">

        <div className="text-center mb-14">
          <p className="text-label text-brand mb-3">For everyone</p>
          <h2 className="text-display text-3xl sm:text-4xl text-[var(--text-primary)]">
            No API key needed
          </h2>
          <p className="mt-4 text-lg text-[var(--text-secondary)]">
            Paste a video link, pick what you want done, download the result.
            Free for everyday use.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 mb-14">
          {presets.map((preset) => (
            <div
              key={preset.title}
              className="group rounded-xl bg-[var(--bg-card)] p-6 border border-[var(--border-subtle)] hover:border-[var(--border-strong)] hover:shadow-sm transition-all duration-200"
            >
              <div className="mb-4 inline-flex h-10 w-10 items-center justify-center rounded-lg bg-[var(--brand-light)]">
                <preset.icon className="h-5 w-5 text-brand" />
              </div>
              <h3 className="font-semibold text-[var(--text-primary)] mb-2">
                {preset.title}
              </h3>
              <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
                {preset.description}
              </p>
            </div>
          ))}
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
          <RouterLink
            to="/web"
            className={cn(buttonVariants({ variant: 'default', size: 'lg' }), 'px-6 gap-2')}
          >
            Get started
            <ArrowRight className="h-4 w-4" />
          </RouterLink>

          <a
            href="/docs"
            className={cn(buttonVariants({ variant: 'outline', size: 'lg' }), 'px-6 gap-2')}
          >
            <BookOpen className="h-4 w-4" />
            View docs
          </a>
        </div>

      </div>
    </section>
  )
}
