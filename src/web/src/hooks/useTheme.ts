import { useState, useEffect } from 'react'

type Theme = 'light' | 'dark' | 'system'

export function useTheme() {
  const [theme, setTheme] = useState<Theme>(() => {
    const stored = localStorage.getItem('flume-theme')
    return (stored as Theme) || 'system'
  })

  const [resolvedTheme, setResolvedTheme] = useState<'light' | 'dark'>('light')

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    
    const resolveTheme = () => {
      if (theme === 'system') {
        return mediaQuery.matches ? 'dark' : 'light'
      }
      return theme
    }
    
    const resolved = resolveTheme()
    setResolvedTheme(resolved)
    
    document.documentElement.classList.toggle('dark', resolved === 'dark')
    document.documentElement.setAttribute('data-theme', resolved)
  }, [theme])

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const handleChange = () => {
      if (theme === 'system') {
        const resolved = mediaQuery.matches ? 'dark' : 'light'
        setResolvedTheme(resolved)
        document.documentElement.classList.toggle('dark', resolved === 'dark')
        document.documentElement.setAttribute('data-theme', resolved)
      }
    }
    
    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [theme])

  const toggleTheme = () => {
    const newTheme = resolvedTheme === 'light' ? 'dark' : 'light'
    setTheme(newTheme)
    localStorage.setItem('flume-theme', newTheme)
  }

  return { theme, resolvedTheme, toggleTheme, setTheme }
}