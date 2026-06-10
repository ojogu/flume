import { cn } from '@/lib/utils'
import { useTheme } from '@/hooks/useTheme'

interface WordmarkProps {
  variant?: 'light' | 'dark' | 'auto'
  className?: string
}

export function Wordmark({ variant = 'auto', className }: WordmarkProps) {
  const { resolvedTheme } = useTheme()

  const activeVariant = variant === 'auto' ? resolvedTheme : variant
  const textColor = activeVariant === 'dark' ? 'var(--brand-mid)' : 'var(--brand-hover)'

  return (
    <svg
      viewBox="0 0 124 32"
      className={cn('h-8 w-auto', className)}
      style={{ color: textColor }}
      aria-label="Flume"
      role="img"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
    >
      {/* Mark: three diagonal parallelogram stripes — top = lightest, bottom = darkest */}
      {/* Top stripe — lightest (brand-light tint) */}
      <path fill="var(--brand-light)" d="M0 11 L8 5 L26 5 L18 11 Z" />
      {/* Middle stripe — brand-mid */}
      <path fill="var(--brand-mid)" d="M0 19 L8 13 L26 13 L18 19 Z" />
      {/* Bottom stripe — brand (darkest, anchors the mark) */}
      <path fill="var(--brand)" d="M0 27 L8 21 L26 21 L18 27 Z" />

      {/* Wordmark text — Instrument Serif italic, color driven by currentColor */}
      <text
        x="34"
        y="24"
        fontFamily="Instrument Serif, serif"
        fontStyle="italic"
        fontWeight="400"
        fontSize="22"
        letterSpacing="-0.44"
        fill="currentColor"
      >
        flume
      </text>
    </svg>
  )
}
