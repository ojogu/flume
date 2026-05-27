import { Scissors, FileArchive, Music, Repeat, Link, Sparkles } from 'lucide-react'

const capabilities = [
  {
    icon: Scissors,
    title: 'Trim or cut a clip',
    description: 'Remove the parts you don\'t need',
  },
  {
    icon: FileArchive,
    title: 'Compress for sharing',
    description: 'Shrink the file size without killing the quality',
  },
  {
    icon: Music,
    title: 'Extract the audio',
    description: 'Pull the sound out of any video',
  },
  {
    icon: Repeat,
    title: 'Convert the format',
    description: 'Change it to MP4, MOV, or whatever you need',
  },
  {
    icon: Link,
    title: 'Download from a link',
    description: 'Paste a link from Instagram, TikTok, or YouTube and get the video',
  },
  {
    icon: Sparkles,
    title: 'More coming soon',
    description: 'New capabilities added regularly',
  },
]

export function CapabilitiesSection() {
  return (
    <section className="py-20 sm:py-24 bg-[var(--bg-subtle)]">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-display text-3xl sm:text-4xl text-[var(--text-primary)]">
            What can Flume do?
          </h2>
          <p className="mt-4 text-lg text-[var(--text-secondary)]">
            Just say it — Flume figures out the rest.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {capabilities.map((capability) => (
            <div
              key={capability.title}
              className="rounded-lg bg-[var(--bg-card)] p-6 shadow-md border border-[var(--border-subtle)]"
            >
              <div className="mb-4 inline-flex h-10 w-10 items-center justify-center rounded-lg bg-[var(--brand-light)]">
                <capability.icon className="h-5 w-5 text-[var(--brand)]" />
              </div>
              <h3 className="font-semibold text-[var(--text-primary)] mb-2">
                {capability.title}
              </h3>
              <p className="text-sm text-[var(--text-secondary)]">
                {capability.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
