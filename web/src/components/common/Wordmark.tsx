import { cn } from '@/lib/utils'

interface WordmarkProps {
  variant?: 'light' | 'dark' | 'auto'
  className?: string
}

export function Wordmark({ variant = 'auto', className }: WordmarkProps) {
  const getTextColor = () => {
    if (variant === 'light') return '#1D9E75'
    if (variant === 'dark') return '#1D9E75'
    return 'var(--brand)'
  }

  return (
    <svg
      viewBox="0 0 76 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={cn('h-6 w-auto', className)}
    >
      <text
        x="0"
        y="20"
        fontFamily="var(--font-serif)"
        fontSize="22"
        fontStyle="italic"
        fontWeight="400"
        fill={getTextColor()}
      >
        Flume
      </text>
    </svg>
  )
}