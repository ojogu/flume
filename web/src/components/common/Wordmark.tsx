import { cn } from '@/lib/utils'
import logoLight from '@/assets/flume_logo_light.png'
import logoDark from '@/assets/flume_logo_dark.png'
import { useTheme } from '@/hooks/useTheme'

interface WordmarkProps {
  variant?: 'light' | 'dark' | 'auto'
  className?: string
}

export function Wordmark({ variant = 'auto', className }: WordmarkProps) {
  const { resolvedTheme } = useTheme()

  const activeVariant = variant === 'auto' ? resolvedTheme : variant

  return (
    <img
      src={activeVariant === 'dark' ? logoLight : logoDark}
      alt="Flume"
      className={cn('h-8 w-auto', className)}
    />
  )
}
