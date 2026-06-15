'use client';

import { useTheme } from 'next-themes';
import { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';

interface WordmarkProps {
  variant?: 'light' | 'dark' | 'auto';
  className?: string;
}

export function Wordmark({ variant = 'auto', className }: WordmarkProps) {
  const { resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const currentVariant = variant === 'auto' ? (resolvedTheme === 'dark' ? 'dark' : 'light') : variant;

  // Render a placeholder or nothing if not mounted to avoid hydration mismatch
  if (!mounted && variant === 'auto') {
    return <div className={cn("h-8 w-32 bg-muted animate-pulse rounded", className)} />;
  }

  const textColor = currentVariant === 'dark' ? 'var(--brand-mid)' : 'var(--brand-hover)';

  return (
    <svg
      viewBox="0 0 124 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={cn("h-8 w-auto", className)}
    >
      {/* Three-stripe mark */}
      <path d="M0 24L8 8H24L16 24H0Z" fill="var(--brand-light)" />
      <path d="M4 28L12 12H28L20 28H4Z" fill="var(--brand-mid)" />
      <path d="M8 32L16 16H32L24 32H8Z" fill="var(--brand)" />

      {/* Logotype */}
      <text
        x="40"
        y="22"
        fill={textColor}
        style={{
          fontFamily: 'var(--font-serif)',
          fontStyle: 'italic',
          fontWeight: 400,
          fontSize: '22px',
          letterSpacing: '-0.44px'
        }}
      >
        flume
      </text>
    </svg>
  );
}
